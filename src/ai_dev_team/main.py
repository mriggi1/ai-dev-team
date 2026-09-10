"""
Application entry point.
"""

from ai_dev_team.agents.developer import DeveloperAgent
from ai_dev_team.agents.planner import PlannerAgent
from ai_dev_team.llm.provider import LLMProvider


def main() -> None:
    provider = LLMProvider()

    planner = PlannerAgent(provider)
    developer = DeveloperAgent(provider)

    task = "Create a REST API for managing books."

    print("\n=== USER REQUEST ===\n")
    print(task)

    plan = planner.run(task)

    print("\n=== IMPLEMENTATION PLAN ===\n")
    print(plan)

    code = developer.run(plan)

    print("\n=== GENERATED CODE ===\n")
    print(code)


if __name__ == "__main__":
    main()