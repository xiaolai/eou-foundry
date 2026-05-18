#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import shutil
from _common import find_repo_root


def clean(root: Path) -> int:
    removed = 0
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
        removed += 1
    for pyc in root.rglob("*.pyc"):
        try:
            pyc.unlink()
            removed += 1
        except FileNotFoundError:
            pass
    return removed


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Remove __pycache__/ and *.pyc under the repo root. "
                    "By default refuses paths outside the repo root.",
    )
    ap.add_argument("path", nargs="?", default=None,
                    help="Path to clean (default: repo root)")
    ap.add_argument("--allow-outside-repo", action="store_true",
                    help="Allow cleaning a path that is not inside the repo root.")
    args = ap.parse_args()
    from _common import cli_error
    try:
        repo_root = find_repo_root()
        target = Path(args.path).resolve() if args.path else repo_root
    except RuntimeError as e:
        cli_error(str(e))
    # Refuse to recursively delete bytecode anywhere outside the repo unless
    # the user explicitly opts in. Without this, an absentminded
    # `clean_generated.py /` would rm -rf __pycache__/ across the home dir.
    if not args.allow_outside_repo:
        try:
            target.relative_to(repo_root)
        except ValueError:
            cli_error(
                f"refusing to clean a path outside the repo root: {target}. "
                f"Pass --allow-outside-repo to override."
            )
    print(f"removed {clean(target)} generated Python artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
