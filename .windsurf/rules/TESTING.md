# Testing Guide for Agri-Weather MCP

This document provides guidance on testing the Agri-Weather MCP project, including best practices for writing and running tests.

## Test Structure

The project uses pytest for testing with the following structure:

```
agri-weather-mcp/
├── tests/
│   ├── conftest.py         # Shared fixtures and test configuration
│   ├── test_mcp.py         # Tests for the original MCP server
│   ├── test_fastmcp_server.py # Tests for the FastMCP v2 server
│   └── test_utils.py       # Test utilities and helpers
```

## Key Fixtures

Fixtures are defined in `conftest.py` to promote reuse across test files:

### Mock API Fixtures

- `mock_api`: Creates a mock OpenMeteoAPI instance with mocked async methods
- `mock_weather_response`: Basic mock weather API response
- `mock_forecast_response`: Mock forecast API response
- `mock_historical_response`: Mock historical weather data
- `mock_weather_data`: Complete mock weather dataset that matches Open-Meteo API format

### Server Fixtures

- `server`: Creates a WeatherMCPServer instance with configurable region
- Various region configurations for testing different geographic areas

## Running Tests

1. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Run all tests:
   ```bash
   python -m pytest
   ```

3. Run specific test file:
   ```bash
   python -m pytest tests/test_fastmcp_server.py
   ```

4. Run with verbose output:
   ```bash
   python -m pytest -v
   ```

## FastMCP v2 Notes

The MCP server has been refactored to use FastMCP v2. Key differences from the original implementation:

1. Tool references use `.fn` attribute instead of `.func` in FastMCP v2
2. All tools are defined using the `@self.mcp.tool` decorator
3. Tests are structured to verify the async nature of tools

## Best Practices

1. **Use fixtures from conftest.py**: Centralize test data and setup in `conftest.py` to promote reuse
2. **Mock external APIs**: Never rely on real API calls in tests
3. **Test with different regions**: Use parameterized tests to verify behavior across regions
4. **Test error handling**: Include tests for error cases and API failures
5. **Verify async behavior**: Ensure all async functions are properly tested with pytest.mark.asyncio

## Recent Improvements

- Moved `create_mock_weather_data()` from `test_utils.py` to `conftest.py` as a fixture for cleaner test setup
- Updated test imports to use the fixture directly
- Fixed FastMCP v2 attribute references (`.fn` instead of `.func`)
- Added comprehensive docstrings to fixtures
