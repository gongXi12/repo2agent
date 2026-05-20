# tests/test_integration.py
import json
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from repo2agent.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_full_pipeline_python(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--output", str(tmp_path)])
    assert result.exit_code == 0

    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "CONTRIBUTING.md").exists()
    assert (tmp_path / "repo2agent.json").exists()
    assert (tmp_path / ".cursorrules").exists()
    assert (tmp_path / ".github" / "copilot-instructions.md").exists()

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "sample-python" in claude
    assert "Python" in claude

    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "sample-python" in agents


def test_full_pipeline_js(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "js_project"), "--output", str(tmp_path)])
    assert result.exit_code == 0

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "sample-js" in claude
    assert "JavaScript" in claude
    assert "React" in claude


def test_full_pipeline_deep_python(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [
        str(FIXTURES / "python_project"), "--deep", "--output", str(tmp_path),
    ])
    assert result.exit_code == 0

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Calculator" in claude or "hello" in claude

    data = json.loads((tmp_path / "repo2agent.json").read_text(encoding="utf-8"))
    assert "interfaces" in data
    assert len(data["interfaces"]) > 0


def test_full_pipeline_deep_js(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [
        str(FIXTURES / "js_project"), "--deep", "--output", str(tmp_path),
    ])
    assert result.exit_code == 0

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "JavaScript" in claude


def test_full_pipeline_deep_go(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [
        str(FIXTURES / "go_project"), "--deep", "--output", str(tmp_path),
    ])
    assert result.exit_code == 0

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Go" in claude


@patch("repo2agent.llm_polisher._call_anthropic")
def test_full_pipeline_llm(mock_call_anthropic, tmp_path, monkeypatch):
    mock_call_anthropic.return_value = "LLM-polished project description"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")

    runner = CliRunner()
    result = runner.invoke(main, [
        str(FIXTURES / "python_project"), "--llm", "--output", str(tmp_path),
    ])
    assert result.exit_code == 0

    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "LLM-polished project description" in claude
