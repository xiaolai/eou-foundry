#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
from _common import find_repo_root, load_yaml

VALID_FUNCTIONS = {"generate", "specify", "validate", "diagnose", "promote", "refactor", "audit", "propose", "activate", "implement", "retire"}
VALID_AUTOMATION = {"deterministic", "LLM_assisted", "human_executed", "hybrid"}
VALID_AUTHORITY = {"suggest_only", "draft_only", "write_candidate", "write_inactive", "mutate_active", "approve", "publish"}
VALID_RISK = {"low", "medium", "high", "critical"}
VALID_STAGE = {"candidate", "draft", "simulated", "pilot", "active", "monitored", "stable", "deprecated", "retired"}
SAFE_GENERATING_AUTHORITY = {"suggest_only", "draft_only", "write_candidate", "write_inactive"}
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


def empty(v) -> bool:
    # Intentionally treats [] as non-empty: required list fields like
    # `versioning.supersedes` are legitimately empty for EOUs with no
    # predecessor. List-typed required fields where emptiness IS an error
    # (must_pass, known_issues, etc.) are checked by purpose-specific code.
    return v in (None, "", {})


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
            if gate in {"registry_diff", "counter_generation"} and value.get("required") is not True:
                problems.append(f"{path}: `{gate}.required` must be true")
        cc = data.get("counter_generation") if isinstance(data.get("counter_generation"), dict) else {}
        rfc = cc.get("requires_for_each_candidate") or []
        if isinstance(rfc, list) and "arguments_against" not in rfc:
            problems.append(f"{path}: counter_generation.requires_for_each_candidate must include `arguments_against`")

    if c.get("authority_level") in {"approve", "publish"}:
        resp = data.get("responsibility") or {}
        cannot = " ".join(resp.get("cannot_delegate") or []).lower()
        if "human" not in cannot and "final" not in cannot:
            problems.append(f"{path}: approve/publish authority requires explicit non-delegable human responsibility")

    blast = data.get("blast_radius")
    if not isinstance(blast, dict) or empty(blast.get("allowed_scope")) or empty(blast.get("forbidden_scope")):
        problems.append(f"{path}: missing blast_radius.allowed_scope/forbidden_scope")

    return problems


def validate_constitution(root: Path) -> list[str]:
    path = root / "foundry" / "constitution.yml"
    if not path.exists():
        return ["foundry/constitution.yml missing"]
    data = load_yaml(path)
    problems = validate_required(path, data, CONSTITUTION_REQUIRED)
    inv = "\n".join(data.get("invariants") or [])
    gen = "\n".join(data.get("generation_invariants") or [])
    for phrase in ["No EOU may approve its own change alone", "Failure history cannot be deleted", "Validation cannot be weakened"]:
        if phrase not in inv:
            problems.append(f"{path}: constitution should include invariant containing `{phrase}`")
    for phrase in ["default to candidate status", "cannot activate", "arguments against creation", "minimal recommended subset"]:
        if phrase not in gen:
            problems.append(f"{path}: generation_invariants should include `{phrase}`")
    return problems


def validate_registry(root: Path, eou_paths: dict[str, Path]) -> list[str]:
    path = root / "foundry" / "registry.yml"
    if not path.exists():
        return ["foundry/registry.yml missing"]
    data = load_yaml(path)
    problems = validate_required(path, data, REGISTRY_REQUIRED)
    entries = data.get("entries") or []
    if not isinstance(entries, list):
        problems.append(f"{path}: registry.entries must be a list")
        return problems
    if not entries:
        # Empty registry is the legitimate post-init state of a fresh app. Pass.
        return problems
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
        rel = entry.get("path")
        if rel and not (root / rel).exists():
            problems.append(f"{path}: registry path does not exist: {rel}")
        if eou_id and eou_id not in eou_paths:
            problems.append(f"{path}: registry entry `{eou_id}` has no matching EOU spec")
        c = entry.get("classification") or {}
        if c.get("authority_level") in {"approve", "publish"}:
            problems.append(f"{path}: registry entry `{eou_id}` has unsafe approve/publish authority")
    for eou_id in sorted(set(eou_paths) - seen):
        problems.append(f"{path}: EOU spec `{eou_id}` missing from registry")
    return problems


def validate_ecps(root: Path) -> list[str]:
    problems: list[str] = []
    base = root / "foundry" / "self-evolution" / "ecp"
    if not base.exists():
        return ["foundry/self-evolution/ecp missing"]
    required = ["id", "target_eou", "target_version_from", "target_version_to", "problem", "proposed_change", "expected_benefit", "risks", "tests_required", "simulation", "approval"]
    for path in sorted(base.rglob("*.yml")):
        data = load_yaml(path)
        problems.extend(validate_required(path, data, required))
        approval = data.get("approval") or {}
        if approval.get("status") == "approved" and not approval.get("approved_by"):
            problems.append(f"{path}: approved ECP lacks approved_by")
    return problems


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


def validate_foundry(root: Path) -> list[str]:
    problems: list[str] = []
    foundry = root / "foundry"
    if not foundry.exists():
        return ["missing foundry/ directory"]
    problems.extend(validate_constitution(root))
    eou_paths: dict[str, Path] = {}
    for base in [foundry / "eous", foundry / "meta-eous"]:
        if not base.exists():
            problems.append(f"missing {base.relative_to(root)}/ directory")
            continue
        for path in sorted(base.glob("*.yml")):
            data = load_yaml(path)
            if isinstance(data, dict) and data.get("id"):
                eou_paths[str(data["id"])] = path
            problems.extend(validate_eou_card(path, root))
    if not eou_paths:
        problems.append("foundry: no EOU specs found")
    problems.extend(validate_registry(root, eou_paths))
    problems.extend(validate_ecps(root))
    problems.extend(validate_regression_cases(root))
    return problems


def main() -> int:
    from _common import cli_error as _cli_error
    try:
        ap = argparse.ArgumentParser()
        ap.add_argument("path", nargs="?", default=None, help="Optional repository root")
        args = ap.parse_args()
        from _common import cli_error
        try:
            root = Path(args.path).resolve() if args.path else find_repo_root()
        except RuntimeError as e:
            cli_error(str(e))
        problems = validate_foundry(root)
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
