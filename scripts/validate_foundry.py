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

# ECP-0018: agentic-judgment package
JUDGMENT_AUTHORIZED_STAGES_REQUIRING_PER_EOU_ECP = {"pilot", "active", "monitored", "stable"}
VALUE_INVOCATION_REQUIRED_FIELDS = ["invocation_id", "timestamp", "captured_workflow_id",
                                    "captured_workflow_version", "domain_value_id",
                                    "priority_at_invocation", "rule_conflict",
                                    "chosen_path", "rejected_alternative",
                                    "justification_against_rejected"]
VALUE_INVOCATION_STRAWMAN_REGEX = re.compile(r"\b(strawman|a\s+weak(er)?|a\s+worse|generic)\b", re.IGNORECASE)

# ECP-0019: agentic-judgment failure codes (taxonomy entries live in engine/failure-taxonomy.yml)
VALID_FAILURE_CLASSES_AGENTIC = {"F14_SILENT_JUDGMENT_FAILURE", "F15_VALUE_HIERARCHY_FAILURE",
                                 "F16_VALUE_DRIFT_FAILURE", "F17_VALUE_HALLUCINATION_FAILURE"}
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
RUN_TRACE_REQUIRED = ["run_id", "eou_id", "eou_version", "status", "started_at", "ended_at", "executor_identity", "inputs", "context_loaded", "steps_completed", "warnings", "outputs", "validation", "human_approval"]
RUN_TRACE_VALID_STATUS = {"success", "partial", "failed", "aborted"}
NO_TRACE_REQUIRED = ["eou_id", "impossibility_reason", "reviewed_by", "reviewed_at", "expires_at"]
CANDIDATE_SET_REQUIRED = ["id", "generated_by", "generated_at", "target_class", "candidates", "audit_outcome", "audit_status"]
CANDIDATE_SET_AUDIT_OUTCOME_KEYS = ["accepted", "merged", "demoted_to_rule", "demoted_to_validator", "demoted_to_stop_condition", "rejected", "minimal_recommended_subset"]
CANDIDATE_SET_VALID_STATUS = {"pending_audit", "audited", "rejected_in_full"}
CANDIDATE_SET_VALID_TARGET_CLASS = {"eou_spec", "ecp", "regression_case", "refactor_option"}

# ECP-0015: captured_workflow noun + schema
CAPTURED_WORKFLOW_REQUIRED = ["id", "schema_version", "created_at", "inputs", "artifact_target",
                              "captured_workflow", "hidden_judgments", "failure_modes",
                              "decision_boundaries", "domain_values", "confidence", "human_approval"]
CAPTURED_WORKFLOW_INPUTS_REQUIRED = ["goal", "reference_set", "constraints",
                                     "negative_constraints", "user_contributed_references"]
CAPTURED_WORKFLOW_ROLE_SLOTS = ["aspirational", "anti_reference", "boundary_case",
                                "mainstream_baseline", "outlier"]
CAPTURED_WORKFLOW_DV_REQUIRED = ["id", "formulation", "priority", "canonical_or_personal",
                                 "protects_against", "decides_when", "inclusion_test_passes"]
CAPTURED_WORKFLOW_DV_CANONICAL_ENUM = {"field_canonical", "user_personal", "user_diverges_from_canonical"}
CAPTURED_WORKFLOW_INCLUSION_TEST_KEYS = ["prevents_domain_failure", "resolves_rule_conflict",
                                         "exposes_hidden_judgment", "resists_false_success",
                                         "protects_invariant", "removal_makes_practice_dangerous"]
CAPTURED_WORKFLOW_CONFIDENCE_KEYS = ["artifact_target", "hidden_judgments", "failure_modes",
                                     "decision_boundaries", "domain_values"]
CAPTURED_WORKFLOW_CONFIDENCE_ENUM = {"low", "medium", "high"}
CAPTURED_WORKFLOW_APPROVAL_GATES = ["reference_set_approved_by", "constraints_approved_by",
                                    "domain_values_approved_by", "bundle_approved_by",
                                    "approved_at"]
