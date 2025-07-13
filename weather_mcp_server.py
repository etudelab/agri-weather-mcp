#!/usr/bin/env python3
"""
Weather MCP Server for Agricultural Applications in Indonesia

This MCP server provides comprehensive weather data and agricultural intelligence
using the Open-Meteo API. It's specifically designed to support farming operations,
cultivation planning, and agricultural decision-making in Indonesia.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Union, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from weather_mcp.api.open_meteo import OpenMeteoAPI
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PREDEFINED_REGIONS = {
    "indonesia": {
        "lat_min": -11.0, "lat_max": 6.0,
        "lon_min": 95.0, "lon_max": 141.0
    },
    "south_east_asia": {
        "lat_min": -10.0, "lat_max": 28.0,
        "lon_min": 90.0, "lon_max": 141.0
    },
    "australia": {
        "lat_min": -44.0, "lat_max": -10.0,
        "lon_min": 112.0, "lon_max": 154.0
    },
    "india": {
        "lat_min": 6.0, "lat_max": 37.0,
        "lon_min": 68.0, "lon_max": 98.0
    }
}

class WeatherMCPServer:
    """Main Weather MCP Server class"""

    def __init__(
        self, 
        region: Union[str, Dict[str, float], None] = "indonesia",
        api: Optional[OpenMeteoAPI] = None
    ):
        self.server = Server("weather-mcp")
        self.api = api or OpenMeteoAPI()
        self._configure_region(region)
        self._setup_tools()

    def _configure_region(self, region_config: Union[str, Dict[str, float], None]):
        """Configure the geographical restriction"""
        self.region_name = "None"
        self.region_bounds = None

        if isinstance(region_config, str) and region_config.lower() != 'none':
            region_key = region_config.lower().replace(" ", "_")
            if region_key in PREDEFINED_REGIONS:
                self.region_name = region_config
                self.region_bounds = PREDEFINED_REGIONS[region_key]
            else:
                raise ValueError(f"Unknown predefined region: {region_config}")
        elif isinstance(region_config, dict):
            required_keys = ["lat_min", "lat_max", "lon_min", "lon_max"]
            if all(key in region_config for key in required_keys):
                self.region_name = "Custom"
                self.region_bounds = region_config
            else:
                raise ValueError("Custom region dictionary is missing required keys.")

    def _setup_tools(self):
        """Register all available tools"""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List all available weather tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_current_weather",
                        description="Get current weather conditions for a location with agriculture-specific data",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate",
                                    "minimum": -90.0,
                                    "maximum": 90.0
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate",
                                    "minimum": -180.0,
                                    "maximum": 180.0
                                },
                                "include_soil_data": {
                                    "type": "boolean",
                                    "description": "Flag to include soil data in the response",
                                    "default": True
                                }
                            },
                            "required": ["latitude", "longitude"]
                        }
                    ),
                    Tool(
                        name="get_weather_forecast",
                        description="Get a 5-day weather forecast for a location",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate",
                                    "minimum": -90.0,
                                    "maximum": 90.0
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate",
                                    "minimum": -180.0,
                                    "maximum": 180.0
                                },
                                "days": {
                                    "type": "integer",
                                    "description": "Number of forecast days (1-7)",
                                    "minimum": 1,
                                    "maximum": 7,
                                    "default": 5
                                },
                                "include_hourly": {
                                    "type": "boolean",
                                    "description": "Flag to include hourly forecast data",
                                    "default": True
                                }
                            },
                            "required": ["latitude", "longitude"]
                        }
                    ),
                    Tool(
                        name="get_agricultural_alerts",
                        description="Get agricultural alerts for a location based on crop and growth stage",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate",
                                    "minimum": -90.0,
                                    "maximum": 90.0
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate",
                                    "minimum": -180.0,
                                    "maximum": 180.0
                                },
                                "crop_type": {
                                    "type": "string",
                                    "description": "Type of crop (e.g., rice, corn, vegetables)",
                                    "enum": ["rice", "corn", "vegetables"],
                                    "default": "rice"
                                },
                                "growth_stage": {
                                    "type": "string",
                                    "description": "Current growth stage of the crop",
                                    "enum": ["planting", "vegetative", "flowering", "harvesting"],
                                    "default": "vegetative"
                                }
                            },
                            "required": ["latitude", "longitude", "crop_type", "growth_stage"]
                        }
                    ),
                    Tool(
                        name="get_soil_conditions",
                        description="Get soil temperature and moisture forecast for a location",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate",
                                    "minimum": -90.0,
                                    "maximum": 90.0
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate",
                                    "minimum": -180.0,
                                    "maximum": 180.0
                                },
                                "forecast_days": {
                                    "type": "integer",
                                    "description": "Number of days for soil forecast (1-3)",
                                    "minimum": 1,
                                    "maximum": 3,
                                    "default": 3
                                }
                            },
                            "required": ["latitude", "longitude"]
                        }
                    ),
                    Tool(
                        name="get_evapotranspiration_data",
                        description="Get evapotranspiration (ET) data for a location",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate",
                                    "minimum": -90.0,
                                    "maximum": 90.0
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate",
                                    "minimum": -180.0,
                                    "maximum": 180.0
                                },
                                "days": {
                                    "type": "integer",
                                    "description": "Number of days for ET forecast (1-7)",
                                    "minimum": 1,
                                    "maximum": 7,
                                    "default": 7
                                }
                            },
                            "required": ["latitude", "longitude"]
                        }
                    ),
                    Tool(
                        name="get_historical_weather",
                        description="Get historical weather data for a location",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate",
                                    "minimum": -90.0,
                                    "maximum": 90.0
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate",
                                    "minimum": -180.0,
                                    "maximum": 180.0
                                },
                                "start_date": {
                                    "type": "string",
                                    "description": "Start date for historical data (YYYY-MM-DD)",
                                    "format": "date"
                                },
                                "end_date": {
                                    "type": "string",
                                    "description": "End date for historical data (YYYY-MM-DD)",
                                    "format": "date"
                                }
                            },
                            "required": ["latitude", "longitude", "start_date", "end_date"]
                        }
                    ),
                    Tool(
                        name="get_supported_region",
                        description="Get the currently configured geographical region restriction",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    )
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool execution requests"""
            try:
                if request.name == "get_current_weather":
                    result = await self._get_current_weather(request.arguments)
                elif request.name == "get_weather_forecast":
                    result = await self._get_weather_forecast(request.arguments)
                elif request.name == "get_agricultural_alerts":
                    result = await self._get_agricultural_alerts(request.arguments)
                elif request.name == "get_soil_conditions":
                    result = await self._get_soil_conditions(request.arguments)
                elif request.name == "get_evapotranspiration_data":
                    result = await self._get_evapotranspiration_data(request.arguments)
                elif request.name == "get_historical_weather":
                    result = await self._get_historical_weather(request.arguments)
                elif request.name == "get_supported_region":
                    result = await self.get_supported_region()
                else:
                    raise ValueError(f"Unknown tool: {request.name}")

                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])

            except Exception as e:
                logger.error(f"Error executing tool {request.name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )

    def _validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validate coordinates are within the configured region bounds"""
        if not self.region_bounds:
            return True  # No restriction

        return (
            self.region_bounds["lat_min"] <= lat <= self.region_bounds["lat_max"] and
            self.region_bounds["lon_min"] <= lon <= self.region_bounds["lon_max"]
        )



    async def _get_current_weather(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current weather conditions"""
        lat = args["latitude"]
        lon = args["longitude"]
        include_soil = args.get("include_soil_data", True)

        if not self._validate_coordinates(lat, lon):
            raise ValueError(f"Coordinates are outside the configured region: {self.region_name}")

        # Define current weather parameters
        current_params = [
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "precipitation", "weather_code", "cloud_cover", "pressure_msl",
            "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
        ]

        if include_soil:
            current_params.extend([
                "soil_temperature_0cm", "soil_temperature_6cm",
                "soil_temperature_18cm", "soil_temperature_54cm",
                "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm",
                "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm"
            ])

        params = {
            "latitude": lat,
            "longitude": lon,
            "current": ",".join(current_params),
            "timezone": "auto"
        }

        data = await self.api.forecast(params)

        # Process and enhance the data
        current = data.get("current", {})
        result = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "timezone": data.get("timezone", ""),
                "elevation": data.get("elevation", 0)
            },
            "current_time": current.get("time", ""),
            "weather": {
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "apparent_temperature": current.get("apparent_temperature"),
                "precipitation": current.get("precipitation", 0),
                "weather_code": current.get("weather_code"),
                "cloud_cover": current.get("cloud_cover"),
                "pressure": current.get("pressure_msl"),
                "wind_speed": current.get("wind_speed_10m"),
                "wind_direction": current.get("wind_direction_10m"),
                "wind_gusts": current.get("wind_gusts_10m")
            }
        }

        if include_soil:
            result["soil"] = {
                "temperature": {
                    "surface": current.get("soil_temperature_0cm"),
                    "6cm": current.get("soil_temperature_6cm"),
                    "18cm": current.get("soil_temperature_18cm"),
                    "54cm": current.get("soil_temperature_54cm")
                },
                "moisture": {
                    "0_1cm": current.get("soil_moisture_0_to_1cm"),
                    "1_3cm": current.get("soil_moisture_1_to_3cm"),
                    "3_9cm": current.get("soil_moisture_3_to_9cm"),
                    "9_27cm": current.get("soil_moisture_9_to_27cm")
                }
            }

        return result

    async def _get_weather_forecast(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather forecast"""
        lat = args["latitude"]
        lon = args["longitude"]
        days = args.get("days", 7)
        include_hourly = args.get("include_hourly", True)

        if not self._validate_coordinates(lat, lon):
            raise ValueError(f"Coordinates are outside the configured region: {self.region_name}")

        # Define forecast parameters
        daily_params = [
            "temperature_2m_max", "temperature_2m_min", "precipitation_sum",
            "precipitation_probability_max", "wind_speed_10m_max",
            "wind_gusts_10m_max", "weather_code", "sunrise", "sunset"
        ]

        hourly_params = [
            "temperature_2m", "relative_humidity_2m", "precipitation",
            "weather_code", "wind_speed_10m", "soil_temperature_0cm",
            "soil_moisture_0_to_1cm", "evapotranspiration", "et0_fao_evapotranspiration"
        ] if include_hourly else []

        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ",".join(daily_params),
            "forecast_days": days,
            "timezone": "auto"
        }

        if include_hourly:
            params["hourly"] = ",".join(hourly_params)

        data = await self.api.forecast(params)

        result = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "timezone": data.get("timezone", ""),
                "elevation": data.get("elevation", 0)
            },
            "forecast_days": days,
            "daily_forecast": []
        }

        # Process daily forecast
        daily_data = data.get("daily", {})
        if daily_data:
            times = daily_data.get("time", [])
            for i, time in enumerate(times):
                day_forecast = {
                    "date": time,
                    "temperature_max": daily_data.get("temperature_2m_max", [])[i] if i < len(daily_data.get("temperature_2m_max", [])) else None,
                    "temperature_min": daily_data.get("temperature_2m_min", [])[i] if i < len(daily_data.get("temperature_2m_min", [])) else None,
                    "precipitation": daily_data.get("precipitation_sum", [])[i] if i < len(daily_data.get("precipitation_sum", [])) else None,
                    "precipitation_probability": daily_data.get("precipitation_probability_max", [])[i] if i < len(daily_data.get("precipitation_probability_max", [])) else None,
                    "wind_speed_max": daily_data.get("wind_speed_10m_max", [])[i] if i < len(daily_data.get("wind_speed_10m_max", [])) else None,
                    "weather_code": daily_data.get("weather_code", [])[i] if i < len(daily_data.get("weather_code", [])) else None,
                    "sunrise": daily_data.get("sunrise", [])[i] if i < len(daily_data.get("sunrise", [])) else None,
                    "sunset": daily_data.get("sunset", [])[i] if i < len(daily_data.get("sunset", [])) else None
                }
                result["daily_forecast"].append(day_forecast)

        # Process hourly forecast if requested
        if include_hourly:
            result["hourly_forecast"] = []
            hourly_data = data.get("hourly", {})
            if hourly_data:
                times = hourly_data.get("time", [])
                for i, time in enumerate(times):
                    hour_forecast = {
                        "time": time,
                        "temperature": hourly_data.get("temperature_2m", [])[i] if i < len(hourly_data.get("temperature_2m", [])) else None,
                        "humidity": hourly_data.get("relative_humidity_2m", [])[i] if i < len(hourly_data.get("relative_humidity_2m", [])) else None,
                        "precipitation": hourly_data.get("precipitation", [])[i] if i < len(hourly_data.get("precipitation", [])) else None,
                        "wind_speed": hourly_data.get("wind_speed_10m", [])[i] if i < len(hourly_data.get("wind_speed_10m", [])) else None,
                        "soil_temperature": hourly_data.get("soil_temperature_0cm", [])[i] if i < len(hourly_data.get("soil_temperature_0cm", [])) else None,
                        "soil_moisture": hourly_data.get("soil_moisture_0_to_1cm", [])[i] if i < len(hourly_data.get("soil_moisture_0_to_1cm", [])) else None,
                        "evapotranspiration": hourly_data.get("evapotranspiration", [])[i] if i < len(hourly_data.get("evapotranspiration", [])) else None,
                        "et0_fao": hourly_data.get("et0_fao_evapotranspiration", [])[i] if i < len(hourly_data.get("et0_fao_evapotranspiration", [])) else None
                    }
                    result["hourly_forecast"].append(hour_forecast)

        return result

    async def _get_agricultural_alerts(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate agricultural alerts and recommendations"""
        lat = args["latitude"]
        lon = args["longitude"]
        crop_type = args.get("crop_type", "general")
        growth_stage = args.get("growth_stage", "vegetative")

        if not self._validate_coordinates(lat, lon):
            raise ValueError(f"Coordinates are outside the configured region: {self.region_name}")

        # Get current weather and 7-day forecast for analysis
        current_args = {"latitude": lat, "longitude": lon, "include_soil_data": True}
        forecast_args = {"latitude": lat, "longitude": lon, "days": 7, "include_hourly": True}

        current_weather = await self._get_current_weather(current_args)
        forecast = await self._get_weather_forecast(forecast_args)

        alerts = []
        recommendations = []

        # Analyze current conditions
        current = current_weather["weather"]
        soil = current_weather.get("soil", {})

        # Temperature alerts
        temp = current.get("temperature")
        if temp is not None:
            if temp > 35:
                alerts.append({
                    "type": "heat_stress",
                    "severity": "high",
                    "message": f"High temperature alert: {temp}°C. Risk of heat stress for crops.",
                    "recommendations": ["Increase irrigation frequency", "Provide shade if possible", "Monitor plants for wilting"]
                })
            elif temp < 15:
                alerts.append({
                    "type": "cold_stress",
                    "severity": "medium",
                    "message": f"Low temperature alert: {temp}°C. Potential cold stress for tropical crops.",
                    "recommendations": ["Consider protective covering", "Delay planting if in planning stage"]
                })

        # Precipitation analysis
        precip = current.get("precipitation", 0)
        if precip > 20:
            alerts.append({
                "type": "heavy_rain",
                "severity": "medium",
                "message": f"Heavy rainfall detected: {precip}mm. Risk of waterlogging.",
                "recommendations": ["Ensure proper drainage", "Delay field operations", "Monitor for fungal diseases"]
            })

        # Soil moisture analysis
        if soil:
            surface_moisture = soil.get("moisture", {}).get("0_1cm")
            if surface_moisture is not None:
                if surface_moisture < 0.1:
                    alerts.append({
                        "type": "drought_stress",
                        "severity": "high",
                        "message": f"Low soil moisture: {surface_moisture:.3f} m³/m³. Irrigation needed.",
                        "recommendations": ["Immediate irrigation required", "Check irrigation system", "Consider mulching"]
                    })
                elif surface_moisture > 0.4:
                    alerts.append({
                        "type": "waterlogged",
                        "severity": "medium",
                        "message": f"High soil moisture: {surface_moisture:.3f} m³/m³. Risk of waterlogging.",
                        "recommendations": ["Improve drainage", "Avoid heavy machinery", "Monitor for root diseases"]
                    })

        # Wind alerts
        wind_speed = current.get("wind_speed", 0)
        wind_gusts = current.get("wind_gusts", 0)
        if wind_gusts > 50:
            alerts.append({
                "type": "strong_wind",
                "severity": "high",
                "message": f"Strong wind gusts: {wind_gusts} km/h. Risk of crop damage.",
                "recommendations": ["Secure tall crops", "Delay spraying operations", "Check for physical damage"]
            })

        # Forecast-based alerts
        daily_forecast = forecast.get("daily_forecast", [])
        if daily_forecast:
            # Check for upcoming dry spell
            dry_days = 0
            for day in daily_forecast[:7]:
                if day.get("precipitation", 0) < 1:
                    dry_days += 1
                else:
                    break

            if dry_days >= 5:
                alerts.append({
                    "type": "dry_spell",
                    "severity": "medium",
                    "message": f"Extended dry period forecast: {dry_days} days without significant rain.",
                    "recommendations": ["Plan irrigation schedule", "Check water reserves", "Consider drought-resistant practices"]
                })

        # Crop-specific recommendations
        crop_recommendations = self._get_crop_specific_recommendations(crop_type, growth_stage, current_weather, forecast)
        recommendations.extend(crop_recommendations)

        return {
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "crop_info": {
                "type": crop_type,
                "growth_stage": growth_stage
            },
            "alerts": alerts,
            "recommendations": recommendations,
            "analysis_time": datetime.now().isoformat()
        }

    def _get_crop_specific_recommendations(self, crop_type: str, growth_stage: str, current_weather: Dict, forecast: Dict) -> List[Dict]:
        """Generate crop-specific recommendations"""
        recommendations = []

        current = current_weather["weather"]
        temp = current.get("temperature", 0)
        humidity = current.get("relative_humidity_2m", 0)

        if crop_type == "rice":
            if growth_stage == "planting":
                if temp >= 20 and temp <= 35:
                    recommendations.append({
                        "type": "optimal_conditions",
                        "message": "Temperature conditions are optimal for rice planting.",
                        "action": "Proceed with planting operations"
                    })

            elif growth_stage == "flowering":
                if temp > 35:
                    recommendations.append({
                        "type": "heat_stress_prevention",
                        "message": "High temperatures during flowering can reduce yield.",
                        "action": "Maintain adequate water levels and consider evening irrigation"
                    })

        elif crop_type == "corn":
            if growth_stage == "vegetative":
                if humidity > 80:
                    recommendations.append({
                        "type": "disease_prevention",
                        "message": "High humidity increases risk of fungal diseases in corn.",
                        "action": "Monitor for leaf blight and ensure good air circulation"
                    })

        elif crop_type == "vegetables":
            if temp > 30:
                recommendations.append({
                    "type": "heat_protection",
                    "message": "High temperatures can stress vegetable crops.",
                    "action": "Consider shade cloth and increase watering frequency"
                })

        return recommendations

    async def _get_soil_conditions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed soil conditions"""
        lat = args["latitude"]
        lon = args["longitude"]
        forecast_days = args.get("forecast_days", 3)

        if not self._validate_coordinates(lat, lon):
            raise ValueError(f"Coordinates are outside the configured region: {self.region_name}")

        # Get soil-specific parameters
        hourly_params = [
            "soil_temperature_0cm", "soil_temperature_6cm",
            "soil_temperature_18cm", "soil_temperature_54cm",
            "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm",
            "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm",
            "soil_moisture_27_to_81cm"
        ]

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ",".join(hourly_params),
            "forecast_days": forecast_days,
            "timezone": "auto"
        }

        data = await self.api.forecast(params)

        result = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "timezone": data.get("timezone", ""),
                "elevation": data.get("elevation", 0)
            },
            "forecast_days": forecast_days,
            "soil_conditions": []
        }

        # Process hourly soil data
        hourly_data = data.get("hourly", {})
        if hourly_data:
            times = hourly_data.get("time", [])
            for i, time in enumerate(times):
                soil_condition = {
                    "time": time,
                    "temperature": {
                        "surface": hourly_data.get("soil_temperature_0cm", [])[i] if i < len(hourly_data.get("soil_temperature_0cm", [])) else None,
                        "6cm": hourly_data.get("soil_temperature_6cm", [])[i] if i < len(hourly_data.get("soil_temperature_6cm", [])) else None,
                        "18cm": hourly_data.get("soil_temperature_18cm", [])[i] if i < len(hourly_data.get("soil_temperature_18cm", [])) else None,
                        "54cm": hourly_data.get("soil_temperature_54cm", [])[i] if i < len(hourly_data.get("soil_temperature_54cm", [])) else None
                    },
                    "moisture": {
                        "0_1cm": hourly_data.get("soil_moisture_0_to_1cm", [])[i] if i < len(hourly_data.get("soil_moisture_0_to_1cm", [])) else None,
                        "1_3cm": hourly_data.get("soil_moisture_1_to_3cm", [])[i] if i < len(hourly_data.get("soil_moisture_1_to_3cm", [])) else None,
                        "3_9cm": hourly_data.get("soil_moisture_3_to_9cm", [])[i] if i < len(hourly_data.get("soil_moisture_3_to_9cm", [])) else None,
                        "9_27cm": hourly_data.get("soil_moisture_9_to_27cm", [])[i] if i < len(hourly_data.get("soil_moisture_9_to_27cm", [])) else None,
                        "27_81cm": hourly_data.get("soil_moisture_27_to_81cm", [])[i] if i < len(hourly_data.get("soil_moisture_27_to_81cm", [])) else None
                    }
                }
                result["soil_conditions"].append(soil_condition)

        return result

    async def _get_evapotranspiration_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get evapotranspiration data"""
        lat = args["latitude"]
        lon = args["longitude"]
        days = args.get("days", 7)

        if not self._validate_coordinates(lat, lon):
            raise ValueError(f"Coordinates are outside the configured region: {self.region_name}")

        # Get ET-specific parameters
        hourly_params = [
            "evapotranspiration", "et0_fao_evapotranspiration",
            "vapour_pressure_deficit", "temperature_2m",
            "relative_humidity_2m", "wind_speed_10m",
            "shortwave_radiation"
        ]

        daily_params = [
            "et0_fao_evapotranspiration"
        ]

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ",".join(hourly_params),
            "daily": ",".join(daily_params),
            "forecast_days": days,
            "timezone": "auto"
        }

        data = await self.api.forecast(params)

        result = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "timezone": data.get("timezone", ""),
                "elevation": data.get("elevation", 0)
            },
            "forecast_days": days,
            "daily_et": [],
            "hourly_et": []
        }

        # Process daily ET data
        daily_data = data.get("daily", {})
        if daily_data:
            times = daily_data.get("time", [])
            et0_values = daily_data.get("et0_fao_evapotranspiration", [])
            for i, time in enumerate(times):
                daily_et = {
                    "date": time,
                    "et0_fao": et0_values[i] if i < len(et0_values) else None
                }
                result["daily_et"].append(daily_et)

        # Process hourly ET data
        hourly_data = data.get("hourly", {})
        if hourly_data:
            times = hourly_data.get("time", [])
            for i, time in enumerate(times):
                hourly_et = {
                    "time": time,
                    "evapotranspiration": hourly_data.get("evapotranspiration", [])[i] if i < len(hourly_data.get("evapotranspiration", [])) else None,
                    "et0_fao": hourly_data.get("et0_fao_evapotranspiration", [])[i] if i < len(hourly_data.get("et0_fao_evapotranspiration", [])) else None,
                    "vpd": hourly_data.get("vapour_pressure_deficit", [])[i] if i < len(hourly_data.get("vapour_pressure_deficit", [])) else None,
                    "temperature": hourly_data.get("temperature_2m", [])[i] if i < len(hourly_data.get("temperature_2m", [])) else None,
                    "humidity": hourly_data.get("relative_humidity_2m", [])[i] if i < len(hourly_data.get("relative_humidity_2m", [])) else None,
                    "wind_speed": hourly_data.get("wind_speed_10m", [])[i] if i < len(hourly_data.get("wind_speed_10m", [])) else None,
                    "solar_radiation": hourly_data.get("shortwave_radiation", [])[i] if i < len(hourly_data.get("shortwave_radiation", [])) else None
                }
                result["hourly_et"].append(hourly_et)

        return result

    async def _get_historical_weather(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical weather data"""
        lat = args["latitude"]
        lon = args["longitude"]
        start_date = args["start_date"]
        end_date = args["end_date"]

        if not self._validate_coordinates(lat, lon):
            raise ValueError(f"Coordinates are outside the configured region: {self.region_name}")

        # Historical weather parameters
        daily_params = [
            "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean",
            "precipitation_sum", "wind_speed_10m_max", "wind_direction_10m_dominant"
        ]

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ",".join(daily_params),
            "timezone": "auto",
            "models": "era5"
        }

        data = await self.api.archive(params)

        result = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "timezone": data.get("timezone", ""),
                "elevation": data.get("elevation", 0)
            },
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "historical_data": []
        }

        # Process historical data
        daily_data = data.get("daily", {})
        if daily_data:
            times = daily_data.get("time", [])
            for i, time in enumerate(times):
                historical_day = {
                    "date": time,
                    "temperature_max": daily_data.get("temperature_2m_max", [])[i] if i < len(daily_data.get("temperature_2m_max", [])) else None,
                    "temperature_min": daily_data.get("temperature_2m_min", [])[i] if i < len(daily_data.get("temperature_2m_min", [])) else None,
                    "temperature_mean": daily_data.get("temperature_2m_mean", [])[i] if i < len(daily_data.get("temperature_2m_mean", [])) else None,
                    "precipitation": daily_data.get("precipitation_sum", [])[i] if i < len(daily_data.get("precipitation_sum", [])) else None,
                    "wind_speed_max": daily_data.get("wind_speed_10m_max", [])[i] if i < len(daily_data.get("wind_speed_10m_max", [])) else None,
                    "wind_direction": daily_data.get("wind_direction_10m_dominant", [])[i] if i < len(daily_data.get("wind_direction_10m_dominant", [])) else None
                }
                result["historical_data"].append(historical_day)

        return result

    async def get_supported_region(self) -> Dict[str, Any]:
        """Get the currently configured geographical region restriction."""
        return {
            "region_name": self.region_name,
            "bounding_box": self.region_bounds
        }

    async def run(self):
        """Run the MCP server"""
        async with self.api:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="weather-mcp",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=None,
                            experimental_capabilities=None,
                        ),
                    ),
                )

async def main():
    """Main entry point"""
    server = WeatherMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
