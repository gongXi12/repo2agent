from pathlib import Path

from repo2agent.analyzer import analyze_project
from repo2agent.generator import Generator

FIXTURES = Path(__file__).parent / "fixtures"


def test_generate_claude_md(tmp_path):
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    output = gen.render_claude_md(meta)
    assert "# sample-python" in output
    assert "Python" in output
    assert "src/main.py" in output or "src" in output


def test_generate_agents_md(tmp_path):
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    output = gen.render_agents_md(meta)
    assert "sample-python" in output
    assert "test" in output.lower()


def test_generate_to_directory(tmp_path):
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    gen.generate(meta, output_dir=tmp_path, formats=["md"])
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "AGENTS.md").exists()


def test_generate_dry_run(tmp_path, capsys):
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    gen.generate(meta, output_dir=tmp_path, formats=["md"], dry_run=True)
    assert not (tmp_path / "CLAUDE.md").exists()
    captured = capsys.readouterr()
    assert "sample-python" in captured.out
