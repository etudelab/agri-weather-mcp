"""
Test utilities for mocking external API calls and other testing helpers.
"""
import json
from typing import Dict, Any, Callable
from functools import wraps
from unittest.mock import AsyncMock, patch

class MockResponse:
    """Mock HTTP response object that mimics httpx.Response."""
    
    def __init__(self, status_code: int, json_data: Dict[str, Any]):
        self.status_code = status_code
        self._json_data = json_data
        
    def json(self) -> Dict[str, Any]:
        """Return the JSON data."""
        return self._json_data
        
    def raise_for_status(self) -> None:
        """Raise an exception if the status code is 4xx or 5xx."""
        if 400 <= self.status_code < 600:
            from httpx import HTTPStatusError
            raise HTTPStatusError(f"HTTP Error: {self.status_code}", request=None, response=self)

def mock_api_response(response_data: Dict[str, Any], status_code: int = 200) -> AsyncMock:
    """
    Create a mock for httpx.AsyncClient.get that returns a predefined response.
    
    Args:
        response_data: The JSON data to return in the response
        status_code: The HTTP status code to return (default: 200)
        
    Returns:
        An AsyncMock object that can be used to patch httpx.AsyncClient.get
    """
    mock = AsyncMock()
    mock.return_value = MockResponse(status_code, response_data)
    return mock

def mock_api_error(status_code: int = 500, error_message: str = "Server Error") -> AsyncMock:
    """
    Create a mock for httpx.AsyncClient.get that simulates an API error.
    
    Args:
        status_code: The HTTP error status code to return (default: 500)
        error_message: The error message to include in the response (default: "Server Error")
        
    Returns:
        An AsyncMock object that can be used to patch httpx.AsyncClient.get
    """
    mock = AsyncMock()
    mock.return_value = MockResponse(status_code, {"error": True, "message": error_message})
    return mock

def api_patch(response_data: Dict[str, Any], status_code: int = 200) -> Callable:
    """
    Decorator to patch httpx.AsyncClient.get with a mock response.
    
    Args:
        response_data: The JSON data to return in the response
        status_code: HTTP status code to return
        
    Returns:
        A decorator function that patches httpx.AsyncClient.get
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            with patch('httpx.AsyncClient.get', mock_api_response(response_data, status_code)):
                return await func(*args, **kwargs)
        return wrapper
    return decorator

def mock_httpx_get(response_data, status_code=200):
    """
    Decorator to mock httpx.AsyncClient.get calls
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with patch('httpx.AsyncClient.get') as mock_get:
                mock_response = MockResponse(
                    status_code=status_code,
                    json_data=response_data
                )
                mock_get.return_value = mock_response
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def mock_httpx_get_error(status_code=500, error_message="Server Error"):
    """
    Decorator to mock httpx.AsyncClient.get calls with error responses
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with patch('httpx.AsyncClient.get') as mock_get:
                mock_response = MockResponse(
                    status_code=status_code,
                    text=error_message
                )
                mock_get.return_value = mock_response
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def get_test_locations(server):
    """
    Get test locations for a server instance based on its region configuration.
    
    Args:
        server: WeatherMCPServer instance
        
    Returns:
        list: List of dictionaries with 'lat' and 'lon' keys for testing
    """
    if server.region_bounds is None:
        # Default test location if no region is configured
        return [{"lat": 0.0, "lon": 0.0}]
    
    region_name = server.region_name.lower() if server.region_name else ''
    
    # Return appropriate test locations based on region
    if region_name == 'indonesia':
        return [{"lat": -6.2088, "lon": 106.8456}]  # Jakarta
    elif region_name in ['south east asia', 'south_east_asia']:
        return [{"lat": 1.3521, "lon": 103.8198}]   # Singapore
    elif region_name == 'australia':
        return [{"lat": -33.8688, "lon": 151.2093}] # Sydney
    elif region_name == 'india':
        return [{"lat": 28.6139, "lon": 77.2090}]   # New Delhi
    elif region_name == 'custom':
        # Use the center of the bounds
        bounds = server.region_bounds
        if bounds and all(key in bounds for key in ['lat_min', 'lat_max', 'lon_min', 'lon_max']):
            lat = (bounds['lat_min'] + bounds['lat_max']) / 2
            lon = (bounds['lon_min'] + bounds['lon_max']) / 2
            return [{"lat": lat, "lon": lon}]
    
    # Fallback to a default location
    return [{"lat": 0.0, "lon": 0.0}]