CAPTURED_WORKFLOW_DV_MIN = 3
CAPTURED_WORKFLOW_DV_MAX = 8
CAPTURED_WORKFLOW_FORMULATION_PATTERN = re.compile(r"^\s*\S.*\s+over\s+\S.*$", re.IGNORECASE)
CAPTURED_WORKFLOW_STRAWMAN_LIST: set[str] = set()   # empty initially; expand as cases surface
LIFECYCLE_TO_MATURITY = {
    "candidate":  "L1_NARRATIVE",
    "draft":      "L2_STRUCTURED",
    "simulated":  "L2_STRUCTURED",
    "pilot":      "L3_EXECUTABLE",
    "active":     "L4_AUDITABLE",
    "monitored":  "L5_GOVERNED",
    "stable":     "L6_SELF_IMPROVING",
}
MATURITY_ORDER = ["L0_TACIT", "L1_NARRATIVE", "L2_STRUCTURED", "L3_EXECUTABLE", "L4_AUDITABLE", "L5_GOVERNED", "L6_SELF_IMPROVING"]

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
    2. ~/.claude/plugins/installed_plugins.json — read the installPath
       for `eou-foundry@xiaolai` if installed via Claude Code.
    3. Path(__file__).parents[1] (fallback when this script is invoked
       directly inside a plugin checkout — plugin self-test).

    No hardcoded user-specific fallback paths.
    """
    env = os.environ.get("EOU_FOUNDRY_PLUGIN_PATH")
    if env:
        p = Path(env).expanduser().resolve()
        if (p / ".claude-plugin" / "plugin.json").exists():
            return p

    # Read Claude Code's installed_plugins registry. The registry may list
    # multiple installs (different versions and/or scopes); their array order
    # is not version-sorted, so resolve to the highest installed version rather
    # than the first entry that happens to be valid.
    registry = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if registry.exists():
        try:
            data = json.loads(registry.read_text())
            entries = (data.get("plugins") or {}).get("eou-foundry@xiaolai") or []
            best: tuple[tuple[int, int, int], Path] | None = None
            for entry in entries:
                install_path = entry.get("installPath")
                if not install_path:
                    continue
                p = Path(install_path).expanduser().resolve()
                if not (p / ".claude-plugin" / "plugin.json").exists():
                    continue
                ver_str = entry.get("version") or read_plugin_version(p) or "0.0.0"
                try:
                    ver = _parse_version(ver_str)
                except (ValueError, AttributeError):
                    ver = (0, 0, 0)
                if best is None or ver > best[0]:
                    best = (ver, p)
            if best is not None:
                return best[1]
        except (OSError, json.JSONDecodeError, AttributeError):
            pass

    # Last-resort fallback: directory two levels up from this script
    # (plugin self-test from within a checkout).
    fallback = Path(__file__).resolve().parents[1]
    if (fallback / ".claude-plugin" / "plugin.json").exists():
        return fallback

    raise RuntimeError(
        "Plugin root not found. Set EOU_FOUNDRY_PLUGIN_PATH to your plugin "
        "checkout, install via `claude plugin install eou-foundry@xiaolai`, "
        "or run from inside a plugin checkout."
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

    # ECP-0018: judgment_authorized validation
    ja = c.get("judgment_authorized")
    if ja is not None:
        if not isinstance(ja, bool):
            problems.append(f"{path}: classification.judgment_authorized must be a boolean (got {ja!r})")
        elif ja is True:
            # Forbidden on function:generate per D6.1
            if c.get("function") == "generate":
                problems.append(
                    f"{path}: F4_SCOPE_FAILURE — classification.judgment_authorized:true "
                    f"forbidden on function:generate (D6.1: generators may not create authority; ECP-0018)"
                )
            # captured_workflow precondition + risk-tier authorization checks
            problems.extend(_validate_judgment_authorization_precondition(path, c, root))

    return problems


def _validate_judgment_authorization_precondition(spec_path: Path, classification: dict, root: Path) -> list[str]:
    """ECP-0018: judgment_authorized:true requires (a) app has an approved
    captured_workflow with ≥3 domain_values; (b) at risk_level high|critical
    at pilot+, per-EOU ECP approval is required."""
    problems: list[str] = []
    cw_dir = root / "foundry" / "captured-workflows"
    has_qualifying_cw = False
    if cw_dir.exists():
        for cw_path in cw_dir.glob("*.yml"):
            if cw_path.name == ".gitkeep":
                continue
            cw = load_yaml(cw_path)
            if not isinstance(cw, dict):
                continue
            ha = cw.get("human_approval") or {}
            all_gates_filled = all(ha.get(g) for g in CAPTURED_WORKFLOW_APPROVAL_GATES)
            dvs = cw.get("domain_values") or []
            if all_gates_filled and isinstance(dvs, list) and len(dvs) >= CAPTURED_WORKFLOW_DV_MIN:
                has_qualifying_cw = True
                break
    if not has_qualifying_cw:
        problems.append(
            f"{spec_path}: classification.judgment_authorized:true requires an "
            f"approved captured_workflow with ≥{CAPTURED_WORKFLOW_DV_MIN} "
            f"domain_values in {cw_dir} (ECP-0018 precondition)"
        )

    risk = classification.get("risk_level")
    stage = classification.get("lifecycle_stage")
    if risk in {"high", "critical"} and stage in JUDGMENT_AUTHORIZED_STAGES_REQUIRING_PER_EOU_ECP:
        # Per-EOU ECP is required. Look for blanket-authorization override OR per-EOU ECP.
        gov_path = root / "foundry" / "governance.yml"
        blanket_ok = False
        if gov_path.exists():
            gov = load_yaml(gov_path)
            if isinstance(gov, dict):
                blanket = gov.get("judgment_blanket_authorization") or {}
                if (
                    isinstance(blanket, dict)
                    and blanket.get("enabled") is True
                    and blanket.get("max_risk_level") in {"low", "medium", "high", "critical"}
                ):
                    # Per ECP-0018: high/critical NEVER blanket-authorized.
                    # max_risk_level cap is checked here.
                    cap = blanket.get("max_risk_level")
                    cap_ok = (risk == "medium" and cap == "medium") or (risk == "low")
                    blanket_ok = cap_ok
        if not blanket_ok:
            # Per-EOU ECP is required. Check approved/ and implemented/ ECPs for
            # one targeting this EOU's id with judgment_authorized intent.
            ecp_dirs = [root / "foundry" / "self-evolution" / "ecp" / d
                        for d in ("approved", "implemented")]
            spec_id = spec_path.stem
            per_eou_ecp_found = False
            for ecp_dir in ecp_dirs:
                if not ecp_dir.exists():
                    continue
                for ecp_path in ecp_dir.glob("*.yml"):
                    ecp = load_yaml(ecp_path)
                    if not isinstance(ecp, dict):
                        continue
                    target = ecp.get("target_eou", "")
                    summary = (ecp.get("proposed_change") or {}).get("summary", "") if isinstance(ecp.get("proposed_change"), dict) else ""
                    if target == spec_id and "judgment_authorized" in str(summary).lower():
                        per_eou_ecp_found = True
                        break
                if per_eou_ecp_found:
                    break
            if not per_eou_ecp_found:
                problems.append(
                    f"{spec_path}: classification.judgment_authorized:true at "
                    f"risk_level:{risk} lifecycle_stage:{stage} requires per-EOU "
                    f"ECP approval (ECP-0018; no qualifying ECP found in "
                    f"approved/ or implemented/)"
                )
    return problems


def validate_value_invocations_in_trace(trace_path: Path, trace: dict) -> list[str]:
    """ECP-0018: validate value_invocations[] entry shape in run traces.
    Each entry must have all 10 required fields; rejected_alternative
    must not match strawman regex; domain_value_id resolution against
    captured_workflow happens in ECP-0020's
    validate_value_invocation_discipline()."""
    problems: list[str] = []
    invocations = trace.get("value_invocations")
    if invocations is None:
        return problems
    if not isinstance(invocations, list):
        problems.append(f"{trace_path}: value_invocations must be a list")
        return problems
    for idx, inv in enumerate(invocations):
        if not isinstance(inv, dict):
            problems.append(f"{trace_path}: value_invocations[{idx}] must be a mapping")
            continue
        inv_id = inv.get("invocation_id", f"value_invocations[{idx}]")
        for field in VALUE_INVOCATION_REQUIRED_FIELDS:
            if not inv.get(field):
                problems.append(
                    f"{trace_path}: value_invocation `{inv_id}` missing required field `{field}` (ECP-0018)"
                )
        rej = inv.get("rejected_alternative")
        if isinstance(rej, str) and (not rej.strip() or VALUE_INVOCATION_STRAWMAN_REGEX.search(rej)):
            problems.append(
                f"{trace_path}: value_invocation `{inv_id}` rejected_alternative "
                f"is empty or matches strawman pattern (ECP-0018 anti-theater check)"
            )
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


def _maturity_satisfies(claimed: str, required: str) -> bool:
    if claimed not in MATURITY_ORDER or required not in MATURITY_ORDER:
        return False
    return MATURITY_ORDER.index(claimed) >= MATURITY_ORDER.index(required)


def validate_activation_evidence(root: Path) -> list[str]:
    """Per ECP-0010: status:active/monitored/stable entries must have
    activated_by, with either ECP-and-approver evidence OR a legacy
    bootstrap declaration with bootstrap_justification + (non-expired)
    bootstrap_expires_at."""
    problems: list[str] = []
    path = root / "foundry" / "registry.yml"
    if not path.exists():
        return problems
    data = load_yaml(path)
    if not isinstance(data, dict):
        return problems
    entries = data.get("entries") or []
    if not isinstance(entries, list):
        return problems
    import datetime as _dt
    now = _dt.datetime.now(_dt.timezone.utc)
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        status = entry.get("status")
        if status not in ACTIVE_STAGES:
            continue
        eou_id = entry.get("eou_id", f"entries[{idx}]")
        ab = entry.get("activated_by")
        if not isinstance(ab, dict):
            problems.append(
                f"{path}: registry entry `{eou_id}` has status `{status}` but "
                f"`activated_by` is missing (rule 89 / ECP-0010)"
            )
            continue
        if ab.get("legacy_bootstrap") is True:
            if not ab.get("bootstrap_justification"):
                problems.append(
                    f"{path}: registry entry `{eou_id}` has "
                    f"activated_by.legacy_bootstrap: true but no "
                    f"bootstrap_justification"
                )
            expires = ab.get("bootstrap_expires_at")
            if not expires:
                problems.append(
                    f"{path}: registry entry `{eou_id}` legacy_bootstrap "
                    f"needs bootstrap_expires_at (ISO-8601 date)"
                )
            else:
                try:
                    expiry = _dt.datetime.fromisoformat(str(expires).replace("Z", "+00:00"))
                    if expiry < now:
                        problems.append(
                            f"{path}: registry entry `{eou_id}` "
                            f"legacy_bootstrap expired at {expires}"
                        )
                except ValueError:
                    problems.append(
                        f"{path}: registry entry `{eou_id}` "
                        f"bootstrap_expires_at `{expires}` is not ISO-8601"
                    )
        else:
            if not ab.get("ecp_id") and not ab.get("approver"):
                problems.append(
                    f"{path}: registry entry `{eou_id}` activated_by needs "
                    f"ecp_id and approver (or legacy_bootstrap: true)"
                )
    return problems


def validate_maturity_evidence(root: Path) -> list[str]:
    """Per ECP-0009: registry entry's maturity must be at-or-above the
    level mapped from its lifecycle_stage. (For deprecated/retired this
    check is skipped — those are governance states, not maturity claims.)"""
    problems: list[str] = []
    path = root / "foundry" / "registry.yml"
    if not path.exists():
        return problems
    data = load_yaml(path)
    if not isinstance(data, dict):
        return problems
    entries = data.get("entries") or []
    if not isinstance(entries, list):
        return problems
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        eou_id = entry.get("eou_id", f"entries[{idx}]")
        status = entry.get("status")
        if status in {"deprecated", "retired"}:
            continue
        claimed = entry.get("maturity")
        required = LIFECYCLE_TO_MATURITY.get(status)
        if not required or not claimed:
            continue
        if not _maturity_satisfies(claimed, required):
            problems.append(
                f"{path}: registry entry `{eou_id}` claims maturity "
                f"`{claimed}` at lifecycle_stage `{status}`, but `{status}` "
                f"requires `{required}` per engine/maturity-model.yml mapping"
            )
    return problems


def validate_dependency_dag(root: Path) -> list[str]:
    """Per ECP-0009: build the EOU dependency DAG; reject cycles and
    references to retired EOUs."""
    problems: list[str] = []
    path = root / "foundry" / "registry.yml"
    if not path.exists():
        return problems
    data = load_yaml(path)
    if not isinstance(data, dict):
        return problems
    entries = data.get("entries") or []
    if not isinstance(entries, list):
        return problems

    # Build graph: eou_id -> [eou_id...] (only follow dependencies.eous)
    graph: dict[str, list[str]] = {}
    retired: set[str] = set()
    known: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        eou_id = entry.get("eou_id")
        if not eou_id:
            continue
        known.add(eou_id)
        if entry.get("status") == "retired":
            retired.add(eou_id)
        deps = (entry.get("dependencies") or {})
        if isinstance(deps, dict):
            dep_eous = deps.get("eous") or []
        else:
            dep_eous = []
        graph[eou_id] = list(dep_eous) if isinstance(dep_eous, list) else []

    # Reference checks: dangling and retired
    for eou_id, deps in graph.items():
        for d in deps:
            if d not in known:
                problems.append(
                    f"{path}: registry entry `{eou_id}` dependencies.eous "
                    f"references unknown `{d}`"
                )
            elif d in retired:
                problems.append(
                    f"{path}: registry entry `{eou_id}` dependencies.eous "
                    f"references retired `{d}`"
                )

    # Cycle detection via DFS
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {k: WHITE for k in graph}
    cycle_msg: list[str] = []

    def dfs(node: str, stack: list[str]) -> None:
        if color.get(node) == GRAY:
            i = stack.index(node) if node in stack else 0
            cycle_msg.append(" -> ".join(stack[i:] + [node]))
            return
        if color.get(node) == BLACK:
            return
        color[node] = GRAY
        for nxt in graph.get(node, []):
            if nxt in graph:
                dfs(nxt, stack + [node])
        color[node] = BLACK

    for n in list(graph):
        if color[n] == WHITE:
            dfs(n, [])
    for c in cycle_msg:
        problems.append(f"{path}: dependency cycle detected: {c}")

    return problems


def validate_run_traces(root: Path) -> list[str]:
    problems: list[str] = []
    base = root / "foundry" / "runs"
    if not base.exists():
        return problems
    for path in sorted(base.rglob("*.yml")):
        if path.name == ".gitkeep":
            continue
        data = load_yaml(path)
        if not isinstance(data, dict):
            problems.append(f"{path}: run trace must be a mapping")
            continue
        problems.extend(validate_required(path, data, RUN_TRACE_REQUIRED))
        if data.get("status") and data["status"] not in RUN_TRACE_VALID_STATUS:
            problems.append(
                f"{path}: status `{data['status']}` not in {sorted(RUN_TRACE_VALID_STATUS)}"
            )
        # ECP-0018: value_invocations entry-shape validation
        problems.extend(validate_value_invocations_in_trace(path, data))
    return problems


def validate_no_trace_justifications(root: Path) -> list[str]:
    problems: list[str] = []
    base = root / "foundry" / "audits" / "no-trace"
    if not base.exists():
        return problems
    import datetime as _dt
    now = _dt.datetime.now(_dt.timezone.utc)
    for path in sorted(base.glob("*.yml")):
        if path.name == ".gitkeep":
            continue
        data = load_yaml(path)
        if not isinstance(data, dict):
            problems.append(f"{path}: no-trace-justification must be a mapping")
            continue
        problems.extend(validate_required(path, data, NO_TRACE_REQUIRED))
        # ECP-0014 anti-gaming: reviewed_by must be a real human identity,
        # not a TODO placeholder. Mass-generating justifications with TODO
        # owners would defeat the gate.
        reviewer = data.get("reviewed_by")
        if reviewer and is_todo(reviewer):
            problems.append(
                f"{path}: reviewed_by `{reviewer}` is a TODO placeholder; "
                f"name a real human reviewer (ECP-0014)"
            )
        expires = data.get("expires_at")
        if expires:
            try:
                expiry = _dt.datetime.fromisoformat(str(expires).replace("Z", "+00:00"))
                if expiry < now:
                    problems.append(
                        f"{path}: expires_at `{expires}` is in the past; "
                        f"re-review and renew before relying on this justification"
                    )
            except ValueError:
                problems.append(f"{path}: expires_at `{expires}` is not ISO-8601")
    return problems


def validate_active_trace_obligation(root: Path, app_eou_paths: dict[str, Path]) -> list[str]:
    """ECP-0014: every EOU at lifecycle_stage:active must either declare
    trace output OR have a non-expired no-trace-justification on record.

    Hard-cut at 0.6.0 — no warning phase. The no-trace-justification
    mechanism IS the migration path: apps that cannot meet the gate write
    an explicit, time-bounded exemption with a named human reviewer.

    Scope: app-side EOUs only (foundry/eous/, foundry/meta-eous/). Engine
    canonical meta-EOUs are explicitly NOT walked — plugin governs its
    own engine via the foundry-audit skill.

    Check is STRUCTURAL: verifies the spec commits to producing trace, OR
    is exempted. Does NOT verify run trace files exist on disk (that's
    runtime, not validation — would break CI/scaffold contexts).
    """
    problems: list[str] = []
    no_trace_dir = root / "foundry" / "audits" / "no-trace"
    for eou_id, spec_path in sorted(app_eou_paths.items()):
        data = load_yaml(spec_path)
        if not isinstance(data, dict):
            continue
        c = data.get("classification") or {}
        if c.get("lifecycle_stage") not in ACTIVE_STAGES:
            continue
        outputs = data.get("outputs") or {}
        trace_decl = outputs.get("trace") if isinstance(outputs, dict) else None
        has_trace_decl = (
            isinstance(trace_decl, list)
            and any(isinstance(t, str) and "runs/" in t.lower() for t in trace_decl)
        )
        if has_trace_decl:
            continue
        # No declared trace — check for no-trace-justification.
        justification = no_trace_dir / f"{eou_id}.yml"
        if not justification.exists():
            problems.append(
                f"{spec_path}: active EOU `{eou_id}` declares no outputs.trace "
                f"and has no foundry/audits/no-trace/{eou_id}.yml. Either add "
                f"trace declaration (outputs.trace listing runs/{eou_id}/... path) "
                f"or write a no-trace-justification with named reviewer and "
                f"expires_at (ECP-0014)"
            )
    return problems


def validate_candidate_sets(root: Path) -> list[str]:
    """ECP-0013: candidate-set artifacts are the named output of every
    generating EOU. They live at foundry/self-evolution/candidate-sets/
    {set_id}.yml. Schema enforced by this walker.
    """
    problems: list[str] = []
    base = root / "foundry" / "self-evolution" / "candidate-sets"
    if not base.exists():
        return problems
    for path in sorted(base.glob("*.yml")):
        if path.name == ".gitkeep":
            continue
        data = load_yaml(path)
        if not isinstance(data, dict):
            problems.append(f"{path}: candidate-set must be a mapping")
            continue
        problems.extend(validate_required(path, data, CANDIDATE_SET_REQUIRED))
        target_class = data.get("target_class")
        if target_class and target_class not in CANDIDATE_SET_VALID_TARGET_CLASS:
            problems.append(
                f"{path}: target_class `{target_class}` not in "
                f"{sorted(CANDIDATE_SET_VALID_TARGET_CLASS)}"
            )
        status = data.get("audit_status")
        if status and status not in CANDIDATE_SET_VALID_STATUS:
            problems.append(
                f"{path}: audit_status `{status}` not in "
                f"{sorted(CANDIDATE_SET_VALID_STATUS)}"
            )
        # Each candidate must declare status:candidate and arguments_against.
        candidates = data.get("candidates")
        if isinstance(candidates, list):
            for idx, cand in enumerate(candidates):
                if not isinstance(cand, dict):
                    problems.append(f"{path}: candidates[{idx}] must be a mapping")
                    continue
                cand_id = cand.get("id", f"candidates[{idx}]")
                cand_status = cand.get("status")
                if cand_status and cand_status != "candidate":
                    problems.append(
                        f"{path}: candidate `{cand_id}` status=`{cand_status}`; "
                        f"only `candidate` is allowed in a candidate-set "
                        f"(generators may not emit other lifecycle states)"
                    )
                if empty(cand.get("arguments_against")):
                    problems.append(
                        f"{path}: candidate `{cand_id}` missing arguments_against "
                        f"(counter_generation requirement)"
                    )
        # Audit outcome must have all 7 keys (may be empty lists pre-audit).
        outcome = data.get("audit_outcome")
        if isinstance(outcome, dict):
            for key in CANDIDATE_SET_AUDIT_OUTCOME_KEYS:
                if key not in outcome:
                    problems.append(f"{path}: audit_outcome missing key `{key}`")
            # If audited: the set must explicitly say what survived AND what didn't.
            # Empty minimal_recommended_subset AND empty rejected = mute audit.
            if status == "audited":
                survived = outcome.get("minimal_recommended_subset") or []
                rejected = outcome.get("rejected") or []
                if not survived and not rejected:
                    problems.append(
                        f"{path}: audit_status=audited but both "
                        f"minimal_recommended_subset and rejected are empty; "
                        f"an audited set must record either what passed or "
                        f"explicit rejection (rejected_in_full status if all rejected)"
                    )
    return problems


def validate_captured_workflows(root: Path) -> list[str]:
    """ECP-0015: captured_workflow artifacts are the Stage 0 output —
    reference-grounded workflow capture plus the per-app constitutional
    layer (domain_values). They live at foundry/captured-workflows/{slug}.yml.
    Schema enforced by this walker.

    Validation checks (in order):
    - required top-level fields present
    - inputs.reference_set has all 5 role slots; each slot non-empty;
      each entry has {ref, why}
    - inputs.user_contributed_references has ≥1 per role slot (V2)
    - domain_values count in [3, 8]
    - domain_values priority is a total order (no ties, no gaps)
    - each domain_value has required subfields
    - each domain_value formulation matches "X over Y" pattern; Y not strawman
    - canonical_or_personal in enum; justification required when non-canonical
    - inclusion_test_passes has all 6 keys; ≥1 true
    - confidence has all 5 subfields; each in {low, medium, high}
    - human_approval has all 4 gates + approved_at; all non-null
    - id matches filename stem
    """
    problems: list[str] = []
    base = root / "foundry" / "captured-workflows"
    if not base.exists():
        return problems
    for path in sorted(base.glob("*.yml")):
        if path.name == ".gitkeep":
            continue
        data = load_yaml(path)
        if not isinstance(data, dict):
            problems.append(f"{path}: captured_workflow must be a mapping")
            continue
        problems.extend(validate_required(path, data, CAPTURED_WORKFLOW_REQUIRED))

        # id matches filename stem
        if data.get("id") and data.get("id") != path.stem:
            problems.append(
                f"{path}: captured_workflow id `{data.get('id')}` does not match "
                f"filename `{path.stem}`"
            )

        # schema_version is an int ≥ 1
        sv = data.get("schema_version")
        if sv is not None and (not isinstance(sv, int) or sv < 1):
            problems.append(
                f"{path}: schema_version must be an integer ≥ 1 (got {sv!r})"
            )

        # inputs structure
        inputs = data.get("inputs")
        if isinstance(inputs, dict):
            for key in CAPTURED_WORKFLOW_INPUTS_REQUIRED:
                if key not in inputs:
                    problems.append(f"{path}: inputs missing required key `{key}`")
            # reference_set role slots
            rs = inputs.get("reference_set")
            if isinstance(rs, dict):
                for slot in CAPTURED_WORKFLOW_ROLE_SLOTS:
                    entries = rs.get(slot)
                    if not entries:
                        problems.append(
                            f"{path}: reference_set.{slot} is empty; "
                            f"all 5 role slots required (outlier mandatory per V1 defense)"
                        )
                    elif isinstance(entries, list):
                        for idx, entry in enumerate(entries):
                            if isinstance(entry, dict):
                                if "ref" not in entry:
                                    problems.append(
                                        f"{path}: reference_set.{slot}[{idx}] missing `ref`"
                                    )
                                if "why" not in entry:
                                    problems.append(
                                        f"{path}: reference_set.{slot}[{idx}] missing `why` "
                                        f"(per-slot justification — V5 enforcement)"
                                    )
            # user_contributed_references per slot
            ucr = inputs.get("user_contributed_references")
            if isinstance(ucr, dict):
                for slot in CAPTURED_WORKFLOW_ROLE_SLOTS:
                    if not ucr.get(slot):
                        problems.append(
                            f"{path}: user_contributed_references.{slot} is empty; "
                            f"≥1 user-contributed reference required per slot "
                            f"(V2 anti-abdication enforcement)"
                        )

        # domain_values block
        dvs = data.get("domain_values")
        if isinstance(dvs, list):
            if len(dvs) < CAPTURED_WORKFLOW_DV_MIN:
                problems.append(
                    f"{path}: domain_values has {len(dvs)} entries; "
                    f"minimum {CAPTURED_WORKFLOW_DV_MIN} required"
                )
            if len(dvs) > CAPTURED_WORKFLOW_DV_MAX:
                problems.append(
                    f"{path}: domain_values has {len(dvs)} entries; "
                    f"maximum {CAPTURED_WORKFLOW_DV_MAX} permitted "
                    f"(mirrors foundry V1-V8 sizing)"
                )
            # Priority is a total order: exactly {1, ..., N}
            priorities = [dv.get("priority") for dv in dvs if isinstance(dv, dict)]
            if all(isinstance(p, int) for p in priorities):
                expected = set(range(1, len(dvs) + 1))
                actual = set(priorities)
                if actual != expected:
                    problems.append(
                        f"{path}: domain_values priorities must be exactly "
                        f"{{1, ..., {len(dvs)}}}; got {sorted(actual)}"
                    )
            # Per-value validation
            for idx, dv in enumerate(dvs):
                if not isinstance(dv, dict):
                    problems.append(f"{path}: domain_values[{idx}] must be a mapping")
                    continue
                dv_id = dv.get("id", f"domain_values[{idx}]")
                for key in CAPTURED_WORKFLOW_DV_REQUIRED:
                    if key not in dv:
                        problems.append(
                            f"{path}: domain_value `{dv_id}` missing required field `{key}`"
                        )
                # canonical_or_personal enum
                cop = dv.get("canonical_or_personal")
                if cop and cop not in CAPTURED_WORKFLOW_DV_CANONICAL_ENUM:
                    problems.append(
                        f"{path}: domain_value `{dv_id}` canonical_or_personal "
                        f"`{cop}` not in {sorted(CAPTURED_WORKFLOW_DV_CANONICAL_ENUM)}"
                    )
                if cop in {"user_personal", "user_diverges_from_canonical"}:
                    if not dv.get("justification_if_diverges"):
                        problems.append(
                            f"{path}: domain_value `{dv_id}` is `{cop}` but "
                            f"justification_if_diverges is missing"
                        )
                # Formulation: "X over Y" pattern, Y not strawman
                form = dv.get("formulation")
                if form:
                    if not CAPTURED_WORKFLOW_FORMULATION_PATTERN.match(form):
                        problems.append(
                            f"{path}: domain_value `{dv_id}` formulation `{form}` "
                            f"does not match required pattern `X over Y` "
                            f"(contested form per V1 defense)"
                        )
                    else:
                        # Extract Y for strawman check
                        m = re.match(r"^(.+?)\s+over\s+(.+)$", form, re.IGNORECASE)
                        if m:
                            y_term = m.group(2).strip().lower().rstrip(".")
                            if y_term in CAPTURED_WORKFLOW_STRAWMAN_LIST:
                                problems.append(
                                    f"{path}: domain_value `{dv_id}` formulation Y term "
                                    f"`{y_term}` is in strawman list — pick a real "
                                    f"opposing value"
                                )
                # inclusion_test_passes: all 6 keys present; ≥1 true
                itp = dv.get("inclusion_test_passes")
                if isinstance(itp, dict):
                    for key in CAPTURED_WORKFLOW_INCLUSION_TEST_KEYS:
                        if key not in itp:
                            problems.append(
                                f"{path}: domain_value `{dv_id}` inclusion_test_passes "
                                f"missing key `{key}`"
                            )
                    truthy = [k for k in CAPTURED_WORKFLOW_INCLUSION_TEST_KEYS
                              if itp.get(k) is True]
                    if not truthy:
                        problems.append(
                            f"{path}: domain_value `{dv_id}` inclusion_test_passes "
                            f"has no true entries; ≥1 required (mirrors 06-values-"
                            f"over-rules.md inclusion test)"
                        )

        # confidence: all 5 subfields; each in {low, medium, high}
        conf = data.get("confidence")
        if isinstance(conf, dict):
            for key in CAPTURED_WORKFLOW_CONFIDENCE_KEYS:
                if key not in conf:
                    problems.append(f"{path}: confidence missing key `{key}`")
                else:
                    val = conf.get(key)
                    if val not in CAPTURED_WORKFLOW_CONFIDENCE_ENUM:
                        problems.append(
                            f"{path}: confidence.{key} = `{val}` not in "
                            f"{sorted(CAPTURED_WORKFLOW_CONFIDENCE_ENUM)}"
                        )

        # human_approval: all 4 gates + approved_at; all non-null
        ha = data.get("human_approval")
        if isinstance(ha, dict):
            for gate in CAPTURED_WORKFLOW_APPROVAL_GATES:
                if not ha.get(gate):
                    problems.append(
                        f"{path}: human_approval.{gate} is missing or null "
                        f"(V2 multi-gate enforcement: all 4 gates + approved_at required)"
                    )

    return problems


def _load_rule_96_exemptions(plugin_root: Path) -> set[str]:
    """Read rule_96_exempt_target_objects from engine/governance.yml.
    Returns an empty set if the field is absent (engine merge model
    permits apps to extend the engine baseline)."""
    gov_path = plugin_root / "engine" / "governance.yml"
    if not gov_path.exists():
        return set()
    data = load_yaml(gov_path) or {}
    exempt = data.get("rule_96_exempt_target_objects") or []
    return set(exempt) if isinstance(exempt, list) else set()


def validate_domain_values_consumption(root: Path, plugin_root: Path) -> list[str]:
    """ECP-0017 / Rule 96: when an approved captured_workflow exists,
    EOU specs MUST operationalize at least one top-three priority
    domain_value in success_criteria.must_pass.

    Detection — for each spec in foundry/eous/ and foundry/meta-eous/,
    look up the parent app's captured_workflows; if any captured_workflow
    has human_approval complete, scan the spec's success_criteria.must_pass
    for references to top-three domain_value ids. If no reference found
    AND the spec is at lifecycle_stage pilot or higher AND target_object
    is not exempt, emit a Rule 96 violation.

    Exemptions:
    - No captured_workflow exists or none is approved (rule does not apply)
    - target_object in rule_96_exempt_target_objects (governance.yml)
    - lifecycle_stage in {candidate, draft} (rule applies only at pilot+)
    """
    problems: list[str] = []
    cw_dir = root / "foundry" / "captured-workflows"
    if not cw_dir.exists():
        return problems

    # Collect top-three domain_value ids from any approved captured_workflow
    top_three_ids: set[str] = set()
    for cw_path in sorted(cw_dir.glob("*.yml")):
        if cw_path.name == ".gitkeep":
            continue
        cw = load_yaml(cw_path)
        if not isinstance(cw, dict):
            continue
        # Check approval is complete (all 4 gates + approved_at non-null)
        ha = cw.get("human_approval") or {}
        if not all(ha.get(g) for g in CAPTURED_WORKFLOW_APPROVAL_GATES):
            continue
        dvs = cw.get("domain_values") or []
        for dv in dvs:
            if not isinstance(dv, dict):
                continue
            pri = dv.get("priority")
            if isinstance(pri, int) and pri <= 3 and dv.get("id"):
                top_three_ids.add(dv["id"])

    if not top_three_ids:
        # No approved captured_workflow with top-three values; rule does not apply
        return problems

    exempt_targets = _load_rule_96_exemptions(plugin_root)
    rule_96_active_stages = {"pilot", "active", "monitored", "stable"}

    # Walk EOU specs
    for spec_dir in ("eous", "meta-eous"):
        # meta-eous lives under the plugin's engine/, not under the app foundry
        if spec_dir == "meta-eous":
            base = plugin_root / "engine" / "meta-eous"
        else:
            base = root / "foundry" / spec_dir
        if not base.exists():
            continue
        for spec_path in sorted(base.glob("*.yml")):
            spec = load_yaml(spec_path)
            if not isinstance(spec, dict):
                continue
            classification = spec.get("classification") or {}
            stage = classification.get("lifecycle_stage")
            if stage not in rule_96_active_stages:
                continue
            target_object = classification.get("target_object")
            if target_object in exempt_targets:
                continue
            sc = spec.get("success_criteria") or {}
            must_pass = sc.get("must_pass") or []
            # Stringify and search for any top-three id
            must_pass_text = "\n".join(str(x) for x in must_pass) if isinstance(must_pass, list) else str(must_pass)
            if not any(dv_id in must_pass_text for dv_id in top_three_ids):
                problems.append(
                    f"{spec_path}: Rule 96 violation — spec at lifecycle_stage "
                    f"`{stage}` in app with approved captured_workflow has no "
                    f"reference to any top-three domain_value "
                    f"({sorted(top_three_ids)}) in success_criteria.must_pass; "
                    f"target_object `{target_object}` is not exempt"
                )

    return problems


def validate_value_invocation_discipline(root: Path) -> list[str]:
    """ECP-0020 / Rule 97: extends ECP-0018's structural value_invocations
    validation with id-resolution against the captured_workflow.

    For each run trace under foundry/runs/ that contains value_invocations,
    verify each invocation's domain_value_id resolves to a current
    domain_value.id in the app's approved captured_workflow. Mismatched
    ids are F17_VALUE_HALLUCINATION_FAILURE violations.

    This is the declarative subset of Rule 97 enforcement. The
    judgment-heavy checks (F14 silent judgment, F15 priority violations,
    F16 drift, counterfactual-swap audit) live in the $audit-judgment
    skill, not the validator."""
    problems: list[str] = []
    runs_dir = root / "foundry" / "runs"
    cw_dir = root / "foundry" / "captured-workflows"
    if not runs_dir.exists() or not cw_dir.exists():
        return problems

    # Collect all domain_value ids from approved captured_workflows
    valid_ids: set[str] = set()
    for cw_path in cw_dir.glob("*.yml"):
        if cw_path.name == ".gitkeep":
            continue
        cw = load_yaml(cw_path)
        if not isinstance(cw, dict):
            continue
        ha = cw.get("human_approval") or {}
        if not all(ha.get(g) for g in CAPTURED_WORKFLOW_APPROVAL_GATES):
            continue
        for dv in cw.get("domain_values") or []:
            if isinstance(dv, dict) and dv.get("id"):
                valid_ids.add(dv["id"])

    if not valid_ids:
        # No approved captured_workflow with values; rule 97 cannot apply
        return problems

    for trace_path in runs_dir.rglob("*.yml"):
        if trace_path.name == ".gitkeep":
            continue
        trace = load_yaml(trace_path)
        if not isinstance(trace, dict):
            continue
        invocations = trace.get("value_invocations") or []
        if not isinstance(invocations, list):
            continue
        for idx, inv in enumerate(invocations):
            if not isinstance(inv, dict):
                continue
            inv_id = inv.get("invocation_id", f"value_invocations[{idx}]")
            dv_id = inv.get("domain_value_id")
            if dv_id and dv_id not in valid_ids:
                problems.append(
                    f"{trace_path}: F17_VALUE_HALLUCINATION_FAILURE — invocation "
                    f"`{inv_id}` references domain_value_id `{dv_id}` which "
                    f"does not resolve in any approved captured_workflow "
                    f"(known ids: {sorted(valid_ids)})"
                )
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
    problems.extend(validate_run_traces(root))
    problems.extend(validate_no_trace_justifications(root))
    problems.extend(validate_active_trace_obligation(root, app_eou_paths))
    problems.extend(validate_candidate_sets(root))
    problems.extend(validate_captured_workflows(root))   # ECP-0015
    problems.extend(validate_domain_values_consumption(root, plugin_root))  # ECP-0017 / Rule 96
    problems.extend(validate_value_invocation_discipline(root))            # ECP-0020 / Rule 97
    problems.extend(validate_dependency_dag(root))
    problems.extend(validate_maturity_evidence(root))
    problems.extend(validate_activation_evidence(root))

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
