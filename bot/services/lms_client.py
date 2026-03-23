"""LMS Backend API client.

Task 2: Implement HTTP client to call the LMS backend.
"""

from config import settings


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self) -> None:
        self.base_url = settings.lms_api_base_url
        self.api_key = settings.lms_api_key

    def health_check(self) -> bool:
        """Check if the backend is healthy.
        
        Returns:
            True if backend is up, False otherwise.
        """
        # Task 2: Implement GET /health
        raise NotImplementedError("Task 2: Implement health_check")

    def get_items(self) -> list:
        """Fetch all available items/labs.
        
        Returns:
            List of items from the backend.
        """
        # Task 2: Implement GET /items
        raise NotImplementedError("Task 2: Implement get_items")

    def get_scores(self, lab: str) -> dict:
        """Fetch scores for a specific lab.
        
        Args:
            lab: The lab identifier.
            
        Returns:
            Scores data for the lab.
        """
        # Task 2: Implement GET /analytics or similar
        raise NotImplementedError("Task 2: Implement get_scores")
