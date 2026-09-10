"""
Application entry point.
"""

from ai_dev_team.agents.developer import DeveloperAgent
from ai_dev_team.llm.provider import LLMProvider


def main() -> None:
    provider = LLMProvider()

    developer = DeveloperAgent(provider)

    task = "Write a Python function that returns the factorial of a number."

    result = developer.run(task)

    print("\nGenerated solution:\n")
    print(result)


if __name__ == "__main__":
    main()