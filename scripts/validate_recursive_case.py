#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
from _common import find_repo_root, load_yaml

REQUIRED_FILES = [
    "README.md",
    "case-protocol.yml",
    "book-production-constitution.yml",
    "candidate-eou-set.v0.1.yml",
    "candidate-set-audit.v0.1.yml",
    "control-comparison.yml",
    "economic-ledger.yml",
    "portfolio-audit.yml",
    "process-evidence-distillation-rules.yml",
    "negative-evidence.md",
    "non-book-transfer-case-investment-research.yml",
    "human-decision-record.example.yml",
]

DANGEROUS_GENERATED_IDS = {
    "auto-approve-chapter",
    "generate-all-prose",
    "publish-without-human-review",
    "recursive-proof-generator",
}


def empty(value) -> bool:
    return value in (None, "", [], {})


def require_keys(path: Path, data: dict, keys: list[str], prefix: str = "") -> list[str]:
    problems: list[str] = []
    for key in keys:
        if empty(data.get(key)):
            problems.append(f"{path}: missing or empty `{prefix + key}`")
    return problems


def validate_case(root: Path) -> list[str]:
    problems: list[str] = []
    case = root / "case-studies" / "recursive-book-production"
    if not case.exists():
        return ["case-studies/recursive-book-production missing"]

    for rel in REQUIRED_FILES:
        if not (case / rel).exists():
            problems.append(f"recursive case missing required file: {rel}")

    if problems:
        return problems

    protocol_path = case / "case-protocol.yml"
    protocol = load_yaml(protocol_path).get("case_protocol") or {}
    problems.extend(require_keys(protocol_path, protocol, ["question", "permitted_claims", "non_claims", "success_criteria", "failure_criteria", "artifacts_to_collect", "evaluation_language"]))
    non_claims = "\n".join(protocol.get("non_claims") or []).lower()
    if "does not prove" not in non_claims:
        problems.append(f"{protocol_path}: non_claims must explicitly reject proof framing")
    allowed = set((protocol.get("evaluation_language") or {}).get("allowed") or [])
    forbidden = set((protocol.get("evaluation_language") or {}).get("forbidden") or [])
    for word in ["demonstrates", "provides evidence"]:
        if word not in allowed:
            problems.append(f"{protocol_path}: evaluation_language.allowed should include `{word}`")
    for word in ["proves universally", "eliminates human judgment"]:
        if word not in forbidden:
            problems.append(f"{protocol_path}: evaluation_language.forbidden should include `{word}`")

    constitution_path = case / "book-production-constitution.yml"
    constitution = load_yaml(constitution_path).get("book_production_constitution") or {}
    problems.extend(require_keys(constitution_path, constitution, ["invariants", "authority_boundaries", "required_human_decision_records", "reader_facing_constraints"]))
    invariants = "\n".join(constitution.get("invariants") or [])
    for phrase in ["No generated chapter may approve itself", "Human owner approves final thesis", "The recursive case must not dominate"]:
        if phrase not in invariants:
            problems.append(f"{constitution_path}: invariants should include `{phrase}`")

    set_path = case / "candidate-eou-set.v0.1.yml"
    candidate_set = load_yaml(set_path).get("candidate_eou_set") or {}
    problems.extend(require_keys(set_path, candidate_set, ["recommended_minimal_set", "candidates", "optional_candidates", "rejected_candidates", "set_level_risks", "required_next_step"]))
    candidates = candidate_set.get("candidates") or []
    if not isinstance(candidates, list) or len(candidates) < 5:
        problems.append(f"{set_path}: expected at least 5 candidates")
    ids = []
    for idx, cand in enumerate(candidates):
        if not isinstance(cand, dict):
            problems.append(f"{set_path}: candidate {idx} must be a mapping")
            continue
        ids.append(cand.get("id"))
        problems.extend(require_keys(set_path, cand, ["id", "classification", "purpose", "distinct_success_criterion", "operational_value", "arguments_against", "activation_requirements", "status"], f"candidates[{idx}]."))
        if cand.get("status") != "candidate":
            problems.append(f"{set_path}: generated candidate `{cand.get('id')}` must have status candidate")
        c = cand.get("classification") or {}
        if c.get("authority_level") in {"mutate_active", "publish"}:
            problems.append(f"{set_path}: candidate `{cand.get('id')}` has unsafe authority {c.get('authority_level')}")
        if c.get("authority_level") == "approve" and c.get("automation_mode") != "human_executed":
            problems.append(f"{set_path}: approve authority must be human_executed for `{cand.get('id')}`")
    minimal = set(candidate_set.get("recommended_minimal_set") or [])
    if not minimal:
        problems.append(f"{set_path}: recommended_minimal_set cannot be empty")
    if not minimal.issubset(set(ids)):
        problems.append(f"{set_path}: recommended_minimal_set references unknown candidates: {sorted(minimal - set(ids))}")
    rejected = candidate_set.get("rejected_candidates") or []
    rejected_ids = {r.get("id") for r in rejected if isinstance(r, dict)}
    if not DANGEROUS_GENERATED_IDS.issubset(rejected_ids):
        problems.append(f"{set_path}: rejected_candidates must include {sorted(DANGEROUS_GENERATED_IDS)}")

    audit_path = case / "candidate-set-audit.v0.1.yml"
    audit = load_yaml(audit_path).get("candidate_set_audit") or {}
    problems.extend(require_keys(audit_path, audit, ["verdict", "findings", "candidate_recommendations", "required_case_artifacts", "approval_status"]))
    recs = audit.get("candidate_recommendations") or {}
    for key in ["keep", "merge", "defer", "reject"]:
        if empty(recs.get(key)):
            problems.append(f"{audit_path}: candidate_recommendations.{key} must be non-empty")
    approval = audit.get("approval_status") or {}
    if approval.get("approved_for_active_use") is not False:
        problems.append(f"{audit_path}: candidate set must not be approved for active use at v0.1")

    control_path = case / "control-comparison.yml"
    controls = (load_yaml(control_path).get("control_comparison") or {}).get("controls") or []
    control_ids = {c.get("id") for c in controls if isinstance(c, dict)}
    for cid in ["prompt_only_book_production", "checklist_only_book_production", "foundry_governed_book_production"]:
        if cid not in control_ids:
            problems.append(f"{control_path}: missing control `{cid}`")

    economics_path = case / "economic-ledger.yml"
    economics = load_yaml(economics_path).get("economic_ledger") or {}
    problems.extend(require_keys(economics_path, economics, ["costs_to_track", "benefits_to_track", "economic_questions", "current_status"]))

    portfolio_path = case / "portfolio-audit.yml"
    portfolio = load_yaml(portfolio_path).get("portfolio_audit") or {}
    problems.extend(require_keys(portfolio_path, portfolio, ["portfolio_health_questions", "current_counts", "preliminary_findings", "health_verdict"]))

    distill_path = case / "process-evidence-distillation-rules.yml"
    distill = load_yaml(distill_path).get("process_evidence_distillation_rules") or {}
    problems.extend(require_keys(distill_path, distill, ["must_include", "must_avoid", "evidence_selection_tests", "recommended_reader_sequence"]))
    for required in ["one_real_or_representative_failure", "one_rejected_candidate", "one_human_decision_record", "one_limitation_or_negative_evidence_item"]:
        if required not in (distill.get("must_include") or []):
            problems.append(f"{distill_path}: must_include should include `{required}`")

    decision_path = case / "human-decision-record.example.yml"
    decision = load_yaml(decision_path).get("human_decision_record") or {}
    problems.extend(require_keys(decision_path, decision, ["decision", "alternatives_considered", "selected", "reason", "evidence_used", "risk_accepted", "owner", "non_delegable", "approval_status"]))
    if decision.get("non_delegable") is not True:
        problems.append(f"{decision_path}: example decision must be non_delegable")

    transfer_path = case / "non-book-transfer-case-investment-research.yml"
    transfer = load_yaml(transfer_path).get("transfer_case") or {}
    problems.extend(require_keys(transfer_path, transfer, ["domain", "high_stakes_constraints", "minimal_candidate_set", "transfer_lesson"]))
    constraints = "\n".join(transfer.get("high_stakes_constraints") or []).lower()
    if "may not recommend trades" not in constraints or "human owner" not in constraints:
        problems.append(f"{transfer_path}: high_stakes_constraints must preserve human investment responsibility")

    incident_files = list((case / "incidents").glob("*.yml"))
    regression_files = list((case / "regression").glob("*.yml"))
    ecp_files = list((case / "ecp").glob("*.yml"))
    if not incident_files:
        problems.append("recursive case must include at least one incident example")
    if not regression_files:
        problems.append("recursive case must include at least one regression case example")
    if not ecp_files:
        problems.append("recursive case must include at least one ECP example")

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
        problems = validate_case(root)
        if problems:
            print("Recursive case validation failed:")
            for p in problems:
                print(f"- {p}")
            return 1
        print("OK: recursive-book-production case")
        return 0


    except (FileNotFoundError, ValueError, RuntimeError) as _e:
        _cli_error(str(_e))

if __name__ == "__main__":
    raise SystemExit(main())
