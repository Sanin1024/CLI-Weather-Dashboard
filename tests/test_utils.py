import io
from rich.console import Console
from utils import display_weather

def test_display_weather_contains_city_name(sample_weather_data):
    output = io.StringIO()
    console = Console(file=output)
    display_weather(sample_weather_data, "metric")
    content = output.getvalue()
    assert "London" in content
    assert "GB" in content

def test_display_weather_shows_temperature(sample_weather_data):
    output = io.StringIO()
    console = Console(file=output)
    display_weather(sample_weather_data, "metric")
    content = output.getvalue()
    assert "18.5°C" in content

def test_display_weather_shows_humidity(sample_weather_data):
    output = io.StringIO()
    console = Console(file=output)
    display_weather(sample_weather_data, "metric")
    content = output.getvalue()
    assert "72%" in content

def test_visibility_converts_metres_to_km(sample_weather_data):
    output = io.StringIO()
    console = Console(file=output)
    display_weather(sample_weather_data, "metric")
    content = output.getvalue()
    assert "10.0 km" in content