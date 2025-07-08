import asyncio
from datetime import datetime, timedelta
import pytest
from typing import Dict, Any, List, Union
import os
import sys
from unittest.mock import patch, AsyncMock
import pytest
import anyio
from weather_mcp_server import WeatherMCPServer, PREDEFINED_REGIONS
from test_utils import get_test_locations, mock_api_response, mock_api_error, api_patch, get_test_locations

# Constants for test data
TEST_CROP_TYPE = "rice"
TEST_GROWTH_STAGE = "vegetative"
TEST_FORECAST_DAYS = 2

# Import fixtures from conftest.py
# These fixtures are now defined in conftest.py

class TestWeatherMCPServer:
    """Test suite for WeatherMCPServer class.
    
    This class contains tests for all the main functionality of the WeatherMCPServer,
    including region handling, weather data retrieval, and error handling.
    
    Each test method focuses on a specific API endpoint or functionality and uses
    mock responses to avoid external API calls during testing.
    """
    
    def _assert_location_structure(self, location_data):
        """Helper method to verify location data structure.
        
        Args:
            location_data: The location data dictionary to verify
        """
        assert "latitude" in location_data
        assert "longitude" in location_data
        assert isinstance(location_data["latitude"], (int, float))
        assert isinstance(location_data["longitude"], (int, float))
    
    @pytest.mark.anyio
    async def test_get_supported_region(self, server: WeatherMCPServer, region_config: Union[str, Dict, None]):
        """Test the get_supported_region tool.
        
        Verifies that the endpoint returns the correct region information including
        region name and properly formatted region bounds.
        
        Args:
            server: The WeatherMCPServer instance
            region_config: The region configuration to test
        """
        result = await server.get_supported_region()
        
        assert "region_name" in result
        assert "bounding_box" in result
        if isinstance(region_config, str) and region_config.lower() != 'none':
            assert result["region_name"] == region_config
            assert result["bounding_box"] == PREDEFINED_REGIONS[region_config.lower().replace(" ", "_")]
        elif isinstance(region_config, dict):
            assert result["region_name"] == "Custom"
            assert result["bounding_box"] == region_config
        else:  # None
            assert result["region_name"] == "None"
            assert result["bounding_box"] is None

    @pytest.mark.anyio
    async def test_current_weather(self, server: WeatherMCPServer, mock_weather_response):
        """Test get_current_weather tool with mocked API response.
        
        Verifies that the current weather endpoint correctly processes and returns
        weather data including location, current conditions, and soil data.
        
        Args:
            server: The WeatherMCPServer instance
            mock_weather_response: Mock API response for weather data
        """
        with patch('httpx.AsyncClient.get', mock_api_response(mock_weather_response)):
            location = get_test_locations(server)[0]
            args = {"latitude": location["lat"], "longitude": location["lon"]}
            result = await server._get_current_weather(args)
            
            # Verify response structure
            assert "location" in result, "Response missing 'location' field"
            assert "current_time" in result, "Response missing 'current_time' field"
            assert "weather" in result, "Response missing 'weather' field"
            assert "soil" in result, "Response missing 'soil' field"
            
            # Verify location structure
            self._assert_location_structure(result["location"])
            
            # Verify weather data
            weather = result["weather"]
            assert isinstance(weather, dict), "Weather data should be a dictionary"
            assert "temperature" in weather, "Weather missing temperature data"
            assert weather["temperature"] == mock_weather_response["weather"]["temperature"], "Temperature mismatch"
            
            # Verify soil data - nested structure
            soil = result["soil"]
            assert isinstance(soil, dict), "Soil data should be a dictionary"
            assert "temperature" in soil, "Soil missing temperature data"
            assert "moisture" in soil, "Soil missing moisture data"
            assert soil["temperature"]["surface"] == mock_weather_response["soil"]["temperature"]["surface"], "Soil temperature mismatch"

    @pytest.mark.anyio
    async def test_weather_forecast(self, server: WeatherMCPServer, mock_forecast_response):
        """Test get_weather_forecast tool with mocked API response.
        
        Verifies that the weather forecast endpoint correctly processes and returns
        forecast data including location and daily forecasts for the requested period.
        
        Args:
            server: The WeatherMCPServer instance
            mock_forecast_response: Mock API response for forecast data
        """
        with patch('httpx.AsyncClient.get', mock_api_response(mock_forecast_response)):
            location = get_test_locations(server)[0]
            forecast_days = 3
            args = {
                "latitude": location["lat"], 
                "longitude": location["lon"], 
                "days": forecast_days
            }
            result = await server._get_weather_forecast(args)
            
            # Verify response structure
            assert "location" in result, "Response missing 'location' field"
            assert "forecast_days" in result, "Response missing 'forecast_days' field"
            assert "daily_forecast" in result, "Response missing 'daily_forecast' field"
            
            # Verify location structure
            self._assert_location_structure(result["location"])
            
            # Verify forecast data
            assert result["forecast_days"] == forecast_days, "Forecast days mismatch"
            assert isinstance(result["daily_forecast"], list), "Daily forecast should be a list"
            assert len(result["daily_forecast"]) == forecast_days, f"Expected {forecast_days} days of forecast data"
            
            # Verify forecast data structure
            for day in result["daily_forecast"]:
                assert "date" in day, "Forecast day missing date"
                assert "temperature_max" in day, "Forecast day missing max temperature"
                assert "temperature_min" in day, "Forecast day missing min temperature"
            
            # Verify the forecast data matches our mock
            for i, day in enumerate(result["daily_forecast"]):
                assert day["date"] == mock_forecast_response["daily"]["time"][i]
                assert day["temperature_max"] == mock_forecast_response["daily"]["temperature_2m_max"][i]

    @pytest.mark.anyio
    async def test_agricultural_alerts(self, server: WeatherMCPServer, mock_weather_response, mock_forecast_response):
        """Test get_agricultural_alerts tool with mocked API responses.
        
        Verifies that the agricultural alerts endpoint correctly processes weather and forecast data
        to generate relevant agricultural alerts for the specified crop and growth stage.
        
        Args:
            server: The WeatherMCPServer instance
            mock_weather_response: Mock API response for current weather data
            mock_forecast_response: Mock API response for forecast data
        """
        # Setup test data for alerts
        self._prepare_mock_data_for_alerts(mock_weather_response, mock_forecast_response)
        
        # Create a prepared weather response that the _get_current_weather method would return
        prepared_weather_response = {
            "location": mock_weather_response.get("location", {"latitude": 0.0, "longitude": 0.0}),
            "current_time": "2025-07-08T12:00:00Z",
            "weather": {
                "temperature": 30.0,
                "humidity": 70.0,
                "precipitation": 5.0,
                "wind_speed": 15.0,
                "wind_gusts": 25.0,  # Explicitly set wind_gusts
                "pressure": 1010.0
            },
            "soil": {
                "temperature": {
                    "0_7cm": 28.5,
                    "7_28cm": 27.0,
                    "28_100cm": 25.5
                },
                "moisture": {
                    "0_1cm": 0.35,
                    "1_3cm": 0.32,
                    "3_9cm": 0.30,
                    "9_27cm": 0.28,
                    "27_81cm": 0.25
                }
            }
        }
        
        # Create a prepared forecast response that the _get_weather_forecast method would return
        prepared_forecast_response = {
            "location": mock_forecast_response.get("location", {"latitude": 0.0, "longitude": 0.0}),
            "forecast_time": "2025-07-08T12:00:00Z",
            "daily_forecast": [
                {
                    "date": "2025-07-08",
                    "temperature_max": 32.0,
                    "temperature_min": 25.0,
                    "precipitation": 0.5,
                    "humidity": 70,
                    "wind_speed": 15.0
                },
                {
                    "date": "2025-07-09",
                    "temperature_max": 31.5,
                    "temperature_min": 24.7,
                    "precipitation": 0.0,
                    "humidity": 71,
                    "wind_speed": 14.5
                },
                # Add more days to ensure we have enough for the dry spell check
                {
                    "date": "2025-07-10",
                    "temperature_max": 31.0,
                    "temperature_min": 24.4,
                    "precipitation": 0.5,
                    "humidity": 72,
                    "wind_speed": 14.0
                },
                {
                    "date": "2025-07-11",
                    "temperature_max": 30.5,
                    "temperature_min": 24.1,
                    "precipitation": 0.0,
                    "humidity": 73,
                    "wind_speed": 13.5
                },
                {
                    "date": "2025-07-12",
                    "temperature_max": 30.0,
                    "temperature_min": 23.8,
                    "precipitation": 0.5,
                    "humidity": 74,
                    "wind_speed": 13.0
                },
                {
                    "date": "2025-07-13",
                    "temperature_max": 29.5,
                    "temperature_min": 23.5,
                    "precipitation": 0.0,
                    "humidity": 75,
                    "wind_speed": 12.5
                },
                {
                    "date": "2025-07-14",
                    "temperature_max": 29.0,
                    "temperature_min": 23.2,
                    "precipitation": 0.5,
                    "humidity": 76,
                    "wind_speed": 12.0
                }
            ]
        }
        
        # Patch the server methods to return our prepared responses
        async def mock_get_current_weather(args):
            return prepared_weather_response
            
        async def mock_get_weather_forecast(args):
            return prepared_forecast_response
        
        # Apply the patches
        with patch.object(server, '_get_current_weather', side_effect=mock_get_current_weather), \
             patch.object(server, '_get_weather_forecast', side_effect=mock_get_weather_forecast):
            
            location = get_test_locations(server)[0]
            args = {
                "latitude": location["lat"],
                "longitude": location["lon"],
                "crop_type": TEST_CROP_TYPE,
                "growth_stage": TEST_GROWTH_STAGE
            }
            result = await server._get_agricultural_alerts(args)
            
            # Verify response structure
            assert "location" in result, "Response missing 'location' field"
            assert "alerts" in result, "Response missing 'alerts' field"
            assert "crop_info" in result, "Response missing 'crop_info' field"
            
            # Verify location structure
            self._assert_location_structure(result["location"])
            
            # Verify crop info
            crop_info = result["crop_info"]
            assert isinstance(crop_info, dict), "Crop info should be a dictionary"
            assert "type" in crop_info, "Crop info missing type field"
            assert "growth_stage" in crop_info, "Crop info missing growth stage field"
            
            # Verify alerts data
            alerts = result["alerts"]
            assert isinstance(alerts, list), "Alerts should be a list"
            
            # If we have alerts, verify their structure
            if alerts:
                for alert in alerts:
                    assert "type" in alert, "Alert missing type field"
                    assert "severity" in alert, "Alert missing severity field"
                    assert isinstance(alert["type"], str), "Alert type should be a string"
                    assert isinstance(alert["severity"], str), "Alert severity should be a string"
    
    def _prepare_mock_data_for_alerts(self, mock_weather_response, mock_forecast_response):
        """Helper method to prepare mock data for agricultural alerts test.
        
        Args:
            mock_weather_response: Mock weather response to prepare
            mock_forecast_response: Mock forecast response to prepare
        """
        # Create a properly structured weather object if it doesn't exist
        if "weather" not in mock_weather_response:
            mock_weather_response["weather"] = {}
            
        # Ensure all required weather fields exist and are not None
        mock_weather_response["weather"]["wind_speed"] = 15.0
        mock_weather_response["weather"]["wind_gusts"] = 25.0
        mock_weather_response["weather"]["temperature"] = 30.0
        mock_weather_response["weather"]["precipitation"] = 5.0
        mock_weather_response["weather"]["humidity"] = 70.0
        
        # Ensure soil data is available with proper structure
        if "soil" not in mock_weather_response:
            mock_weather_response["soil"] = {}
            
        if "moisture" not in mock_weather_response["soil"]:
            mock_weather_response["soil"]["moisture"] = {}
            
        # Add soil moisture data at different depths
        mock_weather_response["soil"]["moisture"]["0_1cm"] = 0.35
        mock_weather_response["soil"]["moisture"]["1_3cm"] = 0.32
        mock_weather_response["soil"]["moisture"]["3_9cm"] = 0.30
        mock_weather_response["soil"]["moisture"]["9_27cm"] = 0.28
        mock_weather_response["soil"]["moisture"]["27_81cm"] = 0.25
        
        # Add soil temperature data if not present
        if "temperature" not in mock_weather_response["soil"]:
            mock_weather_response["soil"]["temperature"] = {}
            
        mock_weather_response["soil"]["temperature"]["0_7cm"] = 28.5
        mock_weather_response["soil"]["temperature"]["7_28cm"] = 27.0
        mock_weather_response["soil"]["temperature"]["28_100cm"] = 25.5
        
        # Ensure forecast data has proper structure
        if "daily_forecast" not in mock_forecast_response:
            mock_forecast_response["daily_forecast"] = []
            
        # Make sure we have at least 7 days of forecast data
        while len(mock_forecast_response["daily_forecast"]) < 7:
            day_index = len(mock_forecast_response["daily_forecast"])
            mock_forecast_response["daily_forecast"].append({
                "date": f"2025-07-{8 + day_index}",
                "temperature_max": 32.0 - day_index * 0.5,
                "temperature_min": 25.0 - day_index * 0.3,
                "precipitation": 0.5 if day_index % 2 == 0 else 0.0,  # Alternate dry and wet days
                "humidity": 70 + day_index,
                "wind_speed": 15.0 - day_index * 0.5
            })
        
        # Make sure the location field is properly structured
        if "location" not in mock_weather_response or not isinstance(mock_weather_response["location"], dict):
            mock_weather_response["location"] = {
                "latitude": 0.0,
                "longitude": 0.0,
                "name": "Test Location"
            }
        
        # Make sure the location field is properly structured in forecast response
        if "location" not in mock_forecast_response or not isinstance(mock_forecast_response["location"], dict):
            mock_forecast_response["location"] = {
                "latitude": 0.0,
                "longitude": 0.0,
                "name": "Test Location"
            }

    @pytest.mark.anyio
    async def test_soil_conditions(self, server: WeatherMCPServer, mock_soil_response):
        """Test get_soil_conditions tool with mocked API response.
        
        Verifies that the soil conditions endpoint correctly processes and returns
        soil data including temperature and moisture at different depths.
        
        Args:
            server: The WeatherMCPServer instance
            mock_soil_response: Mock API response for soil data
        """
        with patch('httpx.AsyncClient.get', mock_api_response(mock_soil_response)):
            location = get_test_locations(server)[0]
            args = {"latitude": location["lat"], "longitude": location["lon"]}
            result = await server._get_soil_conditions(args)
            
            # Verify response structure
            assert "location" in result, "Response missing 'location' field"
            assert "soil_conditions" in result, "Response missing 'soil_conditions' field"
            
            # Verify location structure
            self._assert_location_structure(result["location"])
            
            # Verify soil data structure
            soil_conditions = result["soil_conditions"]
            assert isinstance(soil_conditions, list), "Soil conditions should be a list"
            assert len(soil_conditions) > 0, "Soil conditions list should not be empty"
            
            # Check first soil condition entry
            first_condition = soil_conditions[0]
            assert "time" in first_condition, "Soil condition entry missing time"
            assert "temperature" in first_condition, "Soil condition entry missing temperature"
            assert "moisture" in first_condition, "Soil condition entry missing moisture"
            # Verify temperature data structure in first condition
            temp = first_condition["temperature"]
            assert isinstance(temp, dict), "Soil temperature should be a dictionary"
            assert "surface" in temp, "Soil temperature missing surface data"
            
            # Verify moisture data structure in first condition
            moisture = first_condition["moisture"]
            assert isinstance(moisture, dict), "Soil moisture should be a dictionary"
            assert "0_1cm" in moisture, "Soil moisture missing 0-1cm data"
            
            # Verify the nested structure for soil temperature and moisture matches mock data
            assert first_condition["temperature"]["surface"] == mock_soil_response["hourly"]["soil_temperature_0cm"][0], "Soil surface temperature mismatch"
            assert first_condition["moisture"]["0_1cm"] == mock_soil_response["hourly"]["soil_moisture_0_to_1cm"][0], "Soil moisture mismatch"

    @pytest.mark.anyio
    async def test_evapotranspiration_data(self, server: WeatherMCPServer, mock_et_response):
        """Test get_evapotranspiration_data tool with mocked API response.
        
        Verifies that the evapotranspiration endpoint correctly processes and returns
        daily evapotranspiration data for the requested period.
        
        Args:
            server: The WeatherMCPServer instance
            mock_et_response: Mock API response for evapotranspiration data
        """
        with patch('httpx.AsyncClient.get', mock_api_response(mock_et_response)):
            location = get_test_locations(server)[0]
            forecast_days = 5
            args = {"latitude": location["lat"], "longitude": location["lon"], "days": forecast_days}
            result = await server._get_evapotranspiration_data(args)
            
            assert "location" in result
            assert "daily_et" in result
            assert len(result["daily_et"]) == 5
            
            # Verify ET data matches our mock
            for i, day in enumerate(result["daily_et"]):
                assert day["date"] == mock_et_response["daily"]["time"][i]
                assert day["et0_fao"] == mock_et_response["daily"]["et0_fao_evapotranspiration"][i]

    @pytest.mark.anyio
    async def test_historical_weather(self, server: WeatherMCPServer, mock_historical_response):
        """Test get_historical_weather tool with mocked API response.
        
        Verifies that the historical weather endpoint correctly processes and returns
        historical weather data for the specified date range.
        
        Args:
            server: The WeatherMCPServer instance
            mock_historical_response: Mock API response for historical weather data
        """
        with patch('httpx.AsyncClient.get', mock_api_response(mock_historical_response)):
            location = get_test_locations(server)[0]
            end_date = datetime.now() - timedelta(days=30)
            start_date = end_date - timedelta(days=7)
            args = {
                "latitude": location["lat"],
                "longitude": location["lon"],
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            }
            result = await server._get_historical_weather(args)
            
            # Verify response structure
            assert "location" in result, "Response missing 'location' field"
            assert "historical_data" in result, "Response missing 'historical_data' field"
            
            # Verify location structure
            self._assert_location_structure(result["location"])
            
            # Verify historical data
            historical_data = result["historical_data"]
            assert isinstance(historical_data, list), "Historical data should be a list"
            assert len(historical_data) > 0, "Historical data list is empty"
            
            # Verify data structure of first historical entry
            if historical_data:
                day = historical_data[0]
                assert "date" in day, "Historical day missing date field"
                assert "temperature_max" in day, "Historical day missing max temperature"
                assert "temperature_min" in day, "Historical day missing min temperature"
                assert "precipitation" in day, "Historical day missing precipitation data"
            
            # Verify historical data matches our mock
            assert result["historical_data"][0]["date"] == mock_historical_response["daily"]["time"][0]
            assert result["historical_data"][0]["temperature_max"] == mock_historical_response["daily"]["temperature_2m_max"][0]

    @pytest.mark.anyio
    async def test_error_handling(self, server: WeatherMCPServer):
        """Test error handling for invalid arguments.
        
        Verifies that the server properly handles and raises exceptions for
        invalid or missing arguments.
        
        Args:
            server: The WeatherMCPServer instance
        """
        # Test with missing required arguments
        with pytest.raises(KeyError) as excinfo:
            await server._get_current_weather({})
        # The actual error is a KeyError for the missing latitude parameter
        assert "latitude" in str(excinfo.value), "Exception should be KeyError for missing latitude"
            
        # Test with invalid coordinates
        with pytest.raises(Exception) as excinfo:
            await server._get_current_weather({"latitude": 1000, "longitude": 1000})
        assert "coordinates" in str(excinfo.value).lower() or "latitude" in str(excinfo.value).lower() or \
               "longitude" in str(excinfo.value).lower(), \
            "Exception should mention invalid coordinates"
            
    @pytest.mark.anyio
    async def test_api_error_handling(self, server: WeatherMCPServer):
        """Test error handling for API errors.
        
        Verifies that the server properly handles and raises exceptions for
        external API errors with appropriate error messages.
        
        Args:
            server: The WeatherMCPServer instance
        """
        # Test with API error
        error_code = 500
        error_message = "Internal Server Error"
        with patch('httpx.AsyncClient.get', mock_api_error(status_code=error_code, error_message=error_message)):
            location = get_test_locations(server)[0]
            args = {"latitude": location["lat"], "longitude": location["lon"]}
            
            with pytest.raises(Exception) as excinfo:
                await server._get_current_weather(args)
                
            # Verify error message contains status code and/or error message
            error_str = str(excinfo.value).lower()
            assert str(error_code) in error_str or "error" in error_str, \
                "Exception should mention the API error status code or error message"

