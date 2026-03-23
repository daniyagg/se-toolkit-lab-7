"""Handler for /scores command."""


def handle_scores(lab: str = "") -> str:
    """Handle the /scores command.
    
    Args:
        lab: The lab identifier (e.g., "lab-04").
        
    Returns:
        Scores for the specified lab (placeholder for Task 2).
    """
    if not lab:
        return "Please specify a lab. Example: /scores lab-04"
    
    # Task 2: Fetch real scores from LMS API
    # For now, return a placeholder response
    return f"Scores for {lab}:\n\n• Task 1: 100% ✓\n• Task 2: 85% ✓\n• Task 3: 60% ⚠\n\nOverall: 82%"
