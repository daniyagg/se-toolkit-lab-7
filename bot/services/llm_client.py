"""LLM API client for intent routing.

Task 3: Implement LLM client for natural language understanding.
"""

from config import settings


class LLMClient:
    """Client for the LLM API."""

    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_api_base_url
        self.model = settings.llm_api_model

    def chat(self, messages: list[dict]) -> str:
        """Send a chat request to the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            
        Returns:
            The LLM's response text.
        """
        # Task 3: Implement LLM chat completion
        raise NotImplementedError("Task 3: Implement chat")

    def choose_tool(self, tools: list[dict], user_input: str) -> dict | None:
        """Ask the LLM to choose which tool to call.
        
        Args:
            tools: List of tool descriptions.
            user_input: The user's natural language input.
            
        Returns:
            The selected tool dict, or None if no tool matches.
        """
        # Task 3: Implement tool selection via LLM
        raise NotImplementedError("Task 3: Implement choose_tool")
