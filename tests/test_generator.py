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


def test_generate_cursorrules(tmp_path):
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    gen.generate(meta, output_dir=tmp_path, formats=["all"])
    assert (tmp_path / ".cursorrules").exists()
    content = (tmp_path / ".cursorrules").read_text(encoding="utf-8")
    assert "sample-python" in content


def test_generate_copilot_instructions(tmp_path):
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    gen.generate(meta, output_dir=tmp_path, formats=["all"])
    assert (tmp_path / ".github" / "copilot-instructions.md").exists()


def test_generate_json_includes_interfaces(tmp_path):
    from repo2agent.models import Interface
    meta = analyze_project(FIXTURES / "python_project")
    meta.interfaces.append(Interface(
        name="test_func", kind="function", file_path="src/main.py",
        signature="def test_func() -> None"
    ))
    gen = Generator()
    json_output = gen.render_json(meta)
    import json
    data = json.loads(json_output)
    assert len(data["interfaces"]) > 0
    assert data["interfaces"][0]["name"] == "test_func"


def test_generate_agents_md_includes_interfaces(tmp_path):
    from repo2agent.models import Interface
    meta = analyze_project(FIXTURES / "python_project")
    meta.interfaces.append(Interface(
        name="hello", kind="function", file_path="src/main.py",
        signature="def hello() -> str"
    ))
    gen = Generator()
    output = gen.render_agents_md(meta)
    assert "Key Interfaces" in output
    assert "hello" in output


def test_generate_claude_md_zh():
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    output = gen.render_claude_md(meta, lang="zh")
    assert "# sample-python" in output
    assert "编程语言" in output
    assert "Python" in output


def test_generate_agents_md_zh():
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    output = gen.render_agents_md(meta, lang="zh")
    assert "sample-python" in output
    assert "项目概述" in output
    assert "任务拆解建议" in output


def test_generate_contributing_md_zh():
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    output = gen.render_contributing_md(meta, lang="zh")
    assert "贡献指南" in output
    assert "开发环境搭建" in output


def test_generate_to_directory_zh(tmp_path):
    meta = analyze_project(FIXTURES / "python_project")
    gen = Generator()
    gen.generate(meta, output_dir=tmp_path, formats=["md"], lang="zh")
    assert (tmp_path / "CLAUDE.md").exists()
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "编程语言" in claude
