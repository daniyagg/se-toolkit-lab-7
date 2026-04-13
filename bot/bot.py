"""Telegram bot entry point with --test mode support."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add the bot directory to the path so imports work in both test and Telegram modes
BOT_DIR = Path(__file__).parent
sys.path.insert(0, str(BOT_DIR))

from config import get_bot_token, load_dotenv
from handlers import handle_start, handle_help, handle_health, handle_labs, handle_scores
from handlers.intent_router import IntentRouter
from handlers.intent_router import route_sync
from services.api_client import APIClient

# Load environment variables from .env.bot.secret
load_dotenv()


def process_command(command: str) -> str:
    """Route a command string to the appropriate handler.

    This is the core routing function. It parses the command and arguments,
    then dispatches to the right handler. Same function used by --test mode
    and by the Telegram bot.
    """
    # Split command into parts (e.g., "/scores lab-04" -> ["/scores", "lab-04"])
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    handlers = {
        "/start": handle_start,
        "/help": handle_help,
        "/health": handle_health,
        "/labs": handle_labs,
        "/scores": lambda: handle_scores(args),
    }

    handler = handlers.get(cmd)
    if handler is None:
        return f"❓ Unknown command: {cmd}\nSend /help to see available commands."

    return handler()


def process_message(message: str) -> str:
    """Process any user message — command or natural language.

    If the message starts with /, route to the command handler.
    Otherwise, send it through the LLM intent router.
    """
    message = message.strip()

    # Slash commands go to the command router
    if message.startswith("/"):
        return process_command(message)

    # Everything else goes to the LLM
    return route_sync(message)


# ── Telegram mode (aiogram) ──────────────────────────────────────────────────

# Global router instance for Telegram mode
_router = None


def get_router() -> IntentRouter:
    """Get or create the global intent router."""
    global _router
    if _router is None:
        api_client = APIClient()
        _router = IntentRouter(api_client)
    return _router


async def handle_telegram_start(message):
    """Handle /start command in Telegram mode with inline keyboard buttons."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 What labs?", callback_data="nl:what labs are available"),
                InlineKeyboardButton(text="📊 Scores lab-01", callback_data="nl:scores for lab-01"),
            ],
            [
                InlineKeyboardButton(text="🏆 Top learners", callback_data="nl:top 5 students in lab-01"),
                InlineKeyboardButton(text="👥 Group performance", callback_data="nl:which group is best in lab-01"),
            ],
            [
                InlineKeyboardButton(text="📈 Completion rate", callback_data="nl:completion rate for lab-01"),
                InlineKeyboardButton(text="🔄 Sync data", callback_data="nl:sync the latest data"),
            ],
        ]
    )
    await message.answer(
        "👋 Welcome to the LMS Assistant Bot!\n\n"
        "I can help you check labs, scores, students, and performance data. "
        "Just type your question in plain English, or use one of the buttons below.",
        reply_markup=keyboard,
    )


async def handle_telegram_help(message):
    """Handle /help command in Telegram mode."""
    await message.answer(
        "📖 *Available commands:*\n\n"
        "/start — Start the bot\n"
        "/help — Show this help message\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — Get scores for a lab\n\n"
        "Or just type your question in plain English!"
    )


async def handle_telegram_health(message):
    """Handle /health command in Telegram mode."""
    response = handle_health()
    await message.answer(response)


async def handle_telegram_labs(message):
    """Handle /labs command in Telegram mode."""
    response = handle_labs()
    await message.answer(response)


async def handle_telegram_scores(message, args: str = ""):
    """Handle /scores command in Telegram mode."""
    response = handle_scores(args)
    await message.answer(response)


async def handle_telegram_text(message):
    """Handle natural language messages — route through LLM."""
    user_text = message.text
    response = await get_router().route(user_text)
    if response is None:
        # Shouldn't happen for non-command text, but just in case
        response = "I didn't understand that. Try asking about labs, scores, or students!"
    await message.answer(response)


async def handle_telegram_callback(callback_query):
    """Handle inline keyboard button presses."""
    data = callback_query.data
    if data.startswith("nl:"):
        # Extract the natural language query after "nl:" prefix
        query = data[3:]
        await callback_query.answer()  # Acknowledge the callback
        response = await get_router().route(query)
        await callback_query.message.answer(response)


def run_telegram_bot():
    """Start the Telegram bot with aiogram."""
    from aiogram import Bot, Dispatcher, F
    from aiogram.filters import Command

    token = get_bot_token()
    if not token:
        print("❌ BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=token)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(handle_telegram_start, Command("start"))
    dp.message.register(handle_telegram_help, Command("help"))
    dp.message.register(handle_telegram_health, Command("health"))
    dp.message.register(handle_telegram_labs, Command("labs"))
    dp.message.register(handle_telegram_scores, Command("scores"))
    dp.message.register(handle_telegram_text, F.text)
    dp.callback_query.register(handle_telegram_callback)

    print("🤖 Telegram bot started. Polling for updates...")
    asyncio.run(dp.start_polling(bot))


def main():
    """Entry point. Supports --test mode for local testing without Telegram."""
    parser = argparse.ArgumentParser(description="LMS Assistant Bot")
    parser.add_argument(
        "--test",
        type=str,
        help="Test mode: process a command string and print response to stdout",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: route the message and print the result
        response = process_message(args.test)
        print(response)
        sys.exit(0)
    else:
        # Telegram mode: start the bot
        run_telegram_bot()


if __name__ == "__main__":
    main()
