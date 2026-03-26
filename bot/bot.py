"""LMS Telegram Bot entry point.

Supports two modes:
- Normal mode: Connects to Telegram and handles messages
- Test mode (--test): Prints handler responses to stdout without Telegram

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode: print response to stdout
"""

import argparse
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import settings
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def route_command(command: str) -> str:
    """Route a command string to the appropriate handler.

    Args:
        command: The command string (e.g., "/start", "/scores lab-04")

    Returns:
        The handler's response text.
    """
    parts = command.strip().split()
    if not parts:
        return "Empty command. Use /help to see available commands."

    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    if cmd == "/start":
        return handle_start()
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
        return f"Unknown command: {cmd}\nUse /help to see available commands."


def run_test_mode(command: str) -> None:
    """Run the bot in test mode: print handler response to stdout.

    Args:
        command: The command to test (e.g., "/start")
    """
    response = route_command(command)
    print(response)
    sys.exit(0)


async def cmd_start(message: Message) -> None:
    """Handle /start command from Telegram."""
    response = handle_start()
    await message.answer(response)


async def cmd_help(message: Message) -> None:
    """Handle /help command from Telegram."""
    response = handle_help()
    await message.answer(response)


async def cmd_health(message: Message) -> None:
    """Handle /health command from Telegram."""
    response = handle_health()
    await message.answer(response)


async def cmd_labs(message: Message) -> None:
    """Handle /labs command from Telegram."""
    response = handle_labs()
    await message.answer(response)


async def cmd_scores(message: Message, args: str) -> None:
    """Handle /scores command from Telegram.

    Args:
        message: The Telegram message.
        args: Command arguments (lab identifier).
    """
    response = handle_scores(args.strip() if args else "")
    await message.answer(response)


async def handle_unknown_command(message: Message) -> None:
    """Handle unknown commands or plain text messages."""
    response = "Unknown command. Use /help to see available commands."
    await message.answer(response)


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

        # Handle unknown commands
        dp.message.register(handle_unknown_command)

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
  uv run bot.py                    Start Telegram bot
""",
    )
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Test mode: run a command and print response to stdout",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_mode()


if __name__ == "__main__":
    main()
