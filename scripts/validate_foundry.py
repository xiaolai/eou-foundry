#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from _common import find_repo_root, load_yaml

VALID_FUNCTIONS = {"generate", "specify", "validate", "diagnose", "promote", "refactor", "audit", "propose", "activate", "implement", "retire"}
VALID_AUTOMATION = {"deterministic", "LLM_assisted", "human_executed", "hybrid"}
VALID_AUTHORITY = {"suggest_only", "draft_only", "write_candidate", "write_inactive", "mutate_active", "approve", "publish"}
VALID_RISK = {"low", "medium", "high", "critical"}
VALID_STAGE = {"candidate", "draft", "simulated", "pilot", "active", "monitored", "stable", "deprecated", "retired"}
SAFE_GENERATING_AUTHORITY = {"suggest_only", "draft_only", "write_candidate", "write_inactive"}
ACTIVE_STAGES = {"active", "monitored", "stable"}
REQUIRED_TOP = [
    "id", "name", "version", "classification", "purpose", "operating_hypothesis",
    "inputs", "context_manifest", "execution", "outputs", "success_criteria",
    "validation", "failure_modes", "escalation", "responsibility", "blast_radius", "versioning",
]
REQUIRED_NESTED = {
    "classification": ["function", "target_object", "automation_mode", "authority_level", "risk_level", "lifecycle_stage"],
    "purpose": ["statement", "non_goals"],
    "inputs": ["required", "optional", "forbidden_assumptions"],
    "context_manifest": ["source_of_truth", "supporting", "forbidden"],
    "execution": ["steps", "decision_points", "stop_conditions", "allowed_tools", "prohibited_actions"],
    "outputs": ["primary", "secondary", "trace"],
    "success_criteria": ["must_pass", "should_pass"],
    "validation": ["deterministic", "judgment", "red_team"],
    "failure_modes": ["known", "warning_signs", "repair_actions"],
    "escalation": ["require_human_when", "require_approval_for"],
    "responsibility": ["executor", "reviewer", "approver", "cannot_delegate"],
    "versioning": ["supersedes", "changelog"],
}
GENERATING_REQUIRED = [
    "generation_envelope", "generation_budget", "registry_diff", "minimality_test",
    "operational_value_test", "counter_generation",
]
GENERATION_ENVELOPE_REQUIRED = [
    "allowed_outputs", "forbidden_outputs", "max_candidates", "default_status", "required_for_each_candidate"
]
CONSTITUTION_REQUIRED = ["purpose", "optimize_for", "do_not_optimize_for_alone", "invariants", "forbidden", "generation_invariants", "change_rules"]
REGISTRY_REQUIRED = ["registry_version", "entries"]
REG_ENTRY_REQUIRED = ["eou_id", "current_version", "path", "status", "maturity", "owner", "classification", "dependencies", "last_audit", "known_issues"]
INCIDENT_REQUIRED = ["id", "date", "affected_eou", "failure_class", "summary", "impact", "root_causes", "corrective_actions", "status"]

ENGINE_FILES = [
    "failure-taxonomy.yml",
    "maturity-model.yml",
    "refactoring-patterns.yml",
    "runtime-contract.yml",
    "governance.yml",
]

# Engine artifact structural shape: top-level key each file must contain.
ENGINE_TOPLEVEL = {
    "failure-taxonomy.yml": "failure_taxonomy",
    "maturity-model.yml": "maturity_levels",
    "refactoring-patterns.yml": "patterns",
    "runtime-contract.yml": None,        # contract terms vary; just YAML-mapping check
    "governance.yml": "separation_of_powers",
    "constitution-defaults.yml": "invariants",
}

# Role labels that should never appear as a constitutional or active-EOU
# approver. A role label is a job description, not a named human identity.
ROLE_LABELS = {
    "human owner", "owner", "human", "team", "any human", "designated human",
    "human reviewer", "reviewer", "approver", "maintainer", "foundry maintainer",
    "human owner / foundry maintainer", "designated approver",
}

# Substrings that strongly indicate an identity is unset or a TODO marker.
TODO_PATTERNS = re.compile(r"^\s*(todo|tbd|fixme|xxx)\b", re.IGNORECASE)


