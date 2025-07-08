#!/bin/bash
# Script to run MCP server tools against the real server and output payloads to files
# This is a wrapper around run_mcp_tools.py

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Path to the Python script
PYTHON_SCRIPT="run_mcp_tools.py"

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage:${NC} $0 [options]"
    echo ""
    echo "Options:"
    echo "  --lat LAT           Latitude (default: -6.2088, Jakarta)"
    echo "  --lon LON           Longitude (default: 106.8456, Jakarta)"
    echo "  --region REGION     Region (indonesia, south_east_asia, australia, india, none)"
    echo "  --crop CROP         Crop type (default: rice)"
    echo "  --growth GROWTH     Growth stage (default: vegetative)"
    echo "  --days DAYS         Number of forecast days (default: 7)"
    echo "  --start-date DATE   Start date for historical data (YYYY-MM-DD, default: 7 days ago)"
    echo "  --end-date DATE     End date for historical data (YYYY-MM-DD, default: today)"
    echo "  --output-dir DIR    Output directory (default: tool_outputs)"
    echo "  --tool TOOL         Run specific tool (default: run all tools)"
    echo "  --help              Show this help message"
    echo ""
    echo "Available tools:"
    echo "  current_weather     Get current weather conditions"
    echo "  weather_forecast    Get weather forecast"
    echo "  agricultural_alerts Get agricultural alerts and recommendations"
    echo "  soil_conditions     Get detailed soil conditions"
    echo "  evapotranspiration  Get evapotranspiration data"
    echo "  historical_weather  Get historical weather data"
    echo "  supported_region    Get the currently configured geographical region"
    echo ""
}

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Error: Python script $PYTHON_SCRIPT not found${NC}"
    exit 1
fi

# Check if virtual environment exists and activate it
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo -e "${YELLOW}Warning: Virtual environment not found. Attempting to run with system Python...${NC}"
fi

# Make Python script executable if it's not already
if [ ! -x "$PYTHON_SCRIPT" ]; then
    chmod +x "$PYTHON_SCRIPT"
fi

# Build Python command with arguments
PYTHON_CMD="./$PYTHON_SCRIPT"

# Parse command line arguments and pass them to the Python script
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --help)
            show_usage
            exit 0
            ;;
        --lat|--lon|--region|--crop|--growth|--days|--start-date|--end-date|--output-dir|--tool)
            PYTHON_CMD="$PYTHON_CMD $1 $2"
            shift 2
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Run the Python script
echo -e "${BLUE}Running MCP tools using Python script...${NC}"
echo -e "${YELLOW}Command: $PYTHON_CMD${NC}"
echo ""

eval $PYTHON_CMD

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}MCP tools execution completed successfully!${NC}"
else
    echo -e "${RED}Error: MCP tools execution failed${NC}"
    exit 1
fi
