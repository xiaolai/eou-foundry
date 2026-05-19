#!/usr/bin/env python3
"""Helper for EOU implementations to emit compliant run traces.

Usage:
    from runs import record_run

    record_run(
        eou_id="compile-chapter",
        eou_version="0.2.0",
        status="success",
        executor_identity="xiaolai",
        inputs={...},
        outputs={...},
        ...
    )

The helper writes a run trace at foundry/runs/{eou_id}/{run_id}.yml that
passes run-trace.schema.v3 validation. EOU implementations call this at
the end of each run; long-lived EOUs may write partial traces during
execution and finalize at the end.

Per ECP-0007 (plugin v0.6.0)."""

from __future__ import annotations

import datetime as _dt
import os
import uuid
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    raise SystemExit("error: PyYAML required for run-trace recording")


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _find_foundry_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    while p != p.parent:
        if (p / "foundry" / "constitution.yml").exists():
            return p
        p = p.parent
    raise RuntimeError("foundry root not found")


def record_run(
    *,
    eou_id: str,
    eou_version: str,
    status: str,
    executor_identity: str,
    inputs: dict[str, Any] | None = None,
    context_loaded: list[str] | None = None,
    steps_completed: list[dict[str, Any]] | None = None,
    warnings: list[str] | None = None,
    outputs: dict[str, Any] | None = None,
    validation: dict[str, Any] | None = None,
    human_approval: dict[str, Any] | None = None,
    started_at: str | None = None,
    ended_at: str | None = None,
    run_id: str | None = None,
    foundry_root: Path | None = None,
    extras: dict[str, Any] | None = None,
) -> Path:
    """Emit a run trace YAML and return its path.

    Required fields all have keyword-only parameters; the function fills
    in defaults for timestamps and run_id if absent. Pass `extras` for
    optional fields (decisions_taken, success_criteria_results,
    escalations_triggered, inputs_hash, outputs_summary,
    validator_invocations).
    """
    if status not in {"success", "partial", "failed", "aborted"}:
        raise ValueError(f"invalid status: {status}")
    root = foundry_root or _find_foundry_root()

    started = started_at or _now_iso()
    ended = ended_at or started
    rid = run_id or _now_iso().replace(":", "").replace("-", "") + "-" + uuid.uuid4().hex[:8]

    trace = {
        "run_id": rid,
        "eou_id": eou_id,
        "eou_version": eou_version,
        "status": status,
        "started_at": started,
        "ended_at": ended,
        "executor_identity": executor_identity,
        "inputs": inputs or {},
        "context_loaded": context_loaded or [],
        "steps_completed": steps_completed or [],
        "warnings": warnings or [],
        "outputs": outputs or {},
        "validation": validation or {},
        "human_approval": human_approval,
    }
    if extras:
        trace.update(extras)

    target = root / "foundry" / "runs" / eou_id / f"{rid}.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(trace, sort_keys=False, allow_unicode=True))
    return target
