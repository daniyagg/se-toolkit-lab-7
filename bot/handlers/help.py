"""Handler for /help command."""


def handle_help() -> str:
    """Handle the /help command.
    
    Returns:
        List of available commands with descriptions.
    """
    return """Available commands:

/start - Welcome message and introduction
/help - Show this help message
/health - Check if the backend system is online
/labs - List all available labs
/scores <lab> - View scores for a specific lab (e.g., /scores lab-04)

You can also ask questions in plain language (coming soon)!"""
