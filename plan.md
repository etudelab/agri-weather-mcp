# Weather MCP Server Refactoring Plan

## Overview
Refactor the current `weather_mcp_server.py` to separate concerns by creating a dedicated Open Meteo API wrapper class. This will improve testability, reusability, and maintainability.

## Architecture Goals
- **Separation of Concerns**: Split networking/API logic from MCP tool handling
- **Testability**: Enable easy mocking of API interactions
- **Reusability**: Create reusable API wrapper for potential future services
- **Maintainability**: Centralize API-specific logic in one place

## Final Structure
```
weather_mcp/
├── api/
│   ├── __init__.py
│   └── open_meteo.py          # Pure API wrapper
├── server/
│   ├── __init__.py
│   └── weather_mcp_server.py  # MCP tools + business logic
└── __init__.py                # Package exports
tests/
├── conftest.py                # Test fixtures
├── test_mcp.py               # Main test suite
└── test_utils.py             # Test utilities
main.py                       # Entry point
```

## Current Status
- ✅ **Phase 1 Complete**: Created API wrapper class and directory structure
- ✅ **Phase 2 Complete**: Refactored WeatherMCPServer to use API wrapper
- ✅ **Phase 3 Complete**: Updated tests to work with new architecture
- ✅ **Phase 4 Complete**: Organized file structure and updated documentation
- 🎉 **Refactoring Complete**: All goals achieved successfully!

## Todo Checklist

### Phase 1: Create API Wrapper ✅
- [x] Create `weather_mcp/api/` directory structure
- [x] Implement `OpenMeteoAPI` class in `open_meteo.py`
  - [x] Add async HTTP client management
  - [x] Implement `forecast()` method for forecast endpoint
  - [x] Implement `archive()` method for historical data
  - [x] Add proper error handling and logging
  - [x] Include async context manager support

### Phase 2: Refactor WeatherMCPServer ✅
- [x] Update `WeatherMCPServer.__init__()` to accept `OpenMeteoAPI` instance
- [x] Remove `_make_api_request()` method
- [x] Replace direct HTTP calls with API wrapper calls
- [x] Update forecast methods to use `api.forecast()`
- [x] Update historical methods to use `api.archive()`
- [x] Remove unused imports (`httpx`, `urlencode`)
- [x] Add proper shutdown handling for API wrapper

### Phase 3: Update Tests ✅
- [x] Update test fixtures to mock `OpenMeteoAPI`
- [x] Refactor existing tests to work with new architecture
- [x] Add unit tests for `OpenMeteoAPI` class
- [x] Ensure all existing functionality still works

### Phase 4: Cleanup & Documentation ✅
- [x] Move files to proper directory structure
- [x] Update all import statements and package structure
- [x] Create main entry point
- [x] Update test configuration
- [x] Update documentation with new structure

## Design Decisions

### OpenMeteoAPI Class Features
- **Transport Only**: Pure HTTP wrapper, no business logic
- **Dependency Injection**: Accept optional httpx.AsyncClient
- **Async Context Manager**: Proper resource cleanup
- **Error Handling**: Centralized exception mapping
- **Timeout Configuration**: Configurable request timeout

### WeatherMCPServer Changes
- **Constructor**: Accept optional `OpenMeteoAPI` instance (defaults to new instance)
- **Method Delegation**: Replace direct HTTP calls with wrapper methods
- **Resource Management**: Ensure API wrapper is properly closed

## Benefits
1. **Clear Separation**: Networking logic isolated from MCP handling
2. **Easy Testing**: Mock API wrapper instead of HTTP calls
3. **Future Extensions**: Reusable for CLI, web dashboard, etc.
4. **Maintenance**: API changes centralized in one file
5. **Error Handling**: Consistent error patterns across all API calls

## Risk Mitigation
- Keep existing public interface of WeatherMCPServer unchanged
- Maintain backward compatibility for all tool methods
- Comprehensive testing to ensure no regression
- Gradual migration approach (wrapper first, then refactor)
