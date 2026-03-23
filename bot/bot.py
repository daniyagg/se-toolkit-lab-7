"""LMS Telegram Bot entry point.

Supports two modes:
- Normal mode: Connects to Telegram and handles messages
- Test mode (--test): Prints handler responses to stdout without Telegram

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test "/start"  # Test mode: print response to stdout
"""

import argparse
import sys

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


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


def run_telegram_mode() -> None:
    """Run the bot connected to Telegram (Task 2+)."""
    print("Starting Telegram bot... (implementation coming in Task 2)")
    # Task 2: Initialize aiogram and start polling
    # For now, just acknowledge the mode


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
