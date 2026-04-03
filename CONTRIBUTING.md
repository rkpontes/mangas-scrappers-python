# Contributing

## Scope

This repository is primarily a didactic project for studying
Specification-Driven Development with Spec Kit and for building a small Python
CLI application.

Contributions should keep the project:
- small
- readable
- aligned with the documented specification artifacts
- limited to publicly accessible content flows

## Workflow

1. Start from the active specification documents in `specs/`.
2. Keep changes consistent with `spec.md`, `plan.md`, and `tasks.md`.
3. Prefer small, reviewable commits.
4. Update documentation when behavior changes.
5. Preserve the didactic nature of the repository.

## Development Notes

- Use a local virtual environment.
- Install dependencies with:

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/pip install -e .
```

- Run the CLI locally with:

```bash
.venv/bin/python -m src.cli.main --help
```

## Out of Scope

Contributions that add support for bypassing advertisements, monetization
gates, access controls, authentication walls, anti-bot measures, or similar
third-party restrictions are out of scope for this project.
