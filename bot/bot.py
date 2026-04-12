"""Telegram bot entry point with --test mode support."""

import argparse
import sys
from pathlib import Path

# Add the bot directory to the path so imports work in both test and Telegram modes
BOT_DIR = Path(__file__).parent
sys.path.insert(0, str(BOT_DIR))

from config import load_dotenv
from handlers import handle_start, handle_help, handle_health, handle_labs, handle_scores

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
        # Test mode: route the command and print the result
        response = process_command(args.test)
        print(response)
        sys.exit(0)
    else:
        # Telegram mode: start the bot (implemented in Task 2)
        print("Telegram mode not yet implemented (Task 2)")
        print("Use --test mode for local testing: uv run bot.py --test \"/start\"")


if __name__ == "__main__":
    main()
