"""LMS Backend API client.

Makes HTTP requests to the LMS backend with Bearer token authentication.
"""

import httpx

from config import settings


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self) -> None:
        self.base_url = settings.lms_api_base_url.rstrip("/")
        self.api_key = settings.lms_api_key
        self._headers = {"Authorization": f"Bearer {self.api_key}"}

    def _get(self, path: str, params: dict | None = None) -> httpx.Response:
        """Make a GET request to the backend.
        
        Args:
            path: API path (e.g., "/items/").
            params: Optional query parameters.
            
        Returns:
            httpx.Response object.
            
        Raises:
            httpx.HTTPError: On connection errors or HTTP errors.
        """
        url = f"{self.base_url}{path}"
        with httpx.Client() as client:
            return client.get(url, headers=self._headers, params=params, timeout=10.0)

    def health_check(self) -> dict:
        """Check if the backend is healthy.
        
        Returns:
            Dict with 'healthy' bool and 'message' str.
        """
        try:
            response = self._get("/items/")
            response.raise_for_status()
            items = response.json()
            count = len(items) if isinstance(items, list) else 0
            return {"healthy": True, "message": f"Backend is healthy. {count} items available."}
        except httpx.ConnectError as e:
            return {"healthy": False, "message": f"Backend error: connection refused ({self.base_url}). Check that the services are running."}
        except httpx.HTTPStatusError as e:
            return {"healthy": False, "message": f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."}
        except httpx.HTTPError as e:
            return {"healthy": False, "message": f"Backend error: {str(e)}"}

    def get_items(self) -> dict:
        """Fetch all available items/labs.
        
        Returns:
            Dict with 'success' bool, 'items' list, and 'error' str (if failed).
        """
        try:
            response = self._get("/items/")
            response.raise_for_status()
            items = response.json()
            return {"success": True, "items": items, "error": None}
        except httpx.ConnectError as e:
            return {"success": False, "items": [], "error": f"Connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            return {"success": False, "items": [], "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except httpx.HTTPError as e:
            return {"success": False, "items": [], "error": str(e)}

    def get_pass_rates(self, lab: str) -> dict:
        """Fetch pass rates for a specific lab.
        
        Args:
            lab: The lab identifier (e.g., "lab-04").
            
        Returns:
            Dict with 'success' bool, 'pass_rates' list, and 'error' str (if failed).
        """
        try:
            response = self._get("/analytics/pass-rates", params={"lab": lab})
            response.raise_for_status()
            data = response.json()
            return {"success": True, "pass_rates": data, "error": None}
        except httpx.ConnectError as e:
            return {"success": False, "pass_rates": [], "error": f"Connection refused ({self.base_url})"}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"success": False, "pass_rates": [], "error": f"Lab '{lab}' not found"}
            return {"success": False, "pass_rates": [], "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}"}
        except httpx.HTTPError as e:
            return {"success": False, "pass_rates": [], "error": str(e)}
