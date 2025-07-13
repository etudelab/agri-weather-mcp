"""
Open-Meteo API wrapper for weather data retrieval.

This module provides a clean, async interface to the Open-Meteo API endpoints,
handling HTTP transport, error management, and resource cleanup.
"""

import httpx
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# API endpoints
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"
OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1"


class OpenMeteoAPI:
    """
    Async wrapper for Open-Meteo API endpoints.
    
    This class handles pure HTTP transport without business logic.
    It manages HTTP client lifecycle and provides clean error handling.
    """

    def __init__(self, *, timeout: float = 30.0, client: Optional[httpx.AsyncClient] = None):
        """
        Initialize the API wrapper.
        
        Args:
            timeout: Request timeout in seconds
            client: Optional existing httpx.AsyncClient instance
        """
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout)

    async def forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get weather forecast data from Open-Meteo API.
        
        Args:
            params: Query parameters for the forecast endpoint
            
        Returns:
            JSON response from the API
            
        Raises:
            RuntimeError: If the API request fails
        """
        url = f"{OPEN_METEO_BASE_URL}/forecast"
        return await self._get_json(url, params)

    async def archive(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get historical weather data from Open-Meteo archive API.
        
        Args:
            params: Query parameters for the archive endpoint
            
        Returns:
            JSON response from the API
            
        Raises:
            RuntimeError: If the API request fails
        """
        return await self._get_json(OPEN_METEO_ARCHIVE_URL, params)

    async def _get_json(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP GET request and return JSON response.
        
        Args:
            url: Full URL to request
            params: Query parameters
            
        Returns:
            Parsed JSON response
            
        Raises:
            RuntimeError: If the HTTP request fails
        """
        try:
            logger.debug(f"Making request to {url} with params: {params}")
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            error_msg = f"Open-Meteo API request failed: {exc}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from exc
        except Exception as exc:
            error_msg = f"Unexpected error calling Open-Meteo API: {exc}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from exc

    async def aclose(self) -> None:
        """Close the HTTP client if we own it."""
        if self._owns_client and self._client:
            await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.aclose()
