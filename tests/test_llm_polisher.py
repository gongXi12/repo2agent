from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from repo2agent.llm_polisher import polish_meta
from repo2agent.models import FileNode, Interface, ProjectMeta


def _make_meta(**overrides) -> ProjectMeta:
    defaults = dict(
        name="test-project",
        description="A test project",
        languages=["Python"],
        frameworks=["FastAPI"],
        dependencies={"prod": ["requests"], "dev": ["pytest"]},
        scripts={"start": "python main.py"},
        structure=FileNode(path=".", is_dir=True, children=[]),
        readme_excerpt="A sample README",
        entry_points=["main.py"],
        interfaces=[],
        has_tests=True,
        has_docs=False,
        has_ci=False,
    )
    defaults.update(overrides)
    return ProjectMeta(**defaults)


def test_polish_meta_no_api_key(monkeypatch):
    """Returns original meta when no API key is set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    meta = _make_meta()
    result = polish_meta(meta)
    assert result.description == "A test project"


@patch("repo2agent.llm_polisher._call_anthropic")
def test_polish_meta_with_anthropic(mock_call, monkeypatch):
    """Uses Anthropic when ANTHROPIC_API_KEY is set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mock_call.return_value = "Polished description from Claude."

    meta = _make_meta()
    result = polish_meta(meta)

    assert result.description == "Polished description from Claude."
    mock_call.assert_called_once()


@patch("repo2agent.llm_polisher._call_openai")
def test_polish_meta_with_openai(mock_call, monkeypatch):
    """Uses OpenAI when only OPENAI_API_KEY is set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    mock_call.return_value = "Polished description from GPT."

    meta = _make_meta()
    result = polish_meta(meta)

    assert result.description == "Polished description from GPT."
    mock_call.assert_called_once()


@patch("repo2agent.llm_polisher._call_anthropic", side_effect=Exception("API Error"))
def test_polish_meta_api_error(mock_call, monkeypatch):
    """Falls back to original meta when API call fails."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    meta = _make_meta()
    result = polish_meta(meta)

    assert result.description == "A test project"


@patch("repo2agent.llm_polisher._call_anthropic")
def test_polish_meta_prefers_anthropic(mock_call, monkeypatch):
    """Prefers Anthropic when both keys are present."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-oai-test")
    mock_call.return_value = "Claude result."

    meta = _make_meta()
    result = polish_meta(meta)

    assert result.description == "Claude result."
    mock_call.assert_called_once()


@patch("repo2agent.llm_polisher._call_anthropic")
def test_polish_meta_preserves_other_fields(mock_call, monkeypatch):
    """LLM polish only changes description, not other fields."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    mock_call.return_value = "New description."

    meta = _make_meta()
    result = polish_meta(meta)

    assert result.description == "New description."
    assert result.name == "test-project"
    assert result.languages == ["Python"]
    assert result.frameworks == ["FastAPI"]
