# Current implementation

The application currently uses Python orchestration in `main.py`:

```text
Planner -> Developer tool loop -> Reviewer -> Developer tool loop (revision)
```

Planner and Reviewer each make a text-generation call. Developer uses Ollama
tool calling to choose actions, observe results, and make corrections. LangGraph
and Tester are planned components, not part of the current execution.

Each execution creates `generated/<run-id>/` relative to the project root.
Both Developer stages share this directory. Existing executions are not
overwritten. Generated files are excluded from Git.

Developer tools live in `src/ai_dev_team/tools/workspace.py`:

- `list_files`: discover saved Python files.
- `read_file`: inspect Python source.
- `write_file`: create or replace Python source within the output directory.
- `check_syntax`: compile saved source without executing it or writing bytecode.
- `check_static_analysis`: run Ruff checks for undefined names and related static errors.

The loop preserves assistant tool calls and tool results in its conversation.
Instructions live in `prompts/developer_tools.py`. `LLMProvider.chat()` handles
tool-enabled messages; `generate()` remains available for the other agents.
Reviewer receives the actual saved source with filename comments.

The loop permits at most 12 model turns and 8 tool calls per turn. Files are
limited to 200 KB each and 20 Python files per output directory. A final response
is accepted only when saved Python files exist, syntax and static analysis pass,
and no write operation remains pending. Exhausting the loop raises an error and
preserves partial files for inspection.

This is syntax validation, not execution, dependency validation, or functional
testing. No shell tool or generated application execution is provided.

Run from the project root with `uv run python -m ai_dev_team.main`.
Run offline checks with `uv run python -B -m unittest discover -s tests -v`.

## Current execution flow

User

&#x20;│

&#x20;▼

Planner (Task Analysis)

&#x20;│

&#x20;▼

Developer (Code writing and tool validation)

&#x20;│

&#x20;▼

Reviewer (Plan and code review)

&#x20;│

&#x20;▼

Developer (Revision and tool validation)

Tester (Tests generating, planned)




