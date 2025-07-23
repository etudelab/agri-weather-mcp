#!/usr/bin/env python3
"""
Main entry point for the Weather MCP Server.
"""

import asyncio
import argparse
from weather_mcp.server.weather_mcp_server_fastmcp import WeatherMCPServer

async def main():
    parser = argparse.ArgumentParser(description="Run the Agri-Weather MCP Server.")
    parser.add_argument(
        "--region",
        type=str,
        default="indonesia",
        help="Geographical region to restrict weather data (e.g., 'indonesia', 'south_east_asia', 'australia', 'india', or 'none')."
    )
    args = parser.parse_args()

    server = WeatherMCPServer(region=args.region)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
