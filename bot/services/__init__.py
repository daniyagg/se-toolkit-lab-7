"""Service clients for the bot.

- lms_client: Backend API client (Task 2)
- llm_client: LLM API client (Task 3)
"""

from .lms_client import LMSClient
from .llm_client import LLMClient

__all__ = ["LMSClient", "LLMClient"]
