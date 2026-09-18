# Roadmap

## Sprint 1

- Python environment
- UV package manager
- Ollama installation
- Project setup

✅ Completed

---

## Sprint 2

- Professional project structure
- Git repository
- Initial documentation
- First commit

✅ Completed

---

## Sprint 3

- LLMProvider
- BaseAgent
- DeveloperAgent
- Developer prompt
- End-to-end execution
- Commit: `feat: add developer agent`

✅ Completed

---

## Sprint 4

- PlannerAgent
- Planner prompt
- Implementation plan passed as input to DeveloperAgent
- Manual orchestration:
  User request → PlannerAgent → DeveloperAgent

✅ Completed

## Sprint 5

- ReviewerAgent and reviewer prompt
- Code review against the implementation plan
- Developer revision based on review findings
- Manual workflow:
  Planner → Developer → Reviewer → Developer revision
- Ollama tool-calling support in LLMProvider
- Developer tool loop:
  - List, read, and write Python files
  - Check syntax and static analysis, then correct reported errors using tool results
  - Limit execution iterations and file access
- Generated projects stored in isolated generated/ directories
- Execution time reporting for Planner, Developer, and Reviewer
- Automated tests for developer tools and correction flow
- Automatic revision cycle after ReviewerAgent findings

✅ Completed

## Sprint 6

- TesterAgent
- Automatic test generation
- Complete development pipeline

---

## Sprint 7

- LangGraph integration
- Workflow state management
- Agent graph orchestration
- Refactor manual orchestration into graph-based workflow

