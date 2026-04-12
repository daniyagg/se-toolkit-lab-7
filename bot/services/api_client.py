"""LMS API client service.

Makes HTTP requests to the LMS backend with Bearer token authentication.
Reads LMS_API_BASE_URL and LMS_API_KEY from environment variables.
"""

import httpx

from config import get_lms_api_base_url, get_lms_api_key


class APIClient:
    """Client for the LMS backend API.

    All methods return either (data, None) on success or (None, error_message)
    on failure. This forces callers to handle errors explicitly.
    """

    def __init__(self):
        self.base_url = get_lms_api_base_url().rstrip("/")
        self.api_key = get_lms_api_key()

    def _headers(self) -> dict:
        """Return headers with Bearer auth."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def get_items(self) -> tuple[list | None, str | None]:
        """Fetch all items (labs, tasks) from the backend.

        Returns:
            (items, None) on success, or (None, error_message) on failure.
        """
        try:
            response = httpx.get(
                f"{self.base_url}/items/",
                headers=self._headers(),
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json(), None
        except httpx.ConnectError:
            return None, f"connection refused ({self.base_url}). Check that the services are running."
        except httpx.HTTPStatusError as e:
            return None, f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        except httpx.RequestError as e:
            return None, f"request failed: {e}"

    def get_pass_rates(self, lab: str) -> tuple[list | None, str | None]:
        """Fetch per-task pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            (pass_rates, None) on success, or (None, error_message) on failure.
        """
        try:
            response = httpx.get(
                f"{self.base_url}/analytics/pass-rates",
                headers=self._headers(),
                params={"lab": lab},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json(), None
        except httpx.ConnectError:
            return None, f"connection refused ({self.base_url}). Check that the services are running."
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None, f"lab '{lab}' not found. Use /labs to see available labs."
            return None, f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        except httpx.RequestError as e:
            return None, f"request failed: {e}"
