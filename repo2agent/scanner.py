from __future__ import annotations

from pathlib import Path

import pathspec

from repo2agent.models import FileNode

BUILT_IN_IGNORES = {
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    "target",
    ".git",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}

MAX_DEPTH = 8
MAX_FILES = 5000


def scan_directory(
    path: Path,
    *,
    max_depth: int = MAX_DEPTH,
    max_files: int = MAX_FILES,
) -> FileNode:
    path = path.resolve()
    gitignore_spec = _load_gitignore(path)
    file_count = 0

    def _walk(current: Path, depth: int) -> FileNode:
        nonlocal file_count
        rel = current.relative_to(path)
        is_dir = current.is_dir()

        rel_str = rel.as_posix()
        if not is_dir:
            file_count += 1
            return FileNode(path=rel_str, is_dir=False, children=None)

        children: list[FileNode] = []
        if depth < max_depth and file_count < max_files:
            try:
                entries = sorted(current.iterdir(), key=lambda e: (not e.is_dir(), e.name))
            except PermissionError:
                return FileNode(path=rel_str, is_dir=True, children=[])

            for entry in entries:
                rel_entry = entry.relative_to(path).as_posix()

                if entry.name in BUILT_IN_IGNORES:
                    continue

                if gitignore_spec and gitignore_spec.match_file(rel_entry):
                    continue

                if entry.is_dir() and gitignore_spec and gitignore_spec.match_file(rel_entry + "/"):
                    continue

                children.append(_walk(entry, depth + 1))

        return FileNode(path=rel_str, is_dir=True, children=children)

    return _walk(path, 0)


def _load_gitignore(project_path: Path) -> pathspec.PathSpec | None:
    gitignore_path = project_path / ".gitignore"
    if not gitignore_path.exists():
        return None
    try:
        lines = gitignore_path.read_text(encoding="utf-8").splitlines()
        return pathspec.PathSpec.from_lines("gitignore", lines)
    except (OSError, UnicodeDecodeError):
        return None
