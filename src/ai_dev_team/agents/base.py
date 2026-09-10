"""
Base Agent module.

Defines the abstract base class for all AI agents in the system.
Every agent shares the same language model provider and must
implement the run() method.
"""

from abc import ABC, abstractmethod

from ai_dev_team.llm.provider import LLMProvider


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def generate(self, prompt: str) -> str:
        """
        Generate a response using the configured language model.
        """
        return self.llm_provider.generate(prompt)

    @abstractmethod
    def run(self, task: str) -> str:
        """
        Execute the agent for the given task.
        """
        pass