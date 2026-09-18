"""
Reviewer Agent module.

Defines the agent responsible for reviewing generated code
against its implementation plan and identifying bugs and inconsistencies.
"""

from time import perf_counter

from ai_dev_team.agents.base import BaseAgent
from ai_dev_team.prompts.reviewer import REVIEWER_SYSTEM_PROMPT


class ReviewerAgent(BaseAgent):
    """
    Agent responsible for identifying bugs and inconsistencies in generated code.
    """

    def run(self, task: str) -> str:
        """
        Review the provided task using the reviewer system prompt.

        Args:
            task: Review context containing the implementation plan and code.

        Returns:
            The review containing identified bugs and inconsistencies.
        """
        start_time = perf_counter()
        prompt = f"""
{REVIEWER_SYSTEM_PROMPT}

{task}
"""
        result = self.generate(prompt)
        elapsed_time = perf_counter() - start_time
        print(f"ReviewerAgent execution time: {elapsed_time:.2f} seconds")
        return result

    def review(self, plan: str, code: str) -> str:
        """
        Review generated code against its implementation plan.

        Args:
            plan: Implementation plan produced by the PlannerAgent.
            code: Source code produced by the DeveloperAgent.

        Returns:
            The review containing identified bugs and inconsistencies.
        """
        task = f"""
IMPLEMENTATION PLAN:

{plan}

IMPLEMENTATION:

{code}
"""
        return self.run(task)
