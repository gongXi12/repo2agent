from pathlib import Path

from repo2agent.config_parser import parse_configs

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_package_json():
    project_path = FIXTURES / "js_project"
    result = parse_configs(project_path)
    assert result["name"] == "sample-js"
    assert result["description"] == "A sample JS project"
    assert result["scripts"]["start"] == "node src/index.js"
    assert "react" in result["dependencies"]["prod"]
    assert "jest" in result["dependencies"]["dev"]


def test_parse_pyproject_toml():
    project_path = FIXTURES / "python_project"
    result = parse_configs(project_path)
    assert result["name"] == "sample-python"
    assert result["description"] == "A sample Python project"
    assert "requests" in result["dependencies"]["prod"]


def test_parse_missing_configs(tmp_path):
    (tmp_path / "main.py").write_text("x = 1")
    result = parse_configs(tmp_path)
    assert result["name"] is None
    assert result["scripts"] == {}