# Test for invalid region configuration
def test_invalid_region_config():
    """Test that invalid region configuration raises an error.
    
    Verifies that the server properly validates region configuration
    and raises appropriate exceptions for invalid configurations.
    """
    with pytest.raises(Exception) as excinfo:
        WeatherMCPServer(region_config={"invalid": "config"})
    
    # Verify error message mentions configuration issue
    error_str = str(excinfo.value).lower()
    assert "region" in error_str or "config" in error_str or "invalid" in error_str, \
        "Exception should mention invalid region configuration"

# Additional unit tests for specific components
class TestServerComponents:
    """Test suite for specific components of the WeatherMCPServer.
    
    This class contains tests for individual components and utility methods
    of the WeatherMCPServer class, such as region configuration and coordinate validation.
    """
    
    def test_region_configuration(self):
        """Test that regions are configured correctly.
        
        Verifies that the server properly configures regions based on predefined regions,
        custom region bounds, or no region specification.
        """
        # Test with predefined region
        server = WeatherMCPServer(region="indonesia")
        assert server.region_name == "indonesia", "Region name should match input for predefined region"
        assert server.region_bounds == PREDEFINED_REGIONS["indonesia"], "Region bounds should match predefined bounds"
        
        # Test with custom region
        custom_region = {"lat_min": 10.0, "lat_max": 20.0, "lon_min": 100.0, "lon_max": 110.0}
        server = WeatherMCPServer(region=custom_region)
        assert server.region_name == "Custom", "Region name should be 'Custom' for custom region bounds"
        assert server.region_bounds == custom_region, "Region bounds should match custom bounds"
        
        # Test with no region
        server = WeatherMCPServer(region="none")
        assert server.region_name == "None", "Region name should be 'None' when no region is specified"
        assert server.region_bounds is None, "Region bounds should be None when no region is specified"
        
    def test_coordinate_validation(self):
        """Test coordinate validation logic.
        
        Verifies that the server properly validates coordinates based on region bounds
        and returns appropriate boolean values.
        """
        # Test with predefined region (Indonesia)
        server = WeatherMCPServer(region="indonesia")
        
        # Valid coordinates within Indonesia
        assert server._validate_coordinates(0.0, 120.0) is True, \
            "Coordinates within region bounds should be valid"
        
        # Invalid coordinates outside Indonesia
        assert server._validate_coordinates(50.0, 50.0) is False, \
            "Coordinates outside region bounds should be invalid"
            
        # Test with no region bounds
        server = WeatherMCPServer(region="none")
        assert server._validate_coordinates(50.0, 50.0) is True, \
            "All coordinates should be valid when no region bounds are specified"
