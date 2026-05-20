from pathlib import Path

from repo2agent.analyzer import analyze_project

FIXTURES = Path(__file__).parent / "fixtures"


def test_analyze_python_project():
    project_path = FIXTURES / "python_project"
    meta = analyze_project(project_path)
    assert meta.name == "sample-python"
    assert "Python" in meta.languages
    assert meta.has_tests is True
    assert meta.has_docs is False
    assert "requests" in meta.dependencies["prod"]


def test_analyze_js_project():
    project_path = FIXTURES / "js_project"
    meta = analyze_project(project_path)
    assert meta.name == "sample-js"
    assert "JavaScript" in meta.languages
    assert "React" in meta.frameworks
    assert "Express" in meta.frameworks
    assert "start" in meta.scripts


def test_analyze_readme_excerpt():
    project_path = FIXTURES / "python_project"
    meta = analyze_project(project_path)
    assert "Sample Python" in meta.readme_excerpt


def test_analyze_empty_directory(tmp_path):
    (tmp_path / "main.py").write_text("x = 1")
    meta = analyze_project(tmp_path)
    assert meta.name is None or meta.name == tmp_path.name
    assert meta.structure.is_dir is True
