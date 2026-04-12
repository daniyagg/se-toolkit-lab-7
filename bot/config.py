"""Configuration management for the LMS bot.

Loads settings from environment variables, which are typically set
via .env.bot.secret. This keeps secrets out of source code.
"""

import os
from pathlib import Path


def get_bot_token() -> str:
    """Get the Telegram bot token."""
    return os.environ.get("BOT_TOKEN", "")


def get_lms_api_base_url() -> str:
    """Get the LMS API base URL."""
    return os.environ.get("LMS_API_BASE_URL", "http://localhost:42002")


def get_lms_api_key() -> str:
    """Get the LMS API key."""
    return os.environ.get("LMS_API_KEY", "")


def get_llm_api_key() -> str:
    """Get the LLM API key."""
    return os.environ.get("LLM_API_KEY", "")


def get_llm_api_base_url() -> str:
    """Get the LLM API base URL."""
    return os.environ.get("LLM_API_BASE_URL", "")


def get_llm_api_model() -> str:
    """Get the LLM model name."""
    return os.environ.get("LLM_API_MODEL", "coder-model")


def load_dotenv(env_path: str | None = None) -> None:
    """Load environment variables from a .env file.

    Only loads variables that aren't already set in the environment.
    Supports simple KEY=VALUE format (no quotes, no comments).
    """
    if env_path is None:
        # Default: look for .env.bot.secret next to this file's parent
        bot_dir = Path(__file__).parent.parent
        env_path = str(bot_dir / ".env.bot.secret")

    path = Path(env_path)
    if not path.exists():
        return

    with open(path) as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Only set if not already in environment
            if key and key not in os.environ:
                os.environ[key] = value
