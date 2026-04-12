"""Command handlers for the LMS bot.

These are plain functions that take input and return text.
They don't know about Telegram — same functions work from --test mode,
unit tests, or the Telegram bot handler.
"""

from services.api_client import APIClient


def handle_help() -> str:
    """Handle the /help command. Returns a list of available commands."""
    return (
        "Available commands:\n\n"
        "/start — Start the bot\n"
        "/help — Show this help message\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — Get scores for a lab"
    )


def handle_health() -> str:
    """Handle the /health command. Calls the backend to check health."""
    client = APIClient()
    items, error = client.get_items()
    if error:
        return f"Backend error: {error}"
    count = len(items) if items else 0
    return f"Backend is healthy. {count} items available."


def handle_labs() -> str:
    """Handle the /labs command. Fetches real lab list from the backend."""
    client = APIClient()
    items, error = client.get_items()
    if error:
        return f"Backend error: {error}"
    if not items:
        return "No labs found."
    labs = [item for item in items if item.get("type") == "lab"]
    if not labs:
        return "No labs found. The backend may not have lab data synced."
    lines = ["Available labs:"]
    for lab in labs:
        title = lab.get("title", lab.get("name", "Unknown"))
        lines.append(f"- {title}")
    return "\n".join(lines)


def handle_scores(args: str) -> str:
    """Handle the /scores command. Returns scores for a lab."""
    if not args.strip():
        return "Usage: /scores <lab>. Use /labs to see available labs."
    client = APIClient()
    data, error = client.get_pass_rates(args.strip())
    if error:
        return f"Backend error: {error}"
    if not data:
        return f"No score data found for '{args.strip()}'."
    lines = [f"Scores for {args.strip()}:"]
    for entry in data:
        task = entry.get("task", "Unknown")
        score = entry.get("avg_score", 0)
        attempts = entry.get("attempts", 0)
        lines.append(f"- {task}: {score:.1f}% ({attempts} attempts)")
    return "\n".join(lines)
