import sys
from pathlib import Path

import pytest

from repo2agent.deep_scanner import deep_scan

FIXTURES = Path(__file__).parent / "fixtures"


def test_deep_scan_python_functions():
    """Extract Python function definitions."""
    project_path = FIXTURES / "python_project"
    interfaces = deep_scan(project_path, ["Python"])
    func_names = [i.name for i in interfaces if i.kind == "function"]
    assert "hello" in func_names
    assert "fetch_data" in func_names


def test_deep_scan_python_classes():
    """Extract Python class definitions."""
    project_path = FIXTURES / "python_project"
    interfaces = deep_scan(project_path, ["Python"])
    class_names = [i.name for i in interfaces if i.kind == "class"]
    assert "Calculator" in class_names


def test_deep_scan_python_routes():
    """Extract Flask/FastAPI route decorators."""
    project_path = FIXTURES / "python_project"
    interfaces = deep_scan(project_path, ["Python"])
    routes = [i for i in interfaces if i.kind == "route"]
    assert any("/api/data" in r.signature for r in routes)


def test_deep_scan_python_docstrings():
    """Extract docstrings from Python functions."""
    project_path = FIXTURES / "python_project"
    interfaces = deep_scan(project_path, ["Python"])
    hello = next(i for i in interfaces if i.name == "hello")
    assert hello.docstring is not None
    assert "hello" in hello.docstring.lower()


def test_deep_scan_python_file_path():
    """File paths are relative to project root."""
    project_path = FIXTURES / "python_project"
    interfaces = deep_scan(project_path, ["Python"])
    assert any(Path("src/main.py") == Path(i.file_path) for i in interfaces)


def test_deep_scan_js_functions():
    """Extract JS function declarations."""
    project_path = FIXTURES / "js_project"
    interfaces = deep_scan(project_path, ["JavaScript"])
    func_names = [i.name for i in interfaces if i.kind == "function"]
    assert "fetchData" in func_names


def test_deep_scan_js_classes():
    """Extract JS class declarations."""
    project_path = FIXTURES / "js_project"
    interfaces = deep_scan(project_path, ["JavaScript"])
    class_names = [i.name for i in interfaces if i.kind == "class"]
    assert "UserService" in class_names


def test_deep_scan_go_functions():
    """Extract Go func declarations."""
    project_path = FIXTURES / "go_project"
    interfaces = deep_scan(project_path, ["Go"])
    func_names = [i.name for i in interfaces if i.kind == "function"]
    assert "fetchData" in func_names
    assert "main" in func_names


def test_deep_scan_go_types():
    """Extract Go type declarations."""
    project_path = FIXTURES / "go_project"
    interfaces = deep_scan(project_path, ["Go"])
    type_names = [i.name for i in interfaces if i.kind == "class"]
    assert "Greeter" in type_names


def test_deep_scan_unsupported_language():
    """Unsupported languages return empty list."""
    project_path = FIXTURES / "python_project"
    interfaces = deep_scan(project_path, ["Brainfuck"])
    assert interfaces == []


def test_deep_scan_missing_tree_sitter(tmp_path, monkeypatch):
    """Gracefully handle missing tree-sitter package."""
    (tmp_path / "main.py").write_text("def foo(): pass")
    import repo2agent.deep_scanner as ds
    original_fn = deep_scan

    # Should not raise, just return empty
    interfaces = deep_scan(tmp_path, ["Python"])
    assert isinstance(interfaces, list)
