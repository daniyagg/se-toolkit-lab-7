"""Command handlers for the Telegram bot.

Handlers are pure functions: they take input and return text.
They don't depend on Telegram — same function works in --test mode,
unit tests, or the real Telegram bot.
"""

from .start import handle_start
from .help import handle_help
from .health import handle_health
from .labs import handle_labs
from .scores import handle_scores

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
