"""Optional LLM-powered project description polishing."""
from __future__ import annotations

import logging
import os
from dataclasses import replace

from repo2agent.models import ProjectMeta

logger = logging.getLogger(__name__)


def polish_meta(meta: ProjectMeta) -> ProjectMeta:
    """Polish project description using an LLM if available.

    Returns a new ProjectMeta with an improved description.
    Falls back to the original meta if no API key is set or the call fails.
    """
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    prompt = _build_prompt(meta)

    new_description = None
    if anthropic_key:
        try:
            new_description = _call_anthropic(prompt, anthropic_key)
        except Exception as e:
            logger.warning("Anthropic API call failed: %s", e)
    elif openai_key:
        try:
            new_description = _call_openai(prompt, openai_key)
        except Exception as e:
            logger.warning("OpenAI API call failed: %s", e)
    else:
        logger.info("No LLM API key found (ANTHROPIC_API_KEY or OPENAI_API_KEY). Skipping polish.")

    if new_description:
        return replace(meta, description=new_description)
    return meta


def _build_prompt(meta: ProjectMeta) -> str:
    """Build a prompt for the LLM to polish the project description."""
    deps_list = ", ".join(meta.dependencies.get("prod", []))
    frameworks = ", ".join(meta.frameworks) if meta.frameworks else "None detected"
    languages = ", ".join(meta.languages) if meta.languages else "Unknown"
    scripts = "\n".join(f"  {k}: {v}" for k, v in meta.scripts.items()) if meta.scripts else "None"
    interfaces_summary = ""
    if meta.interfaces:
        interfaces_summary = "\nKey interfaces:\n" + "\n".join(
            f"  - {i.signature}" for i in meta.interfaces[:20]
        )

    return f"""You are analyzing a code repository. Write a concise, informative project description (2-4 sentences) suitable for developer documentation.

Project name: {meta.name}
Current description: {meta.description}
Languages: {languages}
Frameworks: {frameworks}
Dependencies: {deps_list or "None"}
Entry points: {", ".join(meta.entry_points) or "None detected"}
Scripts:
{scripts}
Has tests: {meta.has_tests}
Has CI: {meta.has_ci}
{f"README excerpt: {meta.readme_excerpt[:500]}" if meta.readme_excerpt else ""}
{interfaces_summary}

Write ONLY the improved description. No preamble, no explanation."""


def _call_anthropic(prompt: str, api_key: str) -> str:
    """Call Anthropic API and return the response text."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def _call_openai(prompt: str, api_key: str) -> str:
    """Call OpenAI API and return the response text."""
    import openai

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=300,
        messages=[
            {"role": "system", "content": "You are a technical writer who writes concise project descriptions."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()
