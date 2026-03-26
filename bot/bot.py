"""LMS Telegram Bot entry point.

Supports two modes:
- Normal mode: Connects to Telegram and handles messages
- Test mode (--test): Prints handler responses to stdout without Telegram

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode: print response to stdout
    uv run bot.py --test "what labs are available"  # Test intent routing
"""

import argparse
import logging
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from config import settings
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_intent,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def route_command(command: str, debug: bool = False) -> str:
    """Route a command string to the appropriate handler.

    Args:
        command: The command string (e.g., "/start", "/scores lab-04").
        debug: If True, print debug info to stderr.

    Returns:
        The handler's response text.
    """
    parts = command.strip().split()
    if not parts:
        return "Empty command. Use /help to see available commands."

    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    if cmd == "/start":
        return handle_start()[0]  # Return just the message, not keyboard
    elif cmd == "/help":
        return handle_help()
    elif cmd == "/health":
        return handle_health()
    elif cmd == "/labs":
        return handle_labs()
    elif cmd == "/scores":
        lab = args[0] if args else ""
        return handle_scores(lab)
    else:
        # Unknown command - try intent routing
        return handle_intent(command, debug=debug)


def run_test_mode(command: str, debug: bool = False) -> None:
    """Run the bot in test mode: print handler response to stdout.

    Args:
        command: The command to test (e.g., "/start").
        debug: If True, print debug info to stderr.
    """
    response = route_command(command, debug=debug)
    print(response)
    sys.exit(0)


async def cmd_start(message: Message) -> None:
    """Handle /start command from Telegram."""
    response, keyboard = handle_start()
    await message.answer(response, reply_markup=keyboard)


async def cmd_help(message: Message) -> None:
    """Handle /help command from Telegram."""
    response = handle_help()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 View Labs", callback_data="labs"),
                InlineKeyboardButton(text="💚 Health Check", callback_data="health"),
            ],
            [
                InlineKeyboardButton(text="📈 My Scores", callback_data="scores"),
            ],
        ]
    )
    await message.answer(response, reply_markup=keyboard)


async def cmd_health(message: Message) -> None:
    """Handle /health command from Telegram."""
    response = handle_health()
    await message.answer(response)


async def cmd_labs(message: Message) -> None:
    """Handle /labs command from Telegram."""
    response = handle_labs()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📈 View Scores", callback_data="scores"),
            ],
        ]
    )
    await message.answer(response, reply_markup=keyboard)


async def cmd_scores(message: Message, args: str) -> None:
    """Handle /scores command from Telegram.

    Args:
        message: The Telegram message.
        args: Command arguments (lab identifier).
    """
    response = handle_scores(args.strip() if args else "")
    await message.answer(response)


async def handle_text_message(message: Message) -> None:
    """Handle plain text messages using intent routing.

    Args:
        message: The Telegram message.
    """
    user_input = message.text or ""
    logger.info(f"Received text message: {user_input}")

    try:
        # Use intent routing with debug logging
        response = handle_intent(user_input, debug=True)
        await message.answer(response)
    except Exception as e:
        logger.error(f"Error in intent routing: {e}")
        await message.answer(
            "I encountered an error processing your request. Please try again or use /help for available commands."
        )


async def handle_callback(message: CallbackQuery) -> None:
    """Handle inline keyboard button callbacks.

    Args:
        message: The callback query from inline keyboard.
    """
    action = message.data

    if action == "labs":
        response = handle_labs()
        await message.message.edit_text(response)
    elif action == "health":
        response = handle_health()
        await message.message.edit_text(response)
    elif action == "help":
        response = handle_help()
        await message.message.edit_text(response)
    elif action == "scores":
        # Prompt user to specify a lab
        response = "Please specify a lab. Example: /scores lab-04"
        await message.message.edit_text(response)
    elif action == "sync":
        from services.lms_client import LMSClient

        client = LMSClient()
        result = client.trigger_sync()
        if result["success"]:
            response = "✅ Data sync completed successfully!"
        else:
            response = f"❌ Sync failed: {result.get('error', 'Unknown error')}"
        await message.message.edit_text(response)
    else:
        await message.answer("Unknown action.")


def run_telegram_mode() -> None:
    """Run the bot connected to Telegram."""
    if not settings.bot_token or settings.bot_token == "test-token":
        logger.error("BOT_TOKEN is not configured. Set it in .env.bot.secret")
        sys.exit(1)

    import asyncio
    from aiogram.client.session.aiohttp import AiohttpSession

    async def poll_bot():
        # Use simple timeout (aiogram expects float, not ClientTimeout object)
        session = AiohttpSession(timeout=30.0)
        bot = Bot(token=settings.bot_token, session=session)

        dp = Dispatcher()

        # Register command handlers
        dp.message.register(cmd_start, CommandStart())
        dp.message.register(cmd_help, Command("help"))
        dp.message.register(cmd_health, Command("health"))
        dp.message.register(cmd_labs, Command("labs"))
        dp.message.register(cmd_scores, Command("scores"))

        # Handle text messages with intent routing
        dp.message.register(handle_text_message, F.text)

        # Handle callback queries from inline keyboards
        dp.callback_query.register(handle_callback)

        logger.info("Starting Telegram bot...")
        await dp.start_polling(bot, skip_updates=True)

    asyncio.run(poll_bot())


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run bot.py --test "/start"    Test /start command
  uv run bot.py --test "what labs are available"    Test intent routing
  uv run bot.py --test "which lab has the lowest pass rate"    Test multi-step reasoning
  uv run bot.py                    Start Telegram bot
""",
    )
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Test mode: run a command and print response to stdout",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging to stderr",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test, debug=args.debug)
    else:
        run_telegram_mode()


if __name__ == "__main__":
    main()
