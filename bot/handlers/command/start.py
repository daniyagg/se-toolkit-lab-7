"""Handler for the /start command."""


def handle_start() -> str:
    """Handle the /start command. Returns a welcome message."""
    return (
        "👋 Welcome to the LMS Assistant Bot!\n\n"
        "I can help you check your labs, scores, and health status.\n"
        "Send /help to see all available commands."
    )
