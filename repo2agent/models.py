from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FileNode:
    path: str
    is_dir: bool
    children: list[FileNode] | None = None


@dataclass
class Interface:
    name: str
    kind: str  # "function", "class", "route", "cli_command"
    file_path: str
    signature: str
    docstring: str | None = None


@dataclass
class ProjectMeta:
    name: str
    description: str
    languages: list[str]
    frameworks: list[str]
    dependencies: dict[str, list[str]] = field(default_factory=lambda: {"prod": [], "dev": []})
    scripts: dict[str, str] = field(default_factory=dict)
    structure: FileNode = field(default_factory=lambda: FileNode(path=".", is_dir=True, children=[]))
    readme_excerpt: str = ""
    entry_points: list[str] = field(default_factory=list)
    interfaces: list[Interface] = field(default_factory=list)
    has_tests: bool = False
    has_docs: bool = False
    has_ci: bool = False
