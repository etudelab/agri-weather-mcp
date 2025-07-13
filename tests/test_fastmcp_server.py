#!/usr/bin/env python3
"""
Test suite for FastMCP v2 Weather MCP Server
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from weather_mcp.server.weather_mcp_server_fastmcp import WeatherMCPServer, PREDEFINED_REGIONS
from weather_mcp.api.open_meteo import OpenMeteoAPI
# Using mock_weather_data fixture from conftest.py instead of importing from test_utils


class TestWeatherMCPServerFastMCP:
    """Test suite for FastMCP v2 Weather MCP Server"""

    @pytest.fixture
    def mock_api(self):
        """Create a mock OpenMeteoAPI instance"""
        mock_api = Mock(spec=OpenMeteoAPI)
        mock_api.forecast = AsyncMock()
        mock_api.archive = AsyncMock()
        mock_api.__aenter__ = AsyncMock(return_value=mock_api)
        mock_api.__aexit__ = AsyncMock()
        return mock_api

    @pytest.fixture
    def server(self, mock_api):
        """Create a WeatherMCPServer instance with mocked API"""
        return WeatherMCPServer(region="indonesia", api=mock_api)

    # Using the mock_weather_data fixture from conftest.py
    # This fixture is automatically available to all tests

    @pytest.mark.asyncio
    async def test_server_initialization(self, mock_api):
        """Test server initialization with different regions"""
        # Test with predefined region
        server = WeatherMCPServer(region="indonesia", api=mock_api)
        assert server.region_name == "indonesia"
        assert server.region_bounds == PREDEFINED_REGIONS["indonesia"]
        
        # Test with custom region
        custom_region = {"lat_min": -5, "lat_max": 5, "lon_min": 100, "lon_max": 120}
        server = WeatherMCPServer(region=custom_region, api=mock_api)
        assert server.region_name == "Custom"
        assert server.region_bounds == custom_region

    @pytest.mark.asyncio
    async def test_get_current_weather_tool(self, server, mock_weather_data):
        """Test get_current_weather tool"""
        server.api.forecast.return_value = mock_weather_data
        
        # Get the tool function from the tool manager
        tool_func = None
        if "get_current_weather" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_current_weather"].fn
        
        assert tool_func is not None, "get_current_weather tool should exist"
        
        # Test the tool
        result = await tool_func(-6.2, 106.8, True)
        
        # Verify the result structure
        assert "location" in result
        assert "weather" in result
        assert "soil" in result
        assert result["location"]["latitude"] == -6.2
        assert result["location"]["longitude"] == 106.8
        
        # Verify API was called
        server.api.forecast.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_weather_forecast_tool(self, server, mock_weather_data):
        """Test get_weather_forecast tool"""
        server.api.forecast.return_value = mock_weather_data
        
        # Get the tool function from the tool manager
        tool_func = None
        if "get_weather_forecast" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_weather_forecast"].fn
        
        assert tool_func is not None, "get_weather_forecast tool should exist"
        
        # Test the tool
        result = await tool_func(-6.2, 106.8, 5, True)
        
        # Verify the result structure
        assert "location" in result
        assert "daily_forecast" in result
        assert "hourly_forecast" in result
        assert result["forecast_days"] == 5
        
        # Verify API was called
        server.api.forecast.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_agricultural_alerts_tool(self, server, mock_weather_data):
        """Test get_agricultural_alerts tool"""
        server.api.forecast.return_value = mock_weather_data
        
        # Get the tool function from the tool manager
        tool_func = None
        if "get_agricultural_alerts" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_agricultural_alerts"].fn
        
        assert tool_func is not None, "get_agricultural_alerts tool should exist"
        
        # Test the tool
        result = await tool_func(-6.2, 106.8, "rice", "vegetative")
        
        # Verify the result structure
        assert "location" in result
        assert "crop_info" in result
        assert "alerts" in result
        assert "recommendations" in result
        assert result["crop_info"]["type"] == "rice"
        assert result["crop_info"]["growth_stage"] == "vegetative"
        
        # Verify API was called multiple times (current weather + forecast)
        assert server.api.forecast.call_count >= 2

    @pytest.mark.asyncio
    async def test_get_soil_conditions_tool(self, server, mock_weather_data):
        """Test get_soil_conditions tool"""
        server.api.forecast.return_value = mock_weather_data
        
        # Get the tool function from the tool manager
        tool_func = None
        if "get_soil_conditions" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_soil_conditions"].fn
        
        assert tool_func is not None, "get_soil_conditions tool should exist"
        
        # Test the tool
        result = await tool_func(-6.2, 106.8, 3)
        
        # Verify the result structure
        assert "location" in result
        assert "soil_conditions" in result
        assert result["forecast_days"] == 3
        
        # Verify API was called
        server.api.forecast.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_evapotranspiration_data_tool(self, server, mock_weather_data):
        """Test get_evapotranspiration_data tool"""
        server.api.forecast.return_value = mock_weather_data
        
        # Get the tool function from the tool manager
        tool_func = None
        if "get_evapotranspiration_data" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_evapotranspiration_data"].fn
        
        assert tool_func is not None, "get_evapotranspiration_data tool should exist"
        
        # Test the tool
        result = await tool_func(-6.2, 106.8, 7)
        
        # Verify the result structure
        assert "location" in result
        assert "daily_et" in result
        assert "hourly_et" in result
        assert result["forecast_days"] == 7
        
        # Verify API was called
        server.api.forecast.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_historical_weather_tool(self, server, mock_weather_data):
        """Test get_historical_weather tool"""
        server.api.archive.return_value = mock_weather_data
        
        # Get the tool function from the tool manager
        tool_func = None
        if "get_historical_weather" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_historical_weather"].fn
        
        assert tool_func is not None, "get_historical_weather tool should exist"
        
        # Test the tool
        result = await tool_func(-6.2, 106.8, "2023-01-01", "2023-01-07")
        
        # Verify the result structure
        assert "location" in result
        assert "historical_data" in result
        assert "period" in result
        assert result["period"]["start_date"] == "2023-01-01"
        assert result["period"]["end_date"] == "2023-01-07"
        
        # Verify API was called
        server.api.archive.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_supported_region_tool(self, server):
        """Test get_supported_region tool"""
        # Get the tool function from the tool manager
        tool_func = None
        if "get_supported_region" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_supported_region"].fn
        
        assert tool_func is not None, "get_supported_region tool should exist"
        
        # Test the tool
        result = await tool_func()
        
        # Verify the result structure
        assert "region_name" in result
        assert "bounding_box" in result
        assert result["region_name"] == "indonesia"
        assert result["bounding_box"] == PREDEFINED_REGIONS["indonesia"]

    @pytest.mark.asyncio
    async def test_coordinate_validation(self, server):
        """Test coordinate validation"""
        # Test valid coordinates within region
        assert server._validate_coordinates(-6.2, 106.8) is True
        
        # Test invalid coordinates outside region
        assert server._validate_coordinates(50.0, 10.0) is False
        
        # Test invalid global coordinates
        assert server._validate_coordinates(100.0, 200.0) is False

    @pytest.mark.asyncio
    async def test_error_handling(self, server):
        """Test error handling in tools"""
        # Get the tool function from the tool manager
        tool_func = None
        if "get_current_weather" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_current_weather"].fn
        
        # Test coordinates outside region
        with pytest.raises(ValueError, match="Coordinates are outside the configured region"):
            await tool_func(50.0, 10.0, True)
        
        # Test API error
        server.api.forecast.side_effect = Exception("API Error")
        with pytest.raises(Exception, match="API Error"):
            await tool_func(-6.2, 106.8, True)

    @pytest.mark.asyncio
    async def test_mcp_instance_creation(self, server):
        """Test that FastMCP instance is created properly"""
        assert server.mcp is not None
        assert server.mcp.name == "weather-mcp"
        assert len(server.mcp._tool_manager._tools) == 7  # Should have all 7 tools

    @pytest.mark.asyncio
    async def test_tool_names_and_signatures(self, server):
        """Test that all expected tools exist with correct signatures"""
        expected_tools = [
            "get_current_weather",
            "get_weather_forecast", 
            "get_agricultural_alerts",
            "get_soil_conditions",
            "get_evapotranspiration_data",
            "get_historical_weather",
            "get_supported_region"
        ]
        
        tool_names = list(server.mcp._tool_manager._tools.keys())
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} should exist"

    @pytest.mark.asyncio
    async def test_all_tools_async(self, server):
        """Test that all tools are async functions"""
        import asyncio
        
        for tool_name, tool in server.mcp._tool_manager._tools.items():
            assert asyncio.iscoroutinefunction(tool.fn), f"Tool {tool_name} should be async"

    @pytest.mark.asyncio
    async def test_default_parameters(self, server, mock_weather_data):
        """Test tools with default parameters"""
        server.api.forecast.return_value = mock_weather_data
        
        # Test get_current_weather with default include_soil_data
        tool_func = None
        if "get_current_weather" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_current_weather"].fn
        
        result = await tool_func(-6.2, 106.8)  # Should default to include_soil_data=True
        assert "soil" in result
        
        # Test get_weather_forecast with default parameters
        tool_func = None
        if "get_weather_forecast" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_weather_forecast"].fn
        
        result = await tool_func(-6.2, 106.8)  # Should default to days=5, include_hourly=True
        assert result["forecast_days"] == 5
        assert "hourly_forecast" in result

    @pytest.mark.asyncio
    async def test_region_configurations(self, mock_api):
        """Test different region configurations"""
        # Test all predefined regions
        for region_name in PREDEFINED_REGIONS.keys():
            server = WeatherMCPServer(region=region_name, api=mock_api)
            assert server.region_name == region_name
            assert server.region_bounds == PREDEFINED_REGIONS[region_name]
        
        # Test None region (no restrictions)
        server = WeatherMCPServer(region=None, api=mock_api)
        assert server.region_name == "None"
        assert server.region_bounds is None
        
        # Test invalid region
        with pytest.raises(ValueError, match="Unknown predefined region"):
            WeatherMCPServer(region="invalid_region", api=mock_api)

    @pytest.mark.asyncio
    async def test_custom_region_validation(self, mock_api):
        """Test custom region validation"""
        # Test valid custom region
        custom_region = {"lat_min": -5, "lat_max": 5, "lon_min": 100, "lon_max": 120}
        server = WeatherMCPServer(region=custom_region, api=mock_api)
        assert server.region_name == "Custom"
        
        # Test invalid custom region (missing keys)
        invalid_region = {"lat_min": -5, "lat_max": 5}
        with pytest.raises(ValueError, match="Custom region dictionary is missing required keys"):
            WeatherMCPServer(region=invalid_region, api=mock_api)

    @pytest.mark.asyncio
    async def test_crop_specific_recommendations(self, server, mock_weather_data):
        """Test crop-specific recommendations logic"""
        server.api.forecast.return_value = mock_weather_data
        
        # Test rice crop recommendations
        tool_func = None
        if "get_agricultural_alerts" in server.mcp._tool_manager._tools:
            tool_func = server.mcp._tool_manager._tools["get_agricultural_alerts"].fn
        
        result = await tool_func(-6.2, 106.8, "rice", "planting")
        assert result["crop_info"]["type"] == "rice"
        assert result["crop_info"]["growth_stage"] == "planting"
        assert isinstance(result["recommendations"], list)
        
        # Test corn crop recommendations
        result = await tool_func(-6.2, 106.8, "corn", "vegetative")
        assert result["crop_info"]["type"] == "corn"
        assert result["crop_info"]["growth_stage"] == "vegetative"
        
        # Test vegetables crop recommendations
        result = await tool_func(-6.2, 106.8, "vegetables", "flowering")
        assert result["crop_info"]["type"] == "vegetables"
        assert result["crop_info"]["growth_stage"] == "flowering"
