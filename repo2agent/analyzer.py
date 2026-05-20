from __future__ import annotations

from pathlib import Path

from repo2agent.config_parser import parse_configs
from repo2agent.deep_scanner import deep_scan
from repo2agent.llm_polisher import polish_meta
from repo2agent.models import ProjectMeta
from repo2agent.scanner import scan_directory

README_MAX_LINES = 100


def analyze_project(project_path: Path, *, deep: bool = False, llm: bool = False) -> ProjectMeta:
    project_path = project_path.resolve()

    structure = scan_directory(project_path)
    config = parse_configs(project_path)
    readme_excerpt = _read_readme(project_path)
    entry_points = _detect_entry_points(project_path, config)

    interfaces = []
    if deep:
        interfaces = deep_scan(project_path, config["languages"])

    meta = ProjectMeta(
        name=config["name"] or project_path.name,
        description=config["description"] or "",
        languages=config["languages"],
        frameworks=config["frameworks"],
        dependencies=config["dependencies"],
        scripts=config["scripts"],
        structure=structure,
        readme_excerpt=readme_excerpt,
        entry_points=entry_points,
        interfaces=interfaces,
        has_tests=config["has_tests"],
        has_docs=config["has_docs"],
        has_ci=config["has_ci"],
    )

    if llm:
        meta = polish_meta(meta)

    return meta


def _read_readme(project_path: Path) -> str:
    for name in ("README.md", "README.rst", "README.txt", "readme.md"):
        readme = project_path / name
        if readme.exists():
            try:
                lines = readme.read_text(encoding="utf-8").splitlines()
                return "\n".join(lines[:README_MAX_LINES])
            except (OSError, UnicodeDecodeError):
                pass
    return ""


def _detect_entry_points(project_path: Path, config: dict) -> list[str]:
    entry_points = []

    for name in ("main.py", "app.py", "manage.py", "server.py"):
        if (project_path / name).exists():
            entry_points.append(name)

    for name in ("src/index.js", "src/index.ts", "src/main.js", "src/main.ts"):
        if (project_path / name).exists():
            entry_points.append(name)

    for name in ("main.go", "cmd/main.go"):
        if (project_path / name).exists():
            entry_points.append(name)

    for name in ("src/main.rs",):
        if (project_path / name).exists():
            entry_points.append(name)

    if "start" in config["scripts"]:
        entry_points.append(f"npm start: {config['scripts']['start']}")

    return entry_points
