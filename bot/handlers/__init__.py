"""Command handlers for the LMS bot.

These are plain functions that take input and return text.
They don't know about Telegram — same functions work from --test mode,
unit tests, or the Telegram bot handler.
"""


def handle_start() -> str:
    """Handle the /start command. Returns a welcome message."""
    return (
        "👋 Welcome to the LMS Assistant Bot!\n\n"
        "I can help you check your labs, scores, and health status.\n"
        "Send /help to see all available commands."
    )


def handle_help() -> str:
    """Handle the /help command. Returns a list of available commands."""
    return (
        "📖 *Available commands:*\n\n"
        "/start — Start the bot\n"
        "/help — Show this help message\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — Get your scores for a lab"
    )


def handle_health() -> str:
    """Handle the /health command. Returns backend health status (placeholder)."""
    return "🏥 Backend status: Not implemented yet (Task 2)"


def handle_labs() -> str:
    """Handle the /labs command. Returns list of labs (placeholder)."""
    return "📋 Labs: Not implemented yet (Task 2)"


def handle_scores(args: str) -> str:
    """Handle the /scores command. Returns scores for a lab (placeholder)."""
    return f"📊 Scores for '{args or 'unknown'}': Not implemented yet (Task 2)"
