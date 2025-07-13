"""
Pytest configuration and fixtures for the agri-weather-mcp project.
"""
import asyncio
import pytest
from typing import Dict, Any, List, Union

from weather_mcp.server.weather_mcp_server import WeatherMCPServer, PREDEFINED_REGIONS

# Test configurations for different regions
TEST_CONFIGS = [
    "indonesia",
    "south_east_asia",
    "australia",
    "india",
    pytest.param(
        {"lat_min": 40.0, "lat_max": 50.0, "lon_min": -120.0, "lon_max": -110.0},
        id="custom_region"
    ),
    "none"
]

def get_test_locations(server: WeatherMCPServer) -> List[Dict[str, Any]]:
    """Generates test locations based on the server's configured region."""
    # This function is now implemented in test_utils.py
    # We keep this here for backward compatibility
    from test_utils import get_test_locations as get_locations
    return get_locations(server)

@pytest.fixture(params=TEST_CONFIGS)
def region_config(request):
    """Pytest fixture to provide region configurations."""
    return request.param

@pytest.fixture
def server(region_config):
    """Pytest fixture to create a WeatherMCPServer instance for a given region."""
    from test_utils import mock_open_meteo_api
    # Create server with mocked API to avoid real HTTP calls
    mock_api = mock_open_meteo_api()
    return WeatherMCPServer(region=region_config, api=mock_api)

@pytest.fixture
def mock_weather_response():
    """Fixture providing a mock weather API response."""
    return {
        "location": {
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
            "elevation": 10.0
        },
        "current_time": "2025-07-08T12:00",
        "weather": {
            "temperature": 28.5,
            "humidity": 75.0,
            "apparent_temperature": 32.0,
            "precipitation": 0.0,
            "weather_code": 2,
            "cloud_cover": 70,
            "pressure": 1010.5,
            "wind_speed": 5.0,
            "wind_direction": 180,
            "wind_gusts": 15.0
        },
        "soil": {
            "temperature": {
                "surface": 30.0,
                "6cm": 28.0,
                "18cm": 26.0,
                "54cm": 24.0
            },
            "moisture": {
                "0_1cm": 0.25,
                "1_3cm": 0.28,
                "3_9cm": 0.30,
                "9_27cm": 0.32
            }
        },
        # Keep these for backward compatibility with tests
        "latitude": 0.0,
        "longitude": 0.0,
        "current": {
            "temperature_2m": 28.5,
            "relative_humidity_2m": 75.0,
            "precipitation": 0.0,
            "wind_speed_10m": 5.0,
            "wind_direction_10m": 180,
            "soil_temperature": 30.0,
            "soil_temperature_0cm": 30.0,
            "soil_moisture_0_to_1cm": 0.25
        },
        "location": "Test Location"
    }

@pytest.fixture
def mock_forecast_response():
    """Fixture providing a mock forecast API response."""
    return {
        "location": {
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
            "elevation": 10.0,
            "name": "Test Location"
        },
        "forecast_days": 3,
        "daily_forecast": [
            {
                "date": "2025-07-08",
                "temperature_max": 32.0,
                "temperature_min": 25.0,
                "precipitation": 0.0,
                "precipitation_probability": 0,
                "weather_code": 0,
                "sunrise": "06:00",
                "sunset": "18:00",
                "wind_speed_max": 10.0,
                "wind_direction": 180
            },
            {
                "date": "2025-07-09",
                "temperature_max": 31.5,
                "temperature_min": 24.5,
                "precipitation": 5.2,
                "precipitation_probability": 60,
                "weather_code": 80,
                "sunrise": "06:01",
                "sunset": "18:01",
                "wind_speed_max": 12.5,
                "wind_direction": 200
            },
            {
                "date": "2025-07-10",
                "temperature_max": 30.8,
                "temperature_min": 24.0,
                "precipitation": 10.5,
                "precipitation_probability": 80,
                "weather_code": 95,
                "sunrise": "06:02",
                "sunset": "18:02",
                "wind_speed_max": 15.0,
                "wind_direction": 220
            }
        ],
        # Keep these for backward compatibility with tests
        "daily": {
            "time": ["2025-07-08", "2025-07-09", "2025-07-10"],
            "temperature_2m_max": [32.0, 31.5, 30.8],
            "temperature_2m_min": [25.0, 24.5, 24.0],
            "precipitation_sum": [0.0, 5.2, 10.5],
            "precipitation_probability_max": [0, 60, 80],
            "wind_speed_10m_max": [10.0, 12.5, 15.0],
            "wind_direction_10m_dominant": [180, 200, 220]
        }
    }

