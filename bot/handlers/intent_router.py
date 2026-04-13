"""Intent router for natural language messages.

Routes plain text user messages through the LLM client for tool-based
intent resolution. Also handles fallback cases (greetings, gibberish).
"""

import asyncio
import sys

from services.api_client import APIClient
from services.llm_client import LLMClient


class IntentRouter:
    """Routes natural language messages to the LLM.

    If the message looks like a command (starts with /), returns None
    so the caller can handle it with the command router instead.
    """

    def __init__(self, api_client: APIClient):
        self.llm_client = LLMClient(api_client)

    async def route(self, message: str) -> str | None:
        """Route a message string through the LLM.

        Returns:
            Response string if the message is natural language,
            or None if it looks like a slash command (caller should handle it).
        """
        message = message.strip()

        # If it starts with /, it's a command — let the command router handle it
        if message.startswith("/"):
            return None

        # Send to LLM for tool-based routing
        response = await self.llm_client.route(message)
        return response


def route_sync(message: str) -> str:
    """Synchronous wrapper for --test mode.

    Creates its own API client and LLM client, runs the async loop,
    and returns the final response string.
    """
    from config import load_dotenv

    load_dotenv()

    api_client = APIClient()
    router = IntentRouter(api_client)

    try:
        return asyncio.run(router.route(message))
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        return "⚠️ An error occurred. Check stderr for details."
