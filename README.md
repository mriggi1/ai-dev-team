# AI Dev Team

A local multi-agent software engineering assistant that uses LLMProvider class to select the model to
plan, generate, review, and revise Python projects. Currently it is using a local Ollama model.

## Current flow

```text
User request
    ↓
PlannerAgent
    ↓
DeveloperAgent (tool loop)
    ↓
ReviewerAgent
    ↓
DeveloperAgent (revision tool loop)
```

The workflow is currently orchestrated manually from `src/ai_dev_team/main.py`.
LangGraph integration is planned for a future sprint.

## Requirements

- Python
- uv
- Ollama
- A local Ollama model, such as `qwen3:14b` or `llama3.1:latest`

Install the project dependencies with:

```bash
uv sync
```

## Run

From the project root:

```bash
uv run python -m ai_dev_team.main
```

Each execution creates an isolated project under `generated/<run-id>/`.

## Agents

- **PlannerAgent** creates the implementation plan.
- **DeveloperAgent** creates or revises source files through workspace tools.
- **ReviewerAgent** compares the saved implementation with the plan and reports findings.

## Developer tools

The DeveloperAgent can use the following workspace tools:

- `list_files`: discover Python files in the generated project.
- `read_file`: inspect source files.
- `write_file`: create or replace source files.
- `check_syntax`: compile Python files without executing them.
- `check_static_analysis`: run Ruff checks for undefined names and related static errors.

The DeveloperAgent accepts a result only when source files exist, syntax and
static analysis pass, and no write operation remains pending. The loop is
limited to 12 model turns and 8 tool calls per turn.

## Validation

Run the repository tests with:

```bash
uv run python -B -m unittest discover -s tests -v
```

The current workflow validates syntax and static analysis. It does not yet run
the generated application, install generated-project dependencies, or perform
functional API tests.

## Project status

Sprint 5 is implemented: planning, code generation, review, revision, tool
calling, isolated generated projects, execution-time reporting, and developer
tool tests are available.

Planned work includes TesterAgent, automatic test generation, functional
validation, and LangGraph-based workflow orchestration.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md): current design and execution flow.
- [ROADMAP.md](ROADMAP.md): planned sprint progression.

