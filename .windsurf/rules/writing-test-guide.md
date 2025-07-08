---
trigger: always_on
---

# Writing and Running Tests for the Agri-Weather MCP Project

This guide outlines best practices for writing and running tests for the Agri-Weather MCP project based on the improvements we've implemented.

## Project Test Structure

```
agri-weather-mcp/
├── conftest.py         # Shared fixtures and test configuration
├── test_mcp.py         # Main test file for the MCP server
├── test_utils.py       # Test utilities and helpers
├── pytest.ini          # pytest configuration
└── requirements.txt    # Project dependencies including test dependencies
```

## Setting Up the Test Environment

1. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify the environment**:
   ```bash
   python3 --version
   pip list
   ```

## Writing Tests

### Test Organization

1. **Use pytest fixtures** in `conftest.py` for shared test setup:
   ```python
   @pytest.fixture
   def server(region_config):
       """Pytest fixture to create a WeatherMCPServer instance for a given region."""
       return WeatherMCPServer(region=region_config)
   ```

2. **Group related tests in classes** for better organization:
   ```python
   class TestWeatherMCPServer:
       """Test suite for the WeatherMCPServer class."""

       @pytest.mark.anyio
       async def test_current_weather(self, server, mock_weather_response):
           # Test implementation
   ```

3. **Use parameterization** to test multiple configurations:
   ```python
   @pytest.fixture(params=TEST_CONFIGS)
   def region_config(request):
       """Pytest fixture to provide region configurations."""
       return request.param
   ```

### Test Implementation Best Practices

1. **Write detailed docstrings** for each test:
   ```python
   """Test get_current_weather tool with mocked API response.

   Verifies that the current weather endpoint correctly processes and returns
   weather data including temperature, humidity, and other current conditions.

   Args:
       server: The WeatherMCPServer instance
       mock_weather_response: Mock API response for current weather
   """
   ```

2. **Use descriptive assertion messages**:
   ```python
   assert "location" in result, "Response missing 'location' field"
   assert isinstance(temp, dict), "Soil temperature should be a dictionary"
   ```

3. **Create helper methods** for common verification tasks:
   ```python
   def _assert_location_structure(self, location):
       """Verify the structure of a location object."""
       assert "latitude" in location, "Location missing latitude"
       assert "longitude" in location, "Location missing longitude"
   ```

4. **Mock external API calls** using the utilities in `test_utils.py`:
   ```python
   with patch('httpx.AsyncClient.get', mock_api_response(mock_weather_response)):
       result = await server._get_current_weather(args)
   ```

5. **Test error handling** with appropriate exceptions:
   ```python
   with pytest.raises(KeyError) as excinfo:
       await server._get_current_weather({})
   assert "latitude" in str(excinfo.value)
   ```

6. **Test API errors** using the mock_api_error utility:
   ```python
   with patch('httpx.AsyncClient.get', mock_api_error(status_code=500, error_message="Server Error")):
       with pytest.raises(Exception) as excinfo:
           await server._get_current_weather(args)
   ```

## Running Tests

1. **Run all tests**:
   ```bash
   python3 -m pytest -v
   ```

2. **Run specific test file**:
   ```bash
   python3 -m pytest -v test_mcp.py
   ```

3. **Run specific test class**:
   ```bash
   python3 -m pytest -v test_mcp.py::TestWeatherMCPServer
   ```

4. **Run specific test method**:
   ```bash
   python3 -m pytest -v test_mcp.py::TestWeatherMCPServer::test_current_weather
   ```

5. **Run tests with specific backend**:
   ```bash
   python3 -m pytest -v --anyio-backend=trio
   ```

## Test Maintenance

1. **Keep mock data up-to-date** with the actual API responses
2. **Regularly review and refactor tests** to maintain clarity and reduce duplication
3. **Fix lint errors and maintain consistent style** in test code
4. **Update test documentation** when changing test behavior or adding new tests
5. **Ensure all tests run in isolation** without dependencies on external services

## Common Patterns

1. **API mocking pattern**:
   ```python
   # In test_utils.py
   def mock_api_response(response_data, status_code=200):
       mock = AsyncMock()
       mock.return_value = MockResponse(status_code, response_data)
       return mock

   # In test file
   with patch('httpx.AsyncClient.get', mock_api_response(mock_data)):
       result = await server.some_method(args)
   ```

2. **Async test pattern**:
   ```python
   @pytest.mark.anyio
   async def test_async_function(self, server):
       result = await server.async_method()
       assert result is not None
   ```

3. **Test data preparation pattern**:
   ```python
   def _prepare_mock_data_for_alerts(self, mock_weather_response, mock_forecast_response):
       # Add required fields to mock data
       if "wind_speed_10m" not in mock_weather_response["current"]:
           mock_weather_response["current"]["wind_speed_10m"] = 15.0
   ```

## Key Best Practices Summary

- Use `pytest` and `anyio` for async test support
- Place fixtures in `conftest.py` for reuse and clarity
- Use `test_utils.py` for shared test helpers and API mocking utilities
- Mock all external API calls; never rely on real API endpoints for tests
- Write tests as async functions when testing async code
- Use clear, descriptive assertion messages and docstrings
- Organize tests by feature and use parameterization for region/config coverage
- Always run tests in a clean Python `venv` with dependencies from `requirements.txt`
- Run tests using `python3 -m pytest -v` from the project root
- Keep test output and config in `pytest.ini` for consistency
- Follow naming conventions: test files should start with `test_`, test functions/classes should start with `test_`
- Avoid test duplication by using helpers and fixtures
- Regularly lint test code and fix style issues

By following these best practices, you'll maintain a robust, reliable, and maintainable test suite for the Agri-Weather MCP project.
