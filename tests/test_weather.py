import pytest
from unittest.mock import patch
from weather import get_weather, _safe_get, CityNotFoundError, APIKeyError, NetworkError

@patch("weather.requests.get")
def test_get_weather_success(mock_get, mock_api_200):
    mock_get.return_value = mock_api_200
    result = get_weather("London", "metric")
    assert result["city"] == "London"
    assert result["country"] == "GB"
    assert result["temperature"] == 18.5
    assert result["condition"] == "Cloudy"

@patch("weather.requests.get")
def test_get_weather_city_not_found(mock_get, mock_api_404):
    mock_get.return_value = mock_api_404
    with pytest.raises(CityNotFoundError, match="City 'InvalidCity' not found"):
        get_weather("InvalidCity", "metric")

@patch("weather.requests.get")
def test_get_weather_invalid_api_key(mock_get, mock_api_401):
    mock_get.return_value = mock_api_401
    with pytest.raises(APIKeyError, match="Invalid or missing API key"):
        get_weather("London", "metric")

@patch("weather.requests.get")
def test_get_weather_network_error(mock_get, mock_connection_error):
    mock_get.side_effect = mock_connection_error
    with pytest.raises(NetworkError, match="No internet connection"):
        get_weather("London", "metric")

@patch("weather.requests.get")
def test_get_weather_timeout(mock_get, mock_timeout_error):
    mock_get.side_effect = mock_timeout_error
    with pytest.raises(NetworkError, match="Request timed out"):
        get_weather("London", "metric")

@patch("weather.requests.get")
def test_get_weather_units_metric(mock_get, mock_api_200):
    mock_get.return_value = mock_api_200
    result = get_weather("London", "metric")
    assert result["units"] == "metric"
    assert result["temperature"] == 18.5  # assuming C

@patch("weather.requests.get")
def test_get_weather_units_imperial(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "London",
        "sys": {"country": "GB"},
        "main": {"temp": 65.3, "feels_like": 63.0, "humidity": 72},  # F
        "wind": {"speed": 5.8},  # mph
        "weather": [{"description": "cloudy", "id": 803}],
        "visibility": 10000
    }
    mock_get.return_value = mock_response
    result = get_weather("London", "imperial")
    assert result["units"] == "imperial"
    assert result["temperature"] == 65.3

def test_safe_get_helper():
    data = {"a": {"b": "value"}}
    assert _safe_get(data, "a", "b") == "value"
    assert _safe_get(data, "a", "c") is None
    assert _safe_get(data, "x") is None
    assert _safe_get(data, "a", "b", "c", default="default") == "default"