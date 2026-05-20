# tests/test_integration.py
from pathlib import Path

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