@pytest.fixture
def mock_soil_response():
    """Fixture providing a mock soil conditions API response."""
    return {
        "location": {
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
            "elevation": 10.0,
            "name": "Test Location"
        },
        "soil_conditions": [
            {
                "time": "2025-07-08T00:00",
                "temperature": {
                    "surface": 30.0,
                    "6cm": 28.0,
                    "18cm": 26.0,
                    "54cm": 24.0
                },
                "moisture": {
                    "0_1cm": 0.25,
                    "1_3cm": 0.28,
                    "3_9cm": 0.30,
                    "9_27cm": 0.32,
                    "27_81cm": 0.34
                }
            },
            {
                "time": "2025-07-08T01:00",
                "temperature": {
                    "surface": 29.8,
                    "6cm": 27.9,
                    "18cm": 25.9,
                    "54cm": 24.0
                },
                "moisture": {
                    "0_1cm": 0.25,
                    "1_3cm": 0.28,
                    "3_9cm": 0.30,
                    "9_27cm": 0.32,
                    "27_81cm": 0.34
                }
            },
            {
                "time": "2025-07-08T02:00",
                "temperature": {
                    "surface": 29.6,
                    "6cm": 27.8,
                    "18cm": 25.8,
                    "54cm": 24.0
                },
                "moisture": {
                    "0_1cm": 0.26,
                    "1_3cm": 0.29,
                    "3_9cm": 0.30,
                    "9_27cm": 0.32,
                    "27_81cm": 0.34
                }
            },
            {
                "time": "2025-07-08T03:00",
                "temperature": {
                    "surface": 29.4,
                    "6cm": 27.7,
                    "18cm": 25.7,
                    "54cm": 24.0
                },
                "moisture": {
                    "0_1cm": 0.26,
                    "1_3cm": 0.29,
                    "3_9cm": 0.30,
                    "9_27cm": 0.32,
                    "27_81cm": 0.34
                }
            }
        ],
        # Keep these for backward compatibility with tests
        "hourly": {
            "time": ["2025-07-08T00:00", "2025-07-08T01:00", "2025-07-08T02:00", "2025-07-08T03:00"],
            "soil_temperature_0cm": [30.0, 29.8, 29.6, 29.4],
            "soil_temperature_6cm": [28.0, 27.9, 27.8, 27.7],
            "soil_temperature_18cm": [26.0, 25.9, 25.8, 25.7],
            "soil_temperature_54cm": [24.0, 24.0, 24.0, 24.0],
            "soil_moisture_0_to_1cm": [0.25, 0.25, 0.26, 0.26],
            "soil_moisture_1_to_3cm": [0.28, 0.28, 0.29, 0.29],
            "soil_moisture_3_to_9cm": [0.30, 0.30, 0.30, 0.30],
            "soil_moisture_9_to_27cm": [0.32, 0.32, 0.32, 0.32],
            "soil_moisture_27_to_81cm": [0.34, 0.34, 0.34, 0.34]
        }
    }

@pytest.fixture
def mock_et_response():
    """Fixture providing a mock evapotranspiration API response."""
    return {
        "location": {
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
            "elevation": 10.0,
            "name": "Test Location"
        },
        "daily_et": [
            {
                "date": "2025-07-08",
                "et0_fao": 5.2,
                "solar_radiation": 280.5,
                "vapor_pressure_deficit": 1.2,
                "supporting_data": {
                    "temperature_max": 32.0,
                    "temperature_min": 25.0,
                    "humidity_max": 85.0,
                    "humidity_min": 60.0
                }
            },
            {
                "date": "2025-07-09",
                "et0_fao": 5.0,
                "solar_radiation": 275.0,
                "vapor_pressure_deficit": 1.1,
                "supporting_data": {
                    "temperature_max": 31.5,
                    "temperature_min": 24.5,
                    "humidity_max": 87.0,
                    "humidity_min": 62.0
                }
            },
            {
                "date": "2025-07-10",
                "et0_fao": 4.8,
                "solar_radiation": 260.0,
                "vapor_pressure_deficit": 1.0,
                "supporting_data": {
                    "temperature_max": 30.8,
                    "temperature_min": 24.0,
                    "humidity_max": 90.0,
                    "humidity_min": 65.0
                }
            },
            {
                "date": "2025-07-11",
                "et0_fao": 5.1,
                "solar_radiation": 278.0,
                "vapor_pressure_deficit": 1.15,
                "supporting_data": {
                    "temperature_max": 31.8,
                    "temperature_min": 24.8,
                    "humidity_max": 86.0,
                    "humidity_min": 61.0
                }
            },
            {
                "date": "2025-07-12",
                "et0_fao": 5.3,
                "solar_radiation": 285.0,
                "vapor_pressure_deficit": 1.25,
                "supporting_data": {
                    "temperature_max": 32.5,
                    "temperature_min": 25.5,
                    "humidity_max": 84.0,
                    "humidity_min": 58.0
                }
            }
        ],
        # Keep these for backward compatibility with tests
        "daily": {
            "time": ["2025-07-08", "2025-07-09", "2025-07-10", "2025-07-11", "2025-07-12"],
            "et0_fao_evapotranspiration": [5.2, 5.0, 4.8, 5.1, 5.3]
        }
    }

