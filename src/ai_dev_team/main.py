"""
Application entry point.
"""

from pathlib import Path
from uuid import uuid4

from ai_dev_team.agents.developer import DeveloperAgent
from ai_dev_team.agents.planner import PlannerAgent
from ai_dev_team.agents.reviewer import ReviewerAgent
from ai_dev_team.llm.provider import LLMProvider
from ai_dev_team.prompts.developer_revision import DEVELOPER_REVISION_PROMPT


def main() -> None:
    provider = LLMProvider()

    planner = PlannerAgent(provider)
    output_dir = Path(__file__).resolve().parents[2] / 'generated' / uuid4().hex
    developer = DeveloperAgent(provider, output_dir=output_dir)
    print(f'Generated project: {output_dir}')
    reviewer = ReviewerAgent(LLMProvider(model=provider.model, timeout=900))

    task = "Create a REST API for managing books."

    print("\n=== USER REQUEST ===\n")
    print(task)

    plan = planner.run(task)

    print("\n=== IMPLEMENTATION PLAN ===\n")
    print(plan)

    code = developer.run(plan)

    print("\n=== GENERATED CODE ===\n")
    print(code)

    review = reviewer.review(plan, code)

    print("\n=== REVIEW ===\n")
    print(review)

    revision_task = f"""
{DEVELOPER_REVISION_PROMPT}

ORIGINAL IMPLEMENTATION PLAN:

{plan}

EXISTING IMPLEMENTATION:

{code}

REVIEW FINDINGS:

{review}
"""
    revised_code = developer.run(revision_task)

    print("\n=== REVISED CODE ===\n")
    print(revised_code)


if __name__ == "__main__":
    main()
