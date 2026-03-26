"""Handler for /start command."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def handle_start() -> tuple[str, InlineKeyboardMarkup]:
    """Handle the /start command.

    Returns:
        Tuple of (welcome message, inline keyboard markup).
    """
    message = "Welcome to the LMS Bot! 🎓\n\nI can help you check system health, browse available labs, and view your scores. You can use slash commands or just type your question in plain language!"

    # Create inline keyboard with common actions
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 View Labs", callback_data="labs"),
                InlineKeyboardButton(text="💚 Health Check", callback_data="health"),
            ],
            [
                InlineKeyboardButton(text="📈 My Scores", callback_data="scores"),
                InlineKeyboardButton(text="❓ Help", callback_data="help"),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Sync Data", callback_data="sync"
                ),
            ],
        ]
    )

    return message, keyboard


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Get the main action keyboard.

    Returns:
        Inline keyboard with common actions.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 View Labs", callback_data="labs"),
                InlineKeyboardButton(text="💚 Health Check", callback_data="health"),
            ],
            [
                InlineKeyboardButton(text="📈 My Scores", callback_data="scores"),
                InlineKeyboardButton(text="❓ Help", callback_data="help"),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Sync Data", callback_data="sync"
                ),
            ],
        ]
    )