@pytest.fixture
def mock_historical_response():
    """Fixture providing a mock historical weather API response."""
    return {
        "location": {
            "latitude": 0.0,
            "longitude": 0.0,
            "timezone": "UTC",
            "elevation": 10.0,
            "name": "Test Location"
        },
        "historical_data": [
            {
                "date": "2025-06-08",
                "temperature_max": 31.0,
                "temperature_min": 24.0,
                "temperature_mean": 27.5,
                "precipitation": 2.0,
                "wind_speed_max": 8.0,
                "wind_direction": 190,
                "weather_code": 3,
                "humidity_mean": 75.0
            },
            {
                "date": "2025-06-09",
                "temperature_max": 30.5,
                "temperature_min": 23.5,
                "temperature_mean": 27.0,
                "precipitation": 0.0,
                "wind_speed_max": 7.5,
                "wind_direction": 185,
                "weather_code": 1,
                "humidity_mean": 70.0
            },
            {
                "date": "2025-06-10",
                "temperature_max": 29.8,
                "temperature_min": 23.0,
                "temperature_mean": 26.4,
                "precipitation": 1.5,
                "wind_speed_max": 9.0,
                "wind_direction": 200,
                "weather_code": 2,
                "humidity_mean": 72.0
            }
        ],
        # Keep these for backward compatibility with tests
        "daily": {
            "time": ["2025-06-08", "2025-06-09", "2025-06-10"],
            "temperature_2m_max": [31.0, 30.5, 29.8],
            "temperature_2m_min": [24.0, 23.5, 23.0],
            "temperature_2m_mean": [27.5, 27.0, 26.4],
            "precipitation_sum": [2.0, 0.0, 1.5],
            "wind_speed_10m_max": [8.0, 7.5, 9.0],
            "wind_direction_10m_dominant": [190, 185, 200]
        }
    }


@pytest.fixture
def mock_agricultural_alerts_response():
    """Fixture providing a mock agricultural alerts API response."""
    return {
        "location": {
            "latitude": 0.0,
            "longitude": 0.0,
            "name": "Test Location"
        },
        "crop_info": {
            "type": "rice",
            "growth_stage": "vegetative"
        },
        "alerts": [
            {
                "type": "waterlogged",
                "severity": "medium",
                "message": "High soil moisture: 0.418 m³/m³. Risk of waterlogging.",
                "recommendations": [
                    "Improve drainage",
                    "Avoid heavy machinery",
                    "Monitor for root diseases"
                ]
            },
            {
                "type": "heat_stress",
                "severity": "high",
                "message": "Temperature exceeding optimal range for rice growth. Current: 35°C",
                "recommendations": [
                    "Increase irrigation frequency",
                    "Apply mulch to reduce soil temperature",
                    "Consider shade structures if possible"
                ]
            },
            {
                "type": "pest_risk",
                "severity": "low",
                "message": "Current weather conditions favorable for rice stem borer activity",
                "recommendations": [
                    "Monitor fields regularly",
                    "Consider preventive measures",
                    "Consult local extension service for guidance"
                ]
            }
        ],
        "recommendations": [
            "Maintain optimal water levels for vegetative stage",
            "Monitor nitrogen levels",
            "Scout for early signs of pests and diseases"
        ],
        "analysis_time": "2025-07-08T12:06:01.814321"
    }