def find_plugin_root() -> Path:
    """Resolve the installed plugin root, in priority order:

    1. EOU_FOUNDRY_PLUGIN_PATH environment variable (offline testing,
       development checkouts).
    2. `claude plugin path eou-foundry@xiaolai` if the claude CLI is on
       PATH (production install via Claude Code).
    3. Path(__file__).parents[1] (fallback when this script is invoked
       directly inside a plugin checkout — e.g., plugin self-test).

    Steps 1 and 2 deliberately precede step 3 so that a workshop running
    against an installed plugin gets the installed path, not whatever
    checkout the script happens to live in. Hardcoded user-specific
    fallback paths are intentionally absent: an unconfigured environment
    should fail with a setup error, not silently pick up a path that
    only exists on the maintainer's machine.
    """
    env = os.environ.get("EOU_FOUNDRY_PLUGIN_PATH")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / ".claude-plugin" / "plugin.json").exists():
            return p

    if shutil.which("claude"):
        try:
            result = subprocess.run(
                ["claude", "plugin", "path", "eou-foundry@xiaolai"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                path_str = result.stdout.strip()
                if path_str:
                    p = Path(path_str).expanduser().resolve()
                    if (p / ".claude-plugin" / "plugin.json").exists():
                        return p
        except (subprocess.TimeoutExpired, OSError):
            pass

    # Last-resort fallback: the directory two levels up from this script.
    # Only useful when validate_foundry.py is invoked from within a plugin
    # checkout (plugin self-test, or workshop with the checkout symlinked).
    fallback = Path(__file__).resolve().parents[1]
    if (fallback / ".claude-plugin" / "plugin.json").exists():
        return fallback

    raise RuntimeError(
        "Plugin root not found. Set EOU_FOUNDRY_PLUGIN_PATH, install via "
        "`claude plugin install eou-foundry@xiaolai`, or invoke this "
        "script from inside a plugin checkout."
    )


# Version-spec syntax supported in `inherits_from: "<name>@<spec>"`.
#   ==X.Y.Z   exact
#   >=X.Y.Z   minimum
#   ~=X.Y     compatible release: same major.minor; any patch
#   X.Y.Z     equivalent to ==X.Y.Z
INHERITS_FROM_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9_.-]+)@(?P<op>==|>=|~=)?(?P<version>\d+\.\d+(?:\.\d+)?)\s*$"
)


def _parse_version(s: str) -> tuple[int, int, int]:
    parts = s.split(".")
    while len(parts) < 3:
        parts.append("0")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def parse_inherits_from(value: str) -> tuple[str, str, tuple[int, int, int]] | None:
    """Parse `name@op?version`. Returns (name, op, version_tuple) or None
    if the string doesn't match."""
    m = INHERITS_FROM_RE.match(value or "")
    if not m:
        return None
    op = m.group("op") or "=="
    return (m.group("name"), op, _parse_version(m.group("version")))


def version_satisfies(installed: tuple[int, int, int],
                      op: str, declared: tuple[int, int, int]) -> bool:
    if op == "==":
        return installed == declared
    if op == ">=":
        return installed >= declared
    if op == "~=":
        # Compatible release: same major.minor, installed >= declared.
        return (installed[0] == declared[0]
                and installed[1] == declared[1]
                and installed >= declared)
    return False


