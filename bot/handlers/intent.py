"""Handler for natural language intent routing.

This handler uses the LLM to understand user intent and route to appropriate tools.
"""

from services.llm_client import LLMClient


def handle_intent(message: str, debug: bool = False) -> str:
    """Handle natural language messages using LLM intent routing.

    Args:
        message: The user's natural language input.
        debug: If True, print debug info to stderr.

    Returns:
        The LLM's response after executing necessary tools.
    """
    client = LLMClient()
    return client.route_intent(message, debug=debug)
