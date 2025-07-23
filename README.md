# Agri-Weather MCP

This project provides a comprehensive Weather Model Context Protocol (MCP) server specifically designed for agricultural applications. It leverages the free [Open-Meteo API](https://open-meteo.com/) to provide real-time weather data, forecasts, and agricultural intelligence to support farming operations, cultivation planning, and crop management decisions.

## Key Features

-   **Current Weather**: Get real-time, localized weather conditions, including temperature, humidity, precipitation, and soil data.
-   **Weather Forecast**: Access detailed 5-day weather forecasts with hourly granularity to support agricultural planning.
-   **Agricultural Alerts**: Receive crop-specific alerts and recommendations for various growth stages (e.g., planting, vegetative, flowering).
-   **Soil Conditions**: Retrieve detailed soil temperature and moisture information at multiple depths.
-   **Evapotranspiration Data**: Obtain evapotranspiration (ET) and reference ET₀ data for precise irrigation management.
-   **Historical Weather**: Access historical weather data for trend analysis and seasonal planning.

## Technology Stack

-   **Python 3.11+**
-   **MCP Server SDK**: Core framework for building the Model Context Protocol server.
-   **HTTPX**: For making asynchronous HTTP requests to the Open-Meteo API.
-   **Pytest**: For running the comprehensive test suite.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd agri-weather-mcp
    ```

2.  **Run the setup script (from repository root):**
    ```bash
    ./scripts/setup.sh
    ```

### Alternative Setup

1.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    *On Windows, use `.venv\Scripts\activate`*

2.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running the Server

To run the Agri-Weather server, execute the following command from the project's root directory:

```bash
python main.py
```

The server will start and listen for requests on standard input/output.

#### Configuration

You can specify a geographical region to restrict weather data using the `--region` command-line argument. This is useful for focusing the server's scope on a specific area of interest.

**Example:**

```bash
python main.py --region south_east_asia
```

**Supported Regions:**

*   `indonesia` (default)
*   `south_east_asia`
*   `australia`
*   `india`
*   `none` (no regional restriction)

If you need to define a custom region, you can do so by modifying the `PREDEFINED_REGIONS` dictionary in `weather_mcp/server/weather_mcp_server_fastmcp.py`.

### Running the Test Suite

The project includes a comprehensive test suite that verifies all functionality of the Agri-Weather server.

To run the tests, execute the following command from the project's root directory:

```bash
python -m pytest
```

This will run all tests using both the asyncio and trio backends to ensure compatibility with different async frameworks.

#### Test Features

- **Comprehensive Coverage**: Tests for all MCP tools and server components
- **Multiple Region Support**: Tests run against all supported regions (Indonesia, South East Asia, Australia, India)
- **Mock API Responses**: Uses realistic mock data that matches actual API response structures
- **Async Testing**: Compatible with both asyncio and trio backends
- **Robust Error Handling**: Tests for proper handling of API errors and invalid inputs

## Tools Overview

The server exposes the following tools through the Model Context Protocol:

1.  **`get_current_weather`**: Provides real-time weather conditions for a specific location.
    -   **Parameters**: `latitude`, `longitude`

2.  **`get_weather_forecast`**: Delivers a 5-day weather forecast with daily and hourly data.
    -   **Parameters**: `latitude`, `longitude`

3.  **`get_agricultural_alerts`**: Generates crop-specific warnings and recommendations.
    -   **Parameters**: `latitude`, `longitude`, `crop_type`, `growth_stage`

4.  **`get_soil_conditions`**: Returns detailed soil temperature and moisture forecasts.
    -   **Parameters**: `latitude`, `longitude`

5.  **`get_evapotranspiration_data`**: Provides evapotranspiration data for irrigation planning.
    -   **Parameters**: `latitude`, `longitude`

6.  **`get_historical_weather`**: Fetches historical weather data for a specified date range.
    -   **Parameters**: `latitude`, `longitude`, `start_date`, `end_date`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Attribution

This project uses weather data from Open-Meteo, which is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

<a href="https://open-meteo.com/">Weather data by Open-Meteo.com</a>

When using this project, you must maintain this attribution wherever Open-Meteo data is displayed.
