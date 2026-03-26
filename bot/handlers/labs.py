"""Handler for /labs command."""

from services.lms_client import LMSClient


def handle_labs() -> str:
    """Handle the /labs command.
    
    Returns:
        List of available labs from the real LMS API.
    """
    client = LMSClient()
    result = client.get_items()
    
    if not result["success"]:
        return f"Error fetching labs: {result['error']}"
    
    items = result["items"]
    if not items:
        return "No labs available."
    
    # Format labs from the API response
    # Expected format: [{"id": 1, "title": "Lab 01...", "type": "lab", ...}, ...]
    labs = []
    for item in items:
        item_type = item.get("type", "")
        
        # Only show items with type="lab"
        if item_type == "lab":
            item_id = str(item.get("id", ""))
            item_title = item.get("title", item.get("name", item_id))
            labs.append(f"• {item_title}")
    
    if not labs:
        return "No labs available."
    
    return "Available Labs:\n\n" + "\n".join(labs) + "\n\nUse /scores <lab> to view scores for a specific lab."
