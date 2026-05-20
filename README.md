# repo2agent

Convert any code repository into an agent-ready project.

Scans your project and generates context files for AI coding agents (Claude Code, Cursor, Copilot, Codex).

## Installation

```bash
pip install repo2agent
```

## Usage

```bash
# Generate all files
repo2agent .

# Dry run (preview only)
repo2agent . --dry-run

# Output to specific directory
repo2agent . --output ./agent-context

# Only generate Markdown files
repo2agent . --format md

# Only generate JSON metadata
repo2agent . --format json
```

## Output Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Claude Code context |
| `AGENTS.md` | Generic agent context |
| `CONTRIBUTING.md` | Human collaborators |
| `.cursorrules` | Cursor IDE |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `repo2agent.json` | Machine-readable metadata |

## Supported Languages

- Python
- JavaScript / TypeScript
- Go
- Rust

## License

MIT
