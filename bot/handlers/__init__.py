"""Command handlers for the LMS bot."""

from .command.commands import (
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from .command.start import handle_start

__all__ = ["handle_start", "handle_help", "handle_health", "handle_labs", "handle_scores"]
