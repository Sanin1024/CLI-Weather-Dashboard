import pytest
from unittest.mock import MagicMock
import requests

@pytest.fixture
def sample_weather_data():
    return {
        "city": "London",
        "country": "GB",
        "temperature": 18.5,
        "feels_like": 17.2,
        "humidity": 72,
        "wind_speed": 10.3,
        "condition": "Cloudy",
        "condition_code": 803,
        "visibility": 10000,
        "units": "metric"
    }

@pytest.fixture
def mock_api_200():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "London",
        "sys": {"country": "GB"},
        "main": {"temp": 18.5, "feels_like": 17.2, "humidity": 72},
        "wind": {"speed": 10.3},
        "weather": [{"description": "cloudy", "id": 803}],
        "visibility": 10000
    }
    return mock_response

@pytest.fixture
def mock_api_401():
    mock_response = MagicMock()
    mock_response.status_code = 401
    return mock_response

@pytest.fixture
def mock_api_404():
    mock_response = MagicMock()
    mock_response.status_code = 404
    return mock_response

@pytest.fixture
def mock_connection_error():
    return requests.exceptions.ConnectionError()

@pytest.fixture
def mock_timeout_error():
    return requests.exceptions.Timeout()