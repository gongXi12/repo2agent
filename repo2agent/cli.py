from __future__ import annotations

import sys
from pathlib import Path

import click

from repo2agent.analyzer import analyze_project
from repo2agent.generator import Generator


@click.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False))
@click.option("--deep", is_flag=True, help="Enable AST deep scanning")
@click.option("--llm", is_flag=True, help="Enable LLM polish (requires API key)")
@click.option("--output", "-o", type=click.Path(), default=".", help="Output directory")
@click.option("--format", "-f", "formats", type=click.Choice(["md", "json", "all"]), default="all", help="Output format")
@click.option("--dry-run", is_flag=True, help="Print summary only, don't write files")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(
    path: str,
    deep: bool,
    llm: bool,
    output: str,
    formats: str,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Scan a code repository and generate agent-ready context files."""
    project_path = Path(path).resolve()

    if verbose:
        click.echo(f"Scanning: {project_path}")

    try:
        meta = analyze_project(project_path)
    except Exception as e:
        click.echo(f"Error scanning project: {e}", err=True)
        sys.exit(1)

    generator = Generator()
    output_dir = Path(output).resolve()

    generator.generate(
        meta=meta,
        output_dir=output_dir,
        formats=[formats],
        dry_run=dry_run,
    )

    if not dry_run:
        click.echo(f"Generated files in {output_dir}")


if __name__ == "__main__":
    main()