@pytest.fixture
def mock_weather_data():
    """
    Fixture providing a complete mock weather data set that matches Open-Meteo API format.
    
    This combines various aspects of other mock fixtures but provides a complete dataset
    for comprehensive testing of all weather-related functionality.
    
    Returns:
        Dict[str, Any]: A dictionary with mock weather data
    """
    return {
        "timezone": "Asia/Jakarta",
        "elevation": 8,
        "current": {
            "time": "2024-01-15T12:00:00Z",
            "temperature_2m": 28.5,
            "relative_humidity_2m": 75,
            "apparent_temperature": 32.1,
            "precipitation": 0,
            "weather_code": 0,
            "cloud_cover": 25,
            "pressure_msl": 1013.2,
            "wind_speed_10m": 8.5,
            "wind_direction_10m": 180,
            "wind_gusts_10m": 12.3,
            "soil_temperature_0cm": 26.8,
            "soil_temperature_6cm": 25.2,
            "soil_temperature_18cm": 24.6,
            "soil_temperature_54cm": 23.8,
            "soil_moisture_0_to_1cm": 0.25,
            "soil_moisture_1_to_3cm": 0.28,
            "soil_moisture_3_to_9cm": 0.32,
            "soil_moisture_9_to_27cm": 0.35,
            "soil_moisture_27_to_81cm": 0.38
        },
        "daily": {
            "time": ["2024-01-15", "2024-01-16", "2024-01-17", "2024-01-18", "2024-01-19"],
            "temperature_2m_max": [32.1, 31.8, 33.2, 29.5, 30.8],
            "temperature_2m_min": [24.2, 23.8, 25.1, 22.9, 24.5],
            "temperature_2m_mean": [28.1, 27.8, 29.2, 26.2, 27.7],
            "precipitation_sum": [0.0, 2.3, 0.0, 8.5, 1.2],
            "precipitation_probability_max": [10, 60, 20, 85, 40],
            "wind_speed_10m_max": [12.3, 14.2, 11.8, 16.5, 13.1],
            "wind_gusts_10m_max": [18.7, 21.5, 17.2, 24.8, 19.3],
            "wind_direction_10m_dominant": [180, 200, 165, 220, 190],
            "weather_code": [0, 61, 1, 63, 51],
            "sunrise": ["2024-01-15T06:05:00", "2024-01-16T06:05:00", "2024-01-17T06:06:00", "2024-01-18T06:06:00", "2024-01-19T06:07:00"],
            "sunset": ["2024-01-15T18:20:00", "2024-01-16T18:20:00", "2024-01-17T18:21:00", "2024-01-18T18:21:00", "2024-01-19T18:22:00"],
            "et0_fao_evapotranspiration": [4.2, 3.8, 4.5, 3.2, 3.9]
        },
        "hourly": {
            "time": [
                "2024-01-15T00:00:00", "2024-01-15T01:00:00", "2024-01-15T02:00:00", 
                "2024-01-15T03:00:00", "2024-01-15T04:00:00", "2024-01-15T05:00:00",
                "2024-01-15T06:00:00", "2024-01-15T07:00:00", "2024-01-15T08:00:00",
                "2024-01-15T09:00:00", "2024-01-15T10:00:00", "2024-01-15T11:00:00"
            ],
            "temperature_2m": [25.2, 24.8, 24.5, 24.2, 24.8, 25.5, 26.8, 27.9, 29.2, 30.1, 31.2, 32.1],
            "relative_humidity_2m": [82, 84, 85, 87, 85, 83, 78, 75, 72, 68, 65, 62],
            "precipitation": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "weather_code": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "wind_speed_10m": [5.2, 4.8, 4.5, 4.2, 4.8, 5.5, 6.8, 7.9, 8.2, 9.1, 9.8, 10.2],
            "soil_temperature_0cm": [24.2, 24.0, 23.8, 23.6, 23.8, 24.2, 25.1, 26.2, 27.1, 28.2, 28.8, 29.2],
            "soil_temperature_6cm": [23.8, 23.6, 23.4, 23.2, 23.4, 23.8, 24.6, 25.2, 25.8, 26.4, 26.8, 27.2],
            "soil_temperature_18cm": [23.2, 23.0, 22.8, 22.6, 22.8, 23.2, 23.8, 24.2, 24.6, 25.0, 25.2, 25.4],
            "soil_temperature_54cm": [22.8, 22.6, 22.4, 22.2, 22.4, 22.8, 23.2, 23.4, 23.6, 23.8, 24.0, 24.2],
            "soil_moisture_0_to_1cm": [0.28, 0.28, 0.27, 0.27, 0.27, 0.28, 0.28, 0.27, 0.26, 0.25, 0.24, 0.23],
            "soil_moisture_1_to_3cm": [0.32, 0.32, 0.31, 0.31, 0.31, 0.32, 0.32, 0.31, 0.30, 0.29, 0.28, 0.27],
            "soil_moisture_3_to_9cm": [0.35, 0.35, 0.34, 0.34, 0.34, 0.35, 0.35, 0.34, 0.33, 0.32, 0.31, 0.30],
            "soil_moisture_9_to_27cm": [0.38, 0.38, 0.37, 0.37, 0.37, 0.38, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33],
            "soil_moisture_27_to_81cm": [0.42, 0.42, 0.41, 0.41, 0.41, 0.42, 0.42, 0.41, 0.40, 0.39, 0.38, 0.37],
            "evapotranspiration": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
            "et0_fao_evapotranspiration": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65],
            "vapour_pressure_deficit": [0.2, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4],
            "shortwave_radiation": [0, 0, 0, 0, 0, 50, 150, 250, 350, 450, 550, 650]
        }
    }
