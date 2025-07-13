#!/usr/bin/env python3
"""
Main entry point for the Weather MCP Server.
"""

import asyncio
from weather_mcp.server.weather_mcp_server import main

if __name__ == "__main__":
    asyncio.run(main())
