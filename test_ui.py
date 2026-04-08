#!/usr/bin/env python3
"""
UI Tests for CLI Weather Dashboard
Tests the display functions to ensure they render correctly.
"""

import io
from rich.console import Console
from weather_cli.utils import display_weather, display_forecast, display_state_weather
from weather_cli.config import CONDITION_EMOJIS

def test_display_weather_renders():
    """Test that display_weather produces output without crashing."""
    sample_data = {
        "city": "London",
        "country": "GB",
        "temperature": 18.5,
        "feels_like": 17.2,
        "humidity": 72,
        "pressure": 1013,
        "wind_speed": 10.3,
        "wind_deg": 180,
        "clouds": 75,
        "condition": "Cloudy",
        "condition_code": 999,  # Invalid code for no emoji
        "visibility": 10000,
        "sunrise": "6:30 AM",
        "sunset": "7:45 PM",
        "last_updated": "12:00 PM",
        "cached": False,
        "units": "metric"
    }
    try:
        display_weather(sample_data, "metric")
        print("PASS: display_weather renders correctly")
    except Exception as e:
        print(f"FAIL: display_weather crashed: {e}")
        raise

def test_display_forecast_renders():
    """Test forecast display with trend."""
    sample_forecast = [
        {"date": "2023-10-01", "high": 20.0, "low": 15.0, "condition": "Sunny"},
        {"date": "2023-10-02", "high": 22.0, "low": 16.0, "condition": "Cloudy"}
    ]
    try:
        display_forecast(sample_forecast, "metric")
        print("PASS: display_forecast renders correctly with trend")
    except Exception as e:
        print(f"FAIL: display_forecast crashed: {e}")
        raise

def test_condition_emojis():
    """Test that condition codes are mapped."""
    assert CONDITION_EMOJIS[800] == "SUN"  # Clear sky
    assert CONDITION_EMOJIS[500] == "RAIN"  # Rain
    print("PASS: Condition codes are properly mapped")

if __name__ == "__main__":
    test_display_weather_renders()
    test_display_forecast_renders()
    test_condition_emojis()
    print("All UI tests passed!")