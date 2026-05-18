from __future__ import annotations

from pathlib import Path
from typing import Any
import re
import sys

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


PLACEHOLDER_PATTERNS = [
    re.compile(r"\bTBD\b"),
    re.compile(r"\[MISSING[^\]]*\]"),
    re.compile(r"See book/fair-clues\.yml"),
    re.compile(r"A concrete moment around the assignment makes the old reading feel"),
    re.compile(r"Something about the artifact, the learner, or the process does not fit"),
    re.compile(r"The chapter reveals one part of learning residue"),
]


def require_yaml():
    if yaml is None:
        print("PyYAML is required. Install with: pip install PyYAML", file=sys.stderr)
        raise SystemExit(2)
    return yaml


def load_yaml(path: Path) -> Any:
    """Load YAML expecting a mapping at the top level.

    Returns the parsed mapping (or {} for empty/None files). Raises ValueError
    with a clear message if the file's top-level value is not a mapping, so
    callers can do data.get(...) without first checking isinstance(data, dict).
    """
    y = require_yaml()
    with path.open("r", encoding="utf-8") as f:
        data = y.safe_load(f)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(
            f"{path}: expected a mapping at the top level, got {type(data).__name__}"
        )
    return data


def dump_yaml(path: Path, data: Any) -> None:
    y = require_yaml()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        y.safe_dump(data, f, allow_unicode=True, sort_keys=False)


def find_repo_root(start: Path | None = None) -> Path:
    start = Path.cwd() if start is None else Path(start)
    start = start.resolve()
    candidates = [start]
    if start.is_file():
        candidates = [start.parent]
    for p in [candidates[0], *candidates[0].parents]:
        if (p / "foundry" / "constitution.yml").exists():
            return p
    raise RuntimeError("Could not locate repository root (no foundry/constitution.yml found)")


def books_dir(root: Path | None = None) -> Path:
    return (root or find_repo_root()) / "applications" / "book-workshop" / "books"


def resolve_book(path_or_id: str | Path) -> Path:
    p = Path(path_or_id)
    if p.exists():
        return p.resolve()
    root = find_repo_root()
    book_id = Path(str(path_or_id)).name
    candidate = books_dir(root) / book_id
    if candidate.exists():
        return candidate.resolve()
    raise FileNotFoundError(f"Book not found: {path_or_id}")


def slug(s: str) -> str:
    out = []
    prev_dash = False
    for ch in s.lower():
        if ch.isalnum():
            out.append(ch)
            prev_dash = False
        elif not prev_dash:
            out.append('-')
            prev_dash = True
    return ''.join(out).strip('-') or 'untitled'


import re as _re
_SAFE_ID_RE = _re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def safe_id(value: str, *, kind: str = "id") -> str:
    """Return value if it is a path-safe slug; else raise ValueError.

    Rejects empty strings, path separators (`/`, `\\`), parent-directory
    segments (`..`), absolute-style leading dots, and any character outside
    [a-z0-9._-]. Used to prevent path traversal when an external id (chapter
    id, device id, ...) is interpolated into a filesystem path.
    """
    if not isinstance(value, str) or not value:
        raise ValueError(f"invalid {kind}: empty or non-string")
    if "/" in value or "\\" in value or value.startswith("."):
        raise ValueError(f"invalid {kind}: contains path separator or starts with '.'")
    if not _SAFE_ID_RE.match(value):
        raise ValueError(
            f"invalid {kind}: {value!r} must match {_SAFE_ID_RE.pattern}"
        )
    return value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def cli_error(message: str, code: int = 2) -> "NoReturn":
    """Exit a CLI script with a one-line error message — no traceback."""
    import sys
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_mapping(path: Path) -> tuple[dict | None, str | None]:
    """Load a YAML file expected to contain a mapping at the top level.

    Returns (data, None) if the file is a valid mapping, otherwise
    (None, error_message). Callers should treat the error as a validation
    problem rather than letting the validator crash on a .get() call.
    """
    try:
        data = load_yaml(path)
    except Exception as exc:
        return None, f"{path}: invalid YAML: {exc}"
    if not isinstance(data, dict):
        return None, f"{path}: top-level YAML must be a mapping (got {type(data).__name__})"
    return data, None


def has_placeholders(text: str) -> list[str]:
    found: list[str] = []
    for pat in PLACEHOLDER_PATTERNS:
        if pat.search(text):
            found.append(pat.pattern)
    return found


def extract_frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return "__UNTERMINATED__"
    return text[4:end]


def validate_markdown_frontmatter(path: Path, required: list[str] | None = None) -> list[str]:
    problems: list[str] = []
    text = read_text(path)
    fm = extract_frontmatter(text)
    if fm is None:
        problems.append(f"{path}: missing YAML frontmatter")
        return problems
    if fm == "__UNTERMINATED__":
        problems.append(f"{path}: unterminated YAML frontmatter")
        return problems
    try:
        data = require_yaml().safe_load(fm) or {}
    except Exception as exc:
        problems.append(f"{path}: invalid YAML frontmatter: {exc}")
        return problems
    if not isinstance(data, dict):
        problems.append(f"{path}: YAML frontmatter must be a mapping")
        return problems
    for key in required or []:
        if not data.get(key):
            problems.append(f"{path}: frontmatter missing `{key}`")
    return problems
