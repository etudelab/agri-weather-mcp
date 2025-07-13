#!/usr/bin/env python3
"""
MCP Tool Runner Script

This script runs the Weather MCP Server tools against the real server
and outputs the returned payload to files.
"""

import asyncio
import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add parent directory to path to import weather_mcp_server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_mcp_server import WeatherMCPServer

# Define default output directory (relative to project root)
DEFAULT_OUTPUT_DIR = "../tool_outputs"

# Define default location (Jakarta, Indonesia)
DEFAULT_LATITUDE = -6.2088
DEFAULT_LONGITUDE = 106.8456

# Define available tools and their required arguments
AVAILABLE_TOOLS = {
    "current_weather": {
        "method": "_get_current_weather",
        "args": ["latitude", "longitude"],
        "description": "Get current weather conditions"
    },
    "weather_forecast": {
        "method": "_get_weather_forecast",
        "args": ["latitude", "longitude", "days"],
        "description": "Get weather forecast"
    },
    "agricultural_alerts": {
        "method": "_get_agricultural_alerts",
        "args": ["latitude", "longitude", "crop_type", "growth_stage"],
        "description": "Get agricultural alerts and recommendations"
    },
    "soil_conditions": {
        "method": "_get_soil_conditions",
        "args": ["latitude", "longitude"],
        "description": "Get detailed soil conditions"
    },
    "evapotranspiration": {
        "method": "_get_evapotranspiration_data",
        "args": ["latitude", "longitude", "days"],
        "description": "Get evapotranspiration data"
    },
    "historical_weather": {
        "method": "_get_historical_weather",
        "args": ["latitude", "longitude", "start_date", "end_date"],
        "description": "Get historical weather data"
    },
    "supported_region": {
        "method": "get_supported_region",
        "args": [],
        "description": "Get the currently configured geographical region"
    }
}

def save_to_file(data: Dict[str, Any], tool_name: str, output_dir: str) -> str:
    """
    Save data to a JSON file in the specified output directory.
    
    Args:
        data: The data to save
        tool_name: Name of the tool that generated the data
        output_dir: Directory to save the file in
        
    Returns:
        str: Path to the saved file
    """
    # Convert relative path to absolute path from script location
    if not os.path.isabs(output_dir):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, output_dir)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{tool_name}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Write data to file with pretty formatting
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filepath

async def run_tool(server: WeatherMCPServer, tool_name: str, args: Dict[str, Any], output_dir: str) -> None:
    """
    Run a specific MCP tool and save its output.
    
    Args:
        server: The WeatherMCPServer instance
        tool_name: Name of the tool to run
        args: Arguments to pass to the tool
        output_dir: Directory to save the output in
    """
    if tool_name not in AVAILABLE_TOOLS:
        print(f"Error: Unknown tool '{tool_name}'")
        return
    
    tool_info = AVAILABLE_TOOLS[tool_name]
    method_name = tool_info["method"]
    
    # Check if all required arguments are provided
    missing_args = [arg for arg in tool_info["args"] if arg not in args]
    if missing_args:
        print(f"Error: Missing required arguments for {tool_name}: {', '.join(missing_args)}")
        return
    
    try:
        # Get the method from the server instance
        method = getattr(server, method_name)
        
        # Call the method with the provided arguments
        print(f"Running {tool_name}...")
        if tool_name == "supported_region":
            # The get_supported_region method doesn't accept arguments
            result = await method()
        else:
            result = await method(args)
        
        # Save the result to a file
        filepath = save_to_file(result, tool_name, output_dir)
        print(f"Output saved to: {filepath}")
        
    except Exception as e:
        print(f"Error running {tool_name}: {str(e)}")

async def run_all_tools(server: WeatherMCPServer, args: Dict[str, Any], output_dir: str) -> None:
    """
    Run all available MCP tools and save their outputs.
    
    Args:
        server: The WeatherMCPServer instance
        args: Arguments to pass to the tools
        output_dir: Directory to save the outputs in
    """
    # Get supported region info
    await run_tool(server, "supported_region", {}, output_dir)
    
    # Run tools that require location
    if "latitude" in args and "longitude" in args:
        # Current weather
        await run_tool(server, "current_weather", {
            "latitude": args["latitude"],
            "longitude": args["longitude"]
        }, output_dir)
        
        # Weather forecast (default 7 days)
        await run_tool(server, "weather_forecast", {
            "latitude": args["latitude"],
            "longitude": args["longitude"],
            "days": args.get("days", 7)
        }, output_dir)
        
        # Soil conditions
        await run_tool(server, "soil_conditions", {
            "latitude": args["latitude"],
            "longitude": args["longitude"]
        }, output_dir)
        
        # Evapotranspiration data
        await run_tool(server, "evapotranspiration", {
            "latitude": args["latitude"],
            "longitude": args["longitude"],
            "days": args.get("days", 7)
        }, output_dir)
        
        # Agricultural alerts (if crop_type and growth_stage are provided)
        if "crop_type" in args and "growth_stage" in args:
            await run_tool(server, "agricultural_alerts", {
                "latitude": args["latitude"],
                "longitude": args["longitude"],
                "crop_type": args["crop_type"],
                "growth_stage": args["growth_stage"]
            }, output_dir)
        
        # Historical weather (default: last 7 days)
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        await run_tool(server, "historical_weather", {
            "latitude": args["latitude"],
            "longitude": args["longitude"],
            "start_date": args.get("start_date", week_ago),
            "end_date": args.get("end_date", today)
        }, output_dir)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run MCP server tools and save outputs to files")
    
    parser.add_argument("--region", type=str, default="indonesia",
                        help="Region to use (indonesia, south_east_asia, australia, india, none)")
    
    parser.add_argument("--lat", type=float, default=DEFAULT_LATITUDE,
                        help=f"Latitude (default: {DEFAULT_LATITUDE})")
    
    parser.add_argument("--lon", type=float, default=DEFAULT_LONGITUDE,
                        help=f"Longitude (default: {DEFAULT_LONGITUDE})")
    
    parser.add_argument("--days", type=int, default=7,
                        help="Number of days for forecast and evapotranspiration (default: 7)")
    
    parser.add_argument("--crop", type=str, default="rice",
                        help="Crop type for agricultural alerts (default: rice)")
    
    parser.add_argument("--growth", type=str, default="vegetative",
                        help="Growth stage for agricultural alerts (default: vegetative)")
    
    parser.add_argument("--start-date", type=str,
                        help="Start date for historical data (YYYY-MM-DD, default: 7 days ago)")
    
    parser.add_argument("--end-date", type=str,
                        help="End date for historical data (YYYY-MM-DD, default: today)")
    
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR,
                        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    
    parser.add_argument("--tool", type=str,
                        help="Run a specific tool (default: run all tools)")
    
    return parser.parse_args()

async def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Create WeatherMCPServer instance
    server = WeatherMCPServer(region=args.region)
    
    # Prepare arguments dictionary
    tool_args = {
        "latitude": args.lat,
        "longitude": args.lon,
        "days": args.days,
        "crop_type": args.crop,
        "growth_stage": args.growth
    }
    
    # Add date arguments if provided
    if args.start_date:
        tool_args["start_date"] = args.start_date
    if args.end_date:
        tool_args["end_date"] = args.end_date
    
    # Run specific tool or all tools
    if args.tool:
        await run_tool(server, args.tool, tool_args, args.output_dir)
    else:
        await run_all_tools(server, tool_args, args.output_dir)

if __name__ == "__main__":
    asyncio.run(main())
