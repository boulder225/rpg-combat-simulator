"""SRD API client for fetching D&D 5e creature data from dnd5eapi.co."""

import time
from typing import Optional

import requests


class SRDCreatureAPI:
    """Client for fetching creature data from the D&D 5e SRD API."""

    BASE_URL = "https://www.dnd5eapi.co/api/2014"
    USER_AGENT = "dnd-simulator/0.1.0"

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize the SRD API client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for network errors
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    def _normalize_name(self, name: str) -> str:
        """
        Convert creature name to API format.

        Args:
            name: Creature name (e.g., "Dire Wolf")

        Returns:
            API-formatted name (e.g., "dire-wolf")
        """
        return name.lower().replace(" ", "-")

    def fetch_monster(self, name: str) -> dict:
        """
        Fetch monster data from the SRD API.

        Args:
            name: Creature name (e.g., "goblin", "Dire Wolf")

        Returns:
            Raw JSON response from the API

        Raises:
            ValueError: If the creature name is invalid (404)
            RuntimeError: If the API returns a server error (500+)
            requests.exceptions.RequestException: For network-level errors
        """
        api_name = self._normalize_name(name)
        url = f"{self.BASE_URL}/monsters/{api_name}"

        # Retry logic with exponential backoff
        last_exception: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)

                # Handle specific HTTP errors
                if response.status_code == 404:
                    raise ValueError(
                        f"Creature '{name}' not found in SRD API. "
                        f"Check spelling or try a different creature name."
                    )
                elif response.status_code >= 500:
                    raise RuntimeError(
                        f"SRD API server error (status {response.status_code}). "
                        f"The API may be temporarily unavailable."
                    )

                # Raise for other HTTP errors
                response.raise_for_status()

                return response.json()

            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
            ) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    backoff_time = 2**attempt
                    time.sleep(backoff_time)
                    continue
                else:
                    # Final attempt failed
                    raise requests.exceptions.RequestException(
                        f"Failed to fetch creature '{name}' after {self.max_retries} attempts. "
                        f"Check your network connection."
                    ) from last_exception

        # Should not reach here, but just in case
        raise requests.exceptions.RequestException(
            f"Failed to fetch creature '{name}' from SRD API."
        )
