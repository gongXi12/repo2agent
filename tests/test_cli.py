from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from repo2agent.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_cli_dry_run():
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--dry-run"])
    assert result.exit_code == 0
    assert "sample-python" in result.output


def test_cli_generate_files(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--output", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / "CONTRIBUTING.md").exists()


def test_cli_format_md_only(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--output", str(tmp_path), "--format", "md"])
    assert result.exit_code == 0
    assert (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / "repo2agent.json").exists()


def test_cli_format_json_only(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--output", str(tmp_path), "--format", "json"])
    assert result.exit_code == 0
    assert not (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "repo2agent.json").exists()


def test_cli_invalid_path():
    runner = CliRunner()
    result = runner.invoke(main, ["/nonexistent/path"])
    assert result.exit_code != 0


def test_cli_deep_flag(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--output", str(tmp_path), "--deep"])
    assert result.exit_code == 0
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Calculator" in claude or "hello" in claude


@patch("repo2agent.llm_polisher._call_anthropic")
def test_cli_llm_flag(mock_call, tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mock_call.return_value = "LLM polished description."

    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--output", str(tmp_path), "--llm"])
    assert result.exit_code == 0
    assert (tmp_path / "CLAUDE.md").exists()
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "LLM polished description." in claude


def test_cli_lang_zh(tmp_path):
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--output", str(tmp_path), "--lang", "zh"])
    assert result.exit_code == 0
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "编程语言" in claude
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "项目概述" in agents


def test_cli_lang_zh_dry_run(capsys):
    runner = CliRunner()
    result = runner.invoke(main, [str(FIXTURES / "python_project"), "--lang", "zh", "--dry-run"])
    assert result.exit_code == 0
    assert "项目" in result.output or "生产依赖" in result.output
