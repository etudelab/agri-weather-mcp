#!/bin/bash
# Script to set up a clean virtual environment and install dependencies

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up clean Python virtual environment for agri-weather-mcp...${NC}"

# Check if .venv directory exists and remove it
if [ -d ".venv" ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf .venv
fi

# Create new virtual environment
echo -e "${YELLOW}Creating new virtual environment...${NC}"
python3 -m venv .venv

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}Virtual environment setup complete!${NC}"
echo -e "${GREEN}To activate the virtual environment, run:${NC}"
echo -e "    source .venv/bin/activate"
echo -e "${GREEN}To run tests, activate the virtual environment and run:${NC}"
echo -e "    python -m pytest"
