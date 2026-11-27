# AGENTS.md

## Project state

- Early scaffold: the only source file is `src/tareas/__init__.py` (`__version__`); the CLI implementation does not exist yet. `README.md` is empty, so `pyproject.toml` is the spec.
- `src/` layout with Python 3.12 pinned in `.python-version`; the `tareas` package is installed editable by uv.

## Commands and gotchas

- `pyproject.toml` declares `tareas = "tareas.cli:app"` (Typer), but `src/tareas/cli.py` is missing. Define a module-level `app` there before expecting `uv run tareas ...` to work; otherwise the console script fails on import.
- Set up with `uv sync` (reads `uv.lock`, creates `.venv`), then run the CLI via `uv run tareas ...`. Add or remove dependencies with `uv add` / `uv remove` so both `pyproject.toml` and `uv.lock` stay in sync; do not hand-edit `uv.lock`.
- No test, lint, format, typecheck, or CI config exists. Focused verification currently means running the CLI itself; do not invent pytest/ruff/mypy targets.

## Tooling notes

- `opencode.json` sets edit and shell permissions to `ask`; expect an approval prompt for changes and commands.

## Normas del proyecto

- Yo escribiré `acciones.json` a mano. OpenCode puede ayudarme a comprobar si es válido, pero debe dejar que yo redacte las acciones.