from pathlib import Path

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
