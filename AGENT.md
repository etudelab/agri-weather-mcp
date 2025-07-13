# Weather MCP Server - Agent Configuration

## Commands
**IMPORTANT**: Always activate virtual environment first: `source .venv/bin/activate`

- **Test all**: `python -m pytest` or `pytest`
- **Test single file**: `python -m pytest test_mcp.py::TestWeatherMCPServer::test_current_weather`
- **Run server**: `python main.py`
- **Run MCP tools**: `python scripts/run_mcp_tools.py --tool <tool_name>` or `./scripts/run_mcp_tools.sh`
- **Virtual env setup**: `./setup_venv.sh` or manually: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

## Architecture
- **Package structure**: Modular design with separate API and server concerns
  - `weather_mcp/api/open_meteo.py` - Pure HTTP transport wrapper
  - `weather_mcp/server/weather_mcp_server.py` - MCP server with 7 weather tools
  - `main.py` - Entry point script
- **Test structure**: `tests/` directory with organized test files
  - `tests/test_mcp.py` (main tests), `tests/conftest.py` (fixtures), `tests/test_utils.py` (mock helpers)
- **API integration**: Open-Meteo weather API (forecast and archive endpoints)
- **Framework**: MCP (Model Context Protocol) with dependency injection for testability
- **Regional support**: Predefined regions (Indonesia, South East Asia, Australia, India) with coordinate validation

## Code Style
- **Import order**: stdlib, third-party, local modules
- **Async patterns**: All API calls use `async`/`await` with httpx.AsyncClient
- **Error handling**: Try/catch with logging, return error responses in MCP format
- **Type hints**: Full typing with Union, Dict, Any from typing module
- **Constants**: UPPER_CASE at module level (OPEN_METEO_BASE_URL, PREDEFINED_REGIONS)
- **Class structure**: Private methods prefixed with `_`, tool handlers as async methods
- **Testing**: pytest with anyio backend, fixtures in conftest.py, mock API responses

## Commit Messages
- **Commit message format**: <type>(<scope>): <subject>
- **Commit message types**: feat, fix, docs, style, refactor, test, chore
