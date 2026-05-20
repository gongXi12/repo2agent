from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, PackageLoader

from repo2agent.models import FileNode, ProjectMeta


class Generator:
    def __init__(self) -> None:
        self._env = Environment(
            loader=PackageLoader("repo2agent", "templates"),
            keep_trailing_newline=True,
        )
        self._env.globals["_render_tree"] = self._render_tree

    def generate(
        self,
        meta: ProjectMeta,
        output_dir: Path,
        formats: list[str] | None = None,
        dry_run: bool = False,
    ) -> None:
        if formats is None:
            formats = ["all"]

        if dry_run:
            self._print_summary(meta)
            return

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if "all" in formats or "md" in formats:
            self._write(output_dir / "CLAUDE.md", self.render_claude_md(meta))
            self._write(output_dir / "AGENTS.md", self.render_agents_md(meta))
            self._write(output_dir / "CONTRIBUTING.md", self.render_contributing_md(meta))

        if "all" in formats or "json" in formats:
            self._write(output_dir / "repo2agent.json", self.render_json(meta))

    def render_claude_md(self, meta: ProjectMeta) -> str:
        template = self._env.get_template("claude.md.j2")
        return template.render(meta=meta)

    def render_agents_md(self, meta: ProjectMeta) -> str:
        template = self._env.get_template("agents.md.j2")
        return template.render(meta=meta)

    def render_contributing_md(self, meta: ProjectMeta) -> str:
        template = self._env.get_template("contributing.md.j2")
        return template.render(meta=meta)

    def render_json(self, meta: ProjectMeta) -> str:
        data = {
            "name": meta.name,
            "description": meta.description,
            "languages": meta.languages,
            "frameworks": meta.frameworks,
            "dependencies": meta.dependencies,
            "scripts": meta.scripts,
            "entry_points": meta.entry_points,
            "has_tests": meta.has_tests,
            "has_docs": meta.has_docs,
            "has_ci": meta.has_ci,
        }
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    def _print_summary(self, meta: ProjectMeta) -> None:
        frameworks = f" ({' + '.join(meta.frameworks)})" if meta.frameworks else ""
        print(f"\n📦 Project: {meta.name} ({', '.join(meta.languages)}{frameworks})")
        print(f"📁 Structure: {self._flat_structure(meta.structure)}")
        dep_count = len(meta.dependencies.get("prod", []))
        print(f"🔗 Dependencies: {dep_count} production")
        if meta.scripts:
            first_script = next(iter(meta.scripts.values()))
            print(f"🚀 Start: {first_script}")
        print(f"✅ Would generate: CLAUDE.md, AGENTS.md, CONTRIBUTING.md, repo2agent.json\n")

    def _flat_structure(self, node: FileNode, prefix: str = "") -> str:
        dirs = []
        if node.children:
            for child in node.children:
                if child.is_dir:
                    dirs.append(child.path)
        return " ".join(dirs[:5]) + (" ..." if len(dirs) > 5 else "")

    def _render_tree(self, node: FileNode, prefix: str) -> str:
        lines = []

        def _walk(n: FileNode, pfx: str) -> None:
            if n.children:
                for i, child in enumerate(n.children):
                    is_last = i == len(n.children) - 1
                    connector = "└── " if is_last else "├── "
                    lines.append(f"{pfx}{connector}{child.path}")
                    if child.children:
                        child_pfx = pfx + ("    " if is_last else "│   ")
                        _walk(child, child_pfx)

        lines.append(node.path)
        _walk(node, prefix)
        return "\n".join(lines)

    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
