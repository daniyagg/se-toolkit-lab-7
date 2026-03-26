"""Handler for /health command."""

from services.lms_client import LMSClient


def handle_health() -> str:
    """Handle the /health command.
    
    Returns:
        Backend health status from the real LMS API.
    """
    client = LMSClient()
    result = client.health_check()
    return result["message"]
