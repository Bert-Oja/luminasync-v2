import os
import sys
from unittest.mock import Mock, patch

import pytest
import requests

from src.interfaces.weather_api_interface import (
    WeatherAPIInterface,
    WeatherAPIInterfaceException,
)

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

# Sample data to use in our mocks
MOCK_RESPONSE_SUCCESS = {
    "hourly": {
        "temperature_2m": [20, 21, 22, 23],
        "cloudcover": [50, 60, 70, 80],
        "rain": [0, 0, 0, 0],
    }
}

MOCK_RESPONSE_MISSING_DATA = {
    "hourly": {
        "temperature_2m": [20, 21],
        # Missing 'cloudcover' and 'rain'
    }
}


def test_fetch_weather_data_success():
    """Test successful data retrieval and correct averaging."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = MOCK_RESPONSE_SUCCESS
        mock_get.return_value = mock_response

        weather_api = WeatherAPIInterface(latitude=40.7128, longitude=-74.0060)
        result = weather_api.fetch_weather_data()

        assert result == {
            "temperature": 21.5,  # Average of [20, 21, 22, 23]
            "cloud_cover": 65.0,  # Average of [50, 60, 70, 80]
            "rain": 0,  # Sum of [0, 0, 0, 0]
        }


def test_fetch_weather_data_request_exception():
    """Test handling of network-related exceptions."""
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        weather_api = WeatherAPIInterface(latitude=40.7128, longitude=-74.0060)
        with pytest.raises(WeatherAPIInterfaceException) as exc_info:
            weather_api.fetch_weather_data()
        assert "Error fetching weather data" in str(exc_info.value)


def test_fetch_weather_data_missing_data():
    """Test handling when API returns incomplete data."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None  # No exception
        mock_response.json.return_value = MOCK_RESPONSE_MISSING_DATA
        mock_get.return_value = mock_response

        weather_api = WeatherAPIInterface(latitude=40.7128, longitude=-74.0060)
        with pytest.raises(WeatherAPIInterfaceException) as exc_info:
            weather_api.fetch_weather_data()
        assert "cloudcover" in str(exc_info.value)


def test_fetch_weather_data_invalid_json():
    """Test handling when API returns invalid JSON."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        weather_api = WeatherAPIInterface(latitude=40.7128, longitude=-74.0060)
        with pytest.raises(WeatherAPIInterfaceException) as exc_info:
            weather_api.fetch_weather_data()
        assert "Error fetching weather data" in str(exc_info.value)


def test_fetch_weather_data_http_error():
    """Test handling of HTTP errors (e.g., 404 Not Found)."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error"
        )
        mock_get.return_value = mock_response

        weather_api = WeatherAPIInterface(latitude=40.7128, longitude=-74.0060)
        with pytest.raises(WeatherAPIInterfaceException) as exc_info:
            weather_api.fetch_weather_data()
        assert "404 Client Error" in str(exc_info.value)