def read_plugin_version(plugin_root: Path) -> str | None:
    pj = plugin_root / ".claude-plugin" / "plugin.json"
    if not pj.exists():
        return None
    try:
        data = json.loads(pj.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    v = data.get("version")
    return v if isinstance(v, str) else None


def empty(v) -> bool:
    return v in (None, "", {})


def is_todo(value) -> bool:
    if not isinstance(value, str):
        return True
    return bool(TODO_PATTERNS.match(value))


def is_role_label(value) -> bool:
    """Heuristic: True if `value` looks like a role label rather than a
    named human identity."""
    if not isinstance(value, str):
        return True
    v = value.strip().lower()
    if not v:
        return True
    if v in ROLE_LABELS:
        return True
    # Slash-separated role descriptions like "Claude / script / human"
    if "/" in v and any(part.strip() in ROLE_LABELS for part in v.split("/")):
        return True
    return False


def validate_required(path: Path, data: dict, required: list[str], prefix: str = "") -> list[str]:
    problems: list[str] = []
    for key in required:
        value = data.get(key)
        if empty(value):
            problems.append(f"{path}: missing or empty `{prefix + key}`")
    return problems


def validate_nested(path: Path, data: dict) -> list[str]:
    problems: list[str] = []
    for parent, children in REQUIRED_NESTED.items():
        value = data.get(parent)
        if not isinstance(value, dict):
            problems.append(f"{path}: `{parent}` must be a mapping")
            continue
        problems.extend(validate_required(path, value, children, f"{parent}."))
    return problems


def validate_eou_card(path: Path, root: Path) -> list[str]:
    problems: list[str] = []
    data = load_yaml(path)
    if not isinstance(data, dict):
        return [f"{path}: EOU spec must be a mapping"]
    problems.extend(validate_required(path, data, REQUIRED_TOP))
    if data.get("id") and data.get("id") != path.stem:
        problems.append(f"{path}: id `{data.get('id')}` does not match filename `{path.stem}`")
    problems.extend(validate_nested(path, data))

    c = data.get("classification") if isinstance(data.get("classification"), dict) else {}
    if c.get("function") not in VALID_FUNCTIONS:
        problems.append(f"{path}: classification.function must be one of {sorted(VALID_FUNCTIONS)}")
    if c.get("automation_mode") not in VALID_AUTOMATION:
        problems.append(f"{path}: classification.automation_mode must be one of {sorted(VALID_AUTOMATION)}")
    if c.get("authority_level") not in VALID_AUTHORITY:
        problems.append(f"{path}: classification.authority_level must be one of {sorted(VALID_AUTHORITY)}")
    if c.get("risk_level") not in VALID_RISK:
        problems.append(f"{path}: classification.risk_level must be one of {sorted(VALID_RISK)}")
    if c.get("lifecycle_stage") not in VALID_STAGE:
        problems.append(f"{path}: classification.lifecycle_stage must be one of {sorted(VALID_STAGE)}")

    if c.get("function") == "generate":
        for key in GENERATING_REQUIRED:
            if empty(data.get(key)):
                problems.append(f"{path}: generating EOU missing `{key}`")
        if c.get("authority_level") not in SAFE_GENERATING_AUTHORITY:
            problems.append(f"{path}: generating EOU authority must not be approve/publish/mutate_active")
        env = data.get("generation_envelope") if isinstance(data.get("generation_envelope"), dict) else {}
        problems.extend(validate_required(path, env, GENERATION_ENVELOPE_REQUIRED, "generation_envelope."))
        if env.get("default_status") != "candidate":
            problems.append(f"{path}: generation_envelope.default_status must be `candidate`")
        forbidden = set(env.get("forbidden_outputs") or [])
        for danger in ["active_eou", "approved_eou", "constitution_change", "validator_weakening"]:
            if danger not in forbidden and not any(danger in str(x) for x in forbidden):
                problems.append(f"{path}: generation_envelope.forbidden_outputs should forbid `{danger}`")
        budget = data.get("generation_budget") if isinstance(data.get("generation_budget"), dict) else {}
        if isinstance(budget.get("max_candidates"), int) and isinstance(env.get("max_candidates"), int):
            if budget["max_candidates"] > env["max_candidates"]:
                problems.append(f"{path}: generation_budget.max_candidates cannot exceed generation_envelope.max_candidates")
        for gate in ["registry_diff", "minimality_test", "operational_value_test", "counter_generation"]:
            value = data.get(gate)
            if not isinstance(value, dict):
                problems.append(f"{path}: `{gate}` must be a mapping")
                continue
            if gate == "registry_diff" and value.get("required") is not True:
                problems.append(f"{path}: `registry_diff.required` must be true")
        cc = data.get("counter_generation") if isinstance(data.get("counter_generation"), dict) else {}
        if cc.get("required") is not False:
            rfc = cc.get("requires_for_each_candidate") or []
            if isinstance(rfc, list) and "arguments_against" not in rfc:
                problems.append(f"{path}: counter_generation.requires_for_each_candidate must include `arguments_against`")

    # Rule 94: executor != approver. Structural separation, not a heuristic.
    resp = data.get("responsibility") if isinstance(data.get("responsibility"), dict) else {}
    exec_id = resp.get("executor")
    approver_id = resp.get("approver")
    if isinstance(exec_id, str) and isinstance(approver_id, str) and exec_id.strip() == approver_id.strip() and exec_id.strip():
        problems.append(
            f"{path}: rule 94 violation — responsibility.executor must not equal "
            f"responsibility.approver (both = `{exec_id.strip()}`)"
        )

    # Active EOUs must have a named human approver (no role labels). Approve/
    # publish authority at any stage must also be a named human.
    stage = c.get("lifecycle_stage")
    if stage in ACTIVE_STAGES or c.get("authority_level") in {"approve", "publish"}:
        if is_role_label(approver_id):
            problems.append(
                f"{path}: rule 91 violation — responsibility.approver must be a "
                f"named human identity for active/approve/publish EOUs "
                f"(got `{approver_id}`); role labels are rejected"
            )

    if c.get("authority_level") in {"approve", "publish"}:
        cannot = " ".join(resp.get("cannot_delegate") or []).lower()
        if "human" not in cannot and "final" not in cannot:
            problems.append(f"{path}: approve/publish authority requires explicit non-delegable human responsibility")

    blast = data.get("blast_radius")
    if not isinstance(blast, dict) or empty(blast.get("allowed_scope")) or empty(blast.get("forbidden_scope")):
        problems.append(f"{path}: missing blast_radius.allowed_scope/forbidden_scope")

    return problems


def _merge_constitution(engine_defaults: dict, app_local: dict) -> tuple[dict, list[str]]:
    """Merge engine-default constitution with app local; refuse weakening.

    Weakening protection covers:
      - List fields (invariants, forbidden, generation_invariants): if local
        re-declares, it must contain every engine entry. Final value is the
        union of engine + local + *_additional.
      - change_rules (dict): if local declares, it must contain every engine
        key with values at least as restrictive (substring match) as engine.
      - purpose (string): if local declares, it cannot be empty.
    """
    problems: list[str] = []
    merged: dict = dict(engine_defaults)

    list_fields = ("invariants", "forbidden", "generation_invariants")
    for field in list_fields:
        engine_list = list(engine_defaults.get(field) or [])
        local_list = list(app_local.get(field) or [])
        additional = list(app_local.get(f"{field}_additional") or [])
        if local_list:
            missing = [item for item in engine_list if item not in local_list]
            if missing:
                problems.append(
                    f"constitution: cannot weaken engine `{field}` — missing engine "
                    f"entries: {missing}"
                )
        seen = set()
        union: list = []
        for src in (engine_list, local_list, additional):
            for item in src:
                if item not in seen:
                    union.append(item)
                    seen.add(item)
        merged[field] = union

    # purpose: scalar; local may refine but not empty out.
    if "purpose" in app_local:
        v = app_local.get("purpose")
        if not isinstance(v, str) or not v.strip():
            problems.append("constitution: cannot weaken `purpose` to empty/non-string")
        else:
            merged["purpose"] = v

    # optimize_for / do_not_optimize_for_alone: list-like; do union, no weakening.
    for field in ("optimize_for", "do_not_optimize_for_alone"):
        engine_list = list(engine_defaults.get(field) or [])
        local_list = list(app_local.get(field) or [])
        if local_list:
            missing = [item for item in engine_list if item not in local_list]
            if missing:
                problems.append(
                    f"constitution: cannot weaken engine `{field}` — missing engine "
                    f"entries: {missing}"
                )
            # union
            seen = set()
            union: list = []
            for src in (engine_list, local_list):
                for item in src:
                    if item not in seen:
                        union.append(item)
                        seen.add(item)
            merged[field] = union

    # change_rules: dict; local may add or strengthen entries, never drop or
    # silently replace. Each engine key must be present in the merged result
    # with engine wording (or a strengthened wording the validator can verify
    # — for 0.5.1 we require engine wording to be a substring of the merged
    # value).
    engine_rules = engine_defaults.get("change_rules") or {}
    local_rules = app_local.get("change_rules") or {}
    if isinstance(engine_rules, dict):
        merged_rules: dict = dict(engine_rules)
        if isinstance(local_rules, dict):
            for k, v in local_rules.items():
                if k in engine_rules:
                    engine_v = str(engine_rules[k])
                    local_v = str(v)
                    if engine_v.strip() not in local_v:
                        problems.append(
                            f"constitution: cannot weaken engine `change_rules.{k}` "
                            f"— engine wording must remain a substring of any local override"
                        )
                merged_rules[k] = v
        # Missing engine keys in a fully-replaced local dict is also weakening.
        if isinstance(local_rules, dict) and local_rules:
            for k in engine_rules:
                if k not in merged_rules:
                    problems.append(
                        f"constitution: cannot drop engine `change_rules.{k}`"
                    )
        merged["change_rules"] = merged_rules

    return merged, problems


def load_constitution(root: Path, plugin_root: Path) -> tuple[Path, dict | None, list[str]]:
    path = root / "foundry" / "constitution.yml"
    if not path.exists():
        return path, None, ["foundry/constitution.yml missing"]
    local = load_yaml(path)
    if not isinstance(local, dict):
        return path, None, [f"{path}: top-level YAML must be a mapping"]

    if "inherits_from" not in local:
        return path, local, []

    # Enforce the inherits_from version constraint against the installed
    # plugin's version (per ECP-0005).
    parsed = parse_inherits_from(str(local["inherits_from"]))
    if parsed is None:
        return path, None, [
            f"{path}: inherits_from `{local['inherits_from']}` does not match "
            f"`<name>@(==|>=|~=)?<version>` (supported subset)"
        ]
    name, op, declared = parsed
    if name != "eou-foundry":
        return path, None, [
            f"{path}: inherits_from name `{name}` is not `eou-foundry`; "
            f"cross-plugin inheritance is out of scope in 0.5.x"
        ]
    installed_str = read_plugin_version(plugin_root)
    if not installed_str:
        return path, None, [
            f"{path}: could not read plugin version from "
            f"{plugin_root}/.claude-plugin/plugin.json"
        ]
    installed = _parse_version(installed_str)
    if not version_satisfies(installed, op, declared):
        return path, None, [
            f"{path}: inherits_from constraint `{local['inherits_from']}` not "
            f"satisfied by installed plugin {installed_str}"
        ]

    defaults_path = plugin_root / "engine" / "constitution-defaults.yml"
    if not defaults_path.exists():
        return path, None, [
            f"{path}: inherits_from declared but engine defaults not found at "
            f"{defaults_path}"
        ]
    defaults = load_yaml(defaults_path)
    if not isinstance(defaults, dict):
        return path, None, [f"{defaults_path}: must be a mapping"]
    merged, problems = _merge_constitution(defaults, local)
    # Carry app preamble through so downstream checks (e.g., owner) can read it.
    for k in ("inherits_from", "application"):
        if k in local:
            merged[k] = local[k]
    return path, merged, problems


def _has_active_eou(root: Path) -> bool:
    registry = root / "foundry" / "registry.yml"
    if not registry.exists():
        return False
    data = load_yaml(registry)
    if not isinstance(data, dict):
        return False
    for entry in data.get("entries") or []:
        if isinstance(entry, dict):
            stage = (entry.get("classification") or {}).get("lifecycle_stage")
            if stage in ACTIVE_STAGES or entry.get("status") == "active":
                return True
    return False


def validate_constitution(root: Path, plugin_root: Path) -> tuple[list[str], list[str]]:
    path, data, problems = load_constitution(root, plugin_root)
    warnings: list[str] = []
    if data is None:
        return problems, warnings
    problems.extend(validate_required(path, data, CONSTITUTION_REQUIRED))
    inv = "\n".join(data.get("invariants") or [])
    gen = "\n".join(data.get("generation_invariants") or [])
    for phrase in ["No EOU may approve its own change alone", "Failure history cannot be deleted", "Validation cannot be weakened"]:
        if phrase not in inv:
            problems.append(f"{path}: constitution should include invariant containing `{phrase}`")
    for phrase in ["default to candidate status", "cannot activate", "arguments against creation", "minimal recommended subset"]:
        if phrase not in gen:
            problems.append(f"{path}: generation_invariants should include `{phrase}`")

    # Application owner: required structurally; named human required when any
    # active EOU is registered.
    app = data.get("application") if isinstance(data.get("application"), dict) else {}
    owner = app.get("owner")
    if empty(owner):
        problems.append(f"{path}: application.owner missing or empty")
    elif is_todo(owner):
        problems.append(
            f"{path}: application.owner is a TODO marker (`{owner}`); "
            f"name the responsible human before activating any EOU"
        )
    elif _has_active_eou(root) and is_role_label(owner):
        problems.append(
            f"{path}: application.owner is a role label (`{owner}`); "
            f"rule 91 requires a named human identity once any EOU is active"
        )
    return problems, warnings


def _engine_eou_ids(plugin_root: Path) -> set[str]:
    ids: set[str] = set()
    meta = plugin_root / "engine" / "meta-eous"
    if not meta.exists():
        return ids
    for p in meta.glob("*.yml"):
        data = load_yaml(p)
        if isinstance(data, dict) and data.get("id"):
            ids.add(str(data["id"]))
    return ids


def validate_registry(root: Path, app_eou_paths: dict[str, Path],
                      plugin_root: Path) -> tuple[list[str], list[str]]:
    path = root / "foundry" / "registry.yml"
    problems: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return ["foundry/registry.yml missing"], warnings
    data = load_yaml(path)
    problems.extend(validate_required(path, data, REGISTRY_REQUIRED))
    entries = data.get("entries") or []
    if not isinstance(entries, list):
        problems.append(f"{path}: registry.entries must be a list")
        return problems, warnings
    if not entries:
        return problems, warnings

    engine_ids = _engine_eou_ids(plugin_root)

    seen = set()
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            problems.append(f"{path}: entry {idx} must be a mapping")
            continue
        problems.extend(validate_required(path, entry, REG_ENTRY_REQUIRED, f"entries[{idx}]."))
        eou_id = entry.get("eou_id")
        if eou_id in seen:
            problems.append(f"{path}: duplicate registry entry `{eou_id}`")
        seen.add(eou_id)
        if eou_id in engine_ids:
            problems.append(
                f"{path}: registry entry `{eou_id}` is a plugin-canonical engine "
                f"meta-EOU; engine meta-EOUs must not appear in app registries"
            )
            continue
        rel = entry.get("path")
        if rel and not (root / rel).exists():
            problems.append(f"{path}: registry path does not exist: {rel}")
        if eou_id and eou_id not in app_eou_paths:
            problems.append(f"{path}: registry entry `{eou_id}` has no matching EOU spec")

        # Enum-check the registry's classification fields against the same
        # vocabulary used for EOU specs.
        c = entry.get("classification") or {}
        for field, valid in (
            ("function", VALID_FUNCTIONS),
            ("automation_mode", VALID_AUTOMATION),
            ("authority_level", VALID_AUTHORITY),
            ("risk_level", VALID_RISK),
            ("lifecycle_stage", VALID_STAGE),
        ):
            v = c.get(field)
            if v is not None and v not in valid:
                problems.append(
                    f"{path}: registry entry `{eou_id}` classification.{field} "
                    f"= `{v}` not in {sorted(valid)}"
                )
        if c.get("authority_level") in {"approve", "publish"}:
            problems.append(f"{path}: registry entry `{eou_id}` has unsafe approve/publish authority")

        # Cross-check: registry classification should match the spec's
        # classification exactly.
        spec_path = app_eou_paths.get(eou_id)
        if spec_path:
            spec = load_yaml(spec_path)
            if isinstance(spec, dict):
                spec_c = spec.get("classification") or {}
                for field in ("function", "automation_mode", "authority_level",
                              "risk_level", "lifecycle_stage"):
                    rv, sv = c.get(field), spec_c.get(field)
                    if rv is not None and sv is not None and rv != sv:
                        problems.append(
                            f"{path}: registry entry `{eou_id}` classification.{field} "
                            f"= `{rv}` does not match spec `{sv}` ({spec_path})"
                        )

    for eou_id in sorted(set(app_eou_paths) - seen):
        problems.append(f"{path}: EOU spec `{eou_id}` missing from registry")
    return problems, warnings


# Files in foundry/self-evolution/ecp/proposed/ matching this pattern are
# candidate-set artifacts (rule 95), NOT ECPs. They have their own shape.
CANDIDATE_SET_PATTERN = re.compile(r"-candidates-\d{8}\.ya?ml$|-candidates(?:\..*)?\.ya?ml$")


def validate_ecps(root: Path) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []
    base = root / "foundry" / "self-evolution" / "ecp"
    upstream = root / "foundry" / "self-evolution" / "upstream"
    if not base.exists():
        return ["foundry/self-evolution/ecp missing"], warnings
    required = ["id", "target_eou", "target_version_from", "target_version_to",
                "problem", "proposed_change", "expected_benefit", "risks",
                "tests_required", "simulation", "approval"]
    paths = list(base.rglob("*.yml"))
    if upstream.exists():
        paths.extend(upstream.rglob("*.yml"))
    for path in sorted(paths):
        # Skip candidate-set artifacts (rule 95): they share these directories
        # but have a different schema.
        if CANDIDATE_SET_PATTERN.search(path.name):
            continue
        data = load_yaml(path)
        problems.extend(validate_required(path, data, required))
        approval = data.get("approval") or {}
        status = approval.get("status")
        approver = approval.get("approver") or approval.get("approved_by")
        if status in {"approved", "implemented"}:
            if not approver:
                problems.append(f"{path}: {status} ECP lacks approver (or legacy approved_by)")
            if not approval.get("rollback_considerations"):
                problems.append(
                    f"{path}: {status} ECP requires `approval.rollback_considerations` "
                    f"per rule 92"
                )
        if approval.get("approved_by") and not approval.get("approver"):
            warnings.append(
                f"deprecation: {path} uses `approval.approved_by`; rename to "
                f"`approval.approver` (legacy field accepted through 0.5.x)"
            )
    return problems, warnings


def validate_regression_cases(root: Path) -> list[str]:
    problems: list[str] = []
    base = root / "foundry" / "self-evolution" / "regression" / "cases"
    if not base.exists():
        return ["foundry/self-evolution/regression/cases missing"]
    required = ["id", "target_eou", "failure_class", "failure_observed", "fixture", "expected_behavior", "activation_status", "requires_approval"]
    for path in sorted(base.glob("*.yml")):
        data = load_yaml(path)
        problems.extend(validate_required(path, data, required))
        if data.get("activation_status") not in {"candidate", "active", "retired"}:
            problems.append(f"{path}: invalid activation_status")
    return problems


def validate_incidents(root: Path) -> list[str]:
    problems: list[str] = []
    base = root / "foundry" / "incidents"
    if not base.exists():
        return []
    for path in sorted(base.glob("*.yml")):
        data = load_yaml(path)
        if not isinstance(data, dict):
            problems.append(f"{path}: incident must be a mapping")
            continue
        problems.extend(validate_required(path, data, INCIDENT_REQUIRED))
        # id should match filename stem (consistent with EOU spec convention)
        if data.get("id") and data.get("id") != path.stem:
            problems.append(
                f"{path}: incident id `{data.get('id')}` does not match filename `{path.stem}`"
            )
    return problems


def validate_engine_artifacts(plugin_root: Path) -> list[str]:
    """Defensive: verify the plugin's engine/*.yml files are well-formed and
    contain the structural top-level keys downstream consumers depend on."""
    problems: list[str] = []
    engine = plugin_root / "engine"
    if not engine.exists():
        return [f"plugin engine/ missing at {engine}"]
    for fname, toplevel in ENGINE_TOPLEVEL.items():
        path = engine / fname
        if not path.exists():
            problems.append(f"plugin engine/{fname} missing")
            continue
        try:
            data = load_yaml(path)
        except Exception as exc:
            problems.append(f"plugin engine/{fname}: invalid YAML: {exc}")
            continue
        if not isinstance(data, dict):
            problems.append(f"plugin engine/{fname}: top-level must be a mapping")
            continue
        if toplevel and toplevel not in data:
            problems.append(
                f"plugin engine/{fname}: missing top-level key `{toplevel}`"
            )
    return problems


def validate_overrides(root: Path, plugin_root: Path) -> tuple[list[str], list[str]]:
    """Validate foundry/overrides/<engine-file>.yml entries. Each override may
    add keys or refine values, but may NOT drop top-level keys present in the
    corresponding engine canonical."""
    problems: list[str] = []
    warnings: list[str] = []
    overrides = root / "foundry" / "overrides"
    if not overrides.exists():
        return problems, warnings
    for path in sorted(overrides.glob("*.yml")):
        if path.name == ".gitkeep":
            continue
        canonical = plugin_root / "engine" / path.name
        if not canonical.exists():
            problems.append(
                f"{path}: no matching engine artifact at engine/{path.name}; "
                f"overrides must shadow an engine file"
            )
            continue
        try:
            override_data = load_yaml(path)
            engine_data = load_yaml(canonical)
        except Exception as exc:
            problems.append(f"{path}: invalid YAML: {exc}")
            continue
        if not isinstance(override_data, dict) or not isinstance(engine_data, dict):
            problems.append(f"{path}: both override and engine canonical must be mappings")
            continue
        dropped = [k for k in engine_data if k not in override_data]
        if dropped:
            # An override that omits engine keys is not weakening — the merge
            # treats missing override keys as "inherit engine value." But an
            # override that DECLARES a key with empty/null value IS weakening.
            for k in engine_data:
                if k in override_data and empty(override_data[k]) and not empty(engine_data[k]):
                    problems.append(
                        f"{path}: override drops engine key `{k}` (set empty); "
                        f"omit the key to inherit, or set a non-empty value to strengthen"
                    )
        warnings.append(
            f"overrides applied: foundry/overrides/{path.name} merges over "
            f"plugin engine/{path.name}"
        )
    return problems, warnings


def check_legacy_engine_copies(root: Path, plugin_root: Path) -> list[str]:
    """Deprecation warnings for byte-identical legacy local copies of engine
    artifacts. v0.5.x tolerates; v1.0.0 will reject."""
    warnings: list[str] = []
    for fname in ENGINE_FILES:
        local = root / "foundry" / fname
        canonical = plugin_root / "engine" / fname
        if local.exists() and canonical.exists():
            try:
                if local.read_bytes() == canonical.read_bytes():
                    warnings.append(
                        f"deprecation: foundry/{fname} is a byte-identical "
                        f"copy of plugin engine/{fname}; delete the local "
                        f"copy (engine is read from plugin)."
                    )
                else:
                    warnings.append(
                        f"deprecation: foundry/{fname} differs from plugin "
                        f"engine/{fname}; if this is intentional, move the "
                        f"override to foundry/overrides/{fname} and delete "
                        f"foundry/{fname}."
                    )
            except OSError:
                pass

    local_meta = root / "foundry" / "meta-eous"
    canonical_meta = plugin_root / "engine" / "meta-eous"
    if local_meta.exists() and canonical_meta.exists():
        identical = 0
        divergent: list[str] = []
        for p in sorted(local_meta.glob("*.yml")):
            cp = canonical_meta / p.name
            if cp.exists():
                try:
                    if p.read_bytes() == cp.read_bytes():
                        identical += 1
                    else:
                        divergent.append(p.name)
                except OSError:
                    pass
        if identical:
            warnings.append(
                f"deprecation: foundry/meta-eous/ has {identical} byte-identical "
                f"copies of plugin engine/meta-eous/; delete foundry/meta-eous/ "
                f"if it has no app-specific divergence."
            )
        if divergent:
            warnings.append(
                f"deprecation: foundry/meta-eous/ has {len(divergent)} divergent "
                f"file(s) ({', '.join(divergent[:3])}{'...' if len(divergent) > 3 else ''}); "
                f"move app-specific divergence to foundry/overrides/meta-eous/."
            )
    return warnings


def validate_foundry(root: Path, plugin_root: Path) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    warnings: list[str] = []

    foundry = root / "foundry"
    if not foundry.exists():
        problems.append("missing foundry/ directory")
        return problems, warnings

    # Plugin-side sanity check: the engine artifacts the app inherits from
    # must themselves be well-formed.
    problems.extend(validate_engine_artifacts(plugin_root))

    p, w = validate_constitution(root, plugin_root)
    problems.extend(p)
    warnings.extend(w)

    engine_dir = plugin_root / "engine"
    canonical_meta = engine_dir / "meta-eous"
    if not canonical_meta.exists():
        problems.append(f"plugin engine/meta-eous/ not found at {canonical_meta}")

    engine_eou_paths: dict[str, Path] = {}
    app_eou_paths: dict[str, Path] = {}

    if canonical_meta.exists():
        for path in sorted(canonical_meta.glob("*.yml")):
            problems.extend(validate_eou_card(path, plugin_root))
            data = load_yaml(path)
            if isinstance(data, dict) and data.get("id"):
                engine_eou_paths[str(data["id"])] = path

    app_eous = foundry / "eous"
    if not app_eous.exists():
        problems.append("missing foundry/eous/ directory")
    else:
        for path in sorted(app_eous.glob("*.yml")):
            data = load_yaml(path)
            if isinstance(data, dict) and data.get("id"):
                app_eou_paths[str(data["id"])] = path
            problems.extend(validate_eou_card(path, root))

    app_meta = foundry / "meta-eous"
    if app_meta.exists():
        for path in sorted(app_meta.glob("*.yml")):
            canonical_path = canonical_meta / path.name if canonical_meta.exists() else None
            if canonical_path and canonical_path.exists():
                try:
                    if path.read_bytes() == canonical_path.read_bytes():
                        continue
                except OSError:
                    pass
            data = load_yaml(path)
            if isinstance(data, dict) and data.get("id"):
                app_eou_paths[str(data["id"])] = path
            problems.extend(validate_eou_card(path, root))

    if not engine_eou_paths and not app_eou_paths:
        problems.append("foundry: no EOU specs found")

    p, w = validate_registry(root, app_eou_paths, plugin_root)
    problems.extend(p)
    warnings.extend(w)

    p, w = validate_ecps(root)
    problems.extend(p)
    warnings.extend(w)

    problems.extend(validate_regression_cases(root))
    problems.extend(validate_incidents(root))

    p, w = validate_overrides(root, plugin_root)
    problems.extend(p)
    warnings.extend(w)

    warnings.extend(check_legacy_engine_copies(root, plugin_root))

    return problems, warnings


def main() -> int:
    from _common import cli_error as _cli_error
    try:
        ap = argparse.ArgumentParser()
        ap.add_argument("path", nargs="?", default=None, help="Optional repository root")
        ap.add_argument("--strict-no-legacy", action="store_true",
                        help="Treat legacy local engine copies as errors, not warnings.")
        args = ap.parse_args()
        from _common import cli_error
        try:
            root = Path(args.path).resolve() if args.path else find_repo_root()
        except RuntimeError as e:
            cli_error(str(e))

        plugin_root = find_plugin_root()
        problems, warnings = validate_foundry(root, plugin_root)

        if args.strict_no_legacy:
            problems.extend(warnings)
            warnings = []

        if warnings:
            print("Foundry warnings:", file=sys.stderr)
            for w in warnings:
                print(f"- {w}", file=sys.stderr)

        if problems:
            print("Foundry validation failed:")
            for p in problems:
                print(f"- {p}")
            return 1
        print("OK: foundry")
        return 0

    except (FileNotFoundError, ValueError, RuntimeError) as _e:
        _cli_error(str(_e))


if __name__ == "__main__":
    raise SystemExit(main())
