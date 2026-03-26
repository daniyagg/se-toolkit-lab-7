"""Handler for /scores command."""

from services.lms_client import LMSClient


def handle_scores(lab: str = "") -> str:
    """Handle the /scores command.
    
    Args:
        lab: The lab identifier (e.g., "lab-04").
        
    Returns:
        Scores for the specified lab from the real LMS API.
    """
    if not lab:
        return "Please specify a lab. Example: /scores lab-04"
    
    client = LMSClient()
    result = client.get_pass_rates(lab)
    
    if not result["success"]:
        return f"Error: {result['error']}"
    
    pass_rates = result["pass_rates"]
    if not pass_rates:
        return f"No scores found for '{lab}'."
    
    # Format pass rates from the API response
    # Expected format: [{"task": "Task 1", "pass_rate": 0.92, "attempts": 187}, ...]
    lines = [f"Pass rates for {lab}:"]
    for entry in pass_rates:
        task_name = entry.get("task", entry.get("task_name", "Unknown"))
        rate = entry.get("pass_rate", 0) * 100  # Convert to percentage
        attempts = entry.get("attempts", 0)
        status = "✓" if rate >= 80 else "⚠" if rate >= 60 else "!"
        lines.append(f"• {task_name}: {rate:.1f}% ({attempts} attempts) {status}")
    
    return "\n".join(lines)
