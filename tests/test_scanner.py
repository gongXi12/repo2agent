import os
from pathlib import Path

from repo2agent.scanner import scan_directory


FIXTURES = Path(__file__).parent / "fixtures"


def test_scan_directory_returns_file_tree():
    project_path = FIXTURES / "python_project"
    tree = scan_directory(project_path)
    assert tree.is_dir is True
    assert tree.path == "."


def test_scan_directory_finds_files():
    project_path = FIXTURES / "python_project"
    tree = scan_directory(project_path)
    all_paths = _collect_paths(tree)
    assert "src/main.py" in all_paths
    assert "tests/test_main.py" in all_paths
    assert "pyproject.toml" in all_paths


def test_scan_directory_respects_gitignore(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("*.pyc\n__pycache__/\n")
    (tmp_path / "main.py").write_text("x = 1")
    (tmp_path / "main.pyc").write_bytes(b"\x00")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "cache.pyc").write_bytes(b"\x00")

    tree = scan_directory(tmp_path)
    all_paths = _collect_paths(tree)
    assert "main.py" in all_paths
    assert "main.pyc" not in all_paths
    assert "__pycache__/cache.pyc" not in all_paths


def test_scan_directory_skips_built_in_ignores(tmp_path):
    (tmp_path / "app.py").write_text("x = 1")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.js").write_text("")

    tree = scan_directory(tmp_path)
    all_paths = _collect_paths(tree)
    assert "app.py" in all_paths
    assert "node_modules/pkg.js" not in all_paths


def _collect_paths(node):
    paths = []
    if not node.is_dir:
        paths.append(node.path)
    if node.children:
        for child in node.children:
            paths.extend(_collect_paths(child))
    return paths
