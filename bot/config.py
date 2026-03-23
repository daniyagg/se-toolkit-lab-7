"""Configuration loader for the bot.

Reads settings from environment variables or .env.bot.secret file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str = ""

    # LMS Backend
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"


settings = Settings()
