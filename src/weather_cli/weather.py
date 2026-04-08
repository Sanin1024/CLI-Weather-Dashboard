import requests
from .config import BASE_URL, FORECAST_URL, API_KEY
from typing import Union, Tuple
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from .persistence import get_cached_weather, save_to_cache


class CityNotFoundError(Exception):
    pass


class APIKeyError(Exception):
    pass


class NetworkError(Exception):
    pass

class LocationBoundaryError(Exception):
    pass


def _validate_api_key():
    """Deferred API key check — only called when making an actual API request."""
    if not API_KEY or not API_KEY.strip() or API_KEY.strip() in ["", "your_api_key_here"]:
        raise APIKeyError(
            "No valid API key found.\n"
            "  1. Go to https://openweathermap.org/api and sign up for free\n"
            "  2. Copy your API key\n"
            "  3. Open .env and replace: OPENWEATHER_API_KEY=your_api_key_here\n"
            "     with your real key, e.g.: OPENWEATHER_API_KEY=abc123yourkeyhere"
        )


def _safe_get(data, *keys, default=None):
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, (list, tuple)) and isinstance(key, int) and 0 <= key < len(data):
            data = data[key]
        else:
            return default
    return data

def degrees_to_cardinal(deg):
    if deg is None:
        return ""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(deg / 22.5) % 16
    return directions[index]

def unix_to_time(unix_ts, tz_offset=0):
    # Ensure values are not None and are integers
    if unix_ts is None:
        return "N/A"
    
    # Cast to int and default to 0 if None
    ts = int(unix_ts)
    offset = int(tz_offset) if tz_offset is not None else 0

    # Create UTC datetime and add the city's specific offset
    utc_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    local_dt = utc_dt + timedelta(seconds=offset)
    return local_dt.strftime("%I:%M %p")


def _parse_weather(data, units):
    tz_offset = _safe_get(data, "timezone")
    if tz_offset is None:
        tz_offset = 0
    return {
        "city": _safe_get(data, "name"),
        "country": _safe_get(data, "sys", "country"),
        "temperature": _safe_get(data, "main", "temp"),
        "feels_like": _safe_get(data, "main", "feels_like"),
        "humidity": _safe_get(data, "main", "humidity"),
        "pressure": _safe_get(data, "main", "pressure"),
        "wind_speed": _safe_get(data, "wind", "speed"),
        "wind_deg": _safe_get(data, "wind", "deg"),
        "clouds": _safe_get(data, "clouds", "all"),
        "condition": _safe_get(data, "weather", 0, "description", default="").title(),
        "condition_code": _safe_get(data, "weather", 0, "id"),
        "visibility": _safe_get(data, "visibility"),
        "sunrise": unix_to_time(_safe_get(data, "sys", "sunrise"), tz_offset),
        "sunset": unix_to_time(_safe_get(data, "sys", "sunset"), tz_offset),
        "last_updated": unix_to_time(_safe_get(data, "dt"), tz_offset),
        "units": units
    }


def get_forecast(city: str, units: str = "metric", force: bool = False) -> dict:
    _validate_api_key()
    if not force:
        # For forecast, cache the list with a special key
        cached = get_cached_weather(f"{city}_forecast", units)
        if cached:
            data, _ = cached
            return {"forecast": data["forecast"], "cached": True}
    params = {"q": city, "appid": API_KEY, "units": units}
    import time
    for attempt in range(2):
        try:
            response = requests.get(FORECAST_URL, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                forecasts = []
                for item in data["list"]:
                    forecasts.append({
                        "datetime": item["dt_txt"],
                        "temp": item["main"]["temp"],
                        "condition": item["weather"][0]["description"].title(),
                        "humidity": item["main"]["humidity"],
                        "rain_probability": item.get("pop", 0) * 100
                    })
                daily = defaultdict(list)
                for f in forecasts:
                    date = f["datetime"].split()[0]
                    daily[date].append(f)
                result = []
                for date, items in sorted(daily.items()):
                    temps = [i["temp"] for i in items]
                    conditions = [i["condition"] for i in items]
                    rain_probs = [i["rain_probability"] for i in items]
                    high = max(temps)
                    low = min(temps)
                    high_time = next(i["datetime"].split()[1] for i in items if i["temp"] == high)
                    low_time = next(i["datetime"].split()[1] for i in items if i["temp"] == low)
                    condition = max(set(conditions), key=conditions.count)
                    max_rain_prob = max(rain_probs)
                    result.append({
                        "date": date,
                        "high": high,
                        "low": low,
                        "high_time": high_time,
                        "low_time": low_time,
                        "condition": condition,
                        "rain_probability": max_rain_prob
                    })
                save_to_cache(f"{city}_forecast", units, {"forecast": result}, None)
                return {"forecast": result, "cached": False}
            elif response.status_code == 401:
                raise APIKeyError("Invalid API key. Check your .env file.")
            elif response.status_code == 404:
                raise CityNotFoundError(f"City '{city}' not found. Check spelling.")
            else:
                raise NetworkError(f"Unexpected API error: {response.status_code}")
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt == 0:
                time.sleep(1)
                continue
            raise NetworkError("Connection failed after multiple attempts. Check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {e}")


def get_weather(city: str, units: str = "metric", verbose: bool = False, force: bool = False, india_validate: bool = False) -> Union[dict, Tuple[dict, dict]]:
    _validate_api_key()
    if not force:
        cached = get_cached_weather(city, units)
        if cached:
            data, raw = cached
            data["cached"] = True
            if verbose:
                return data, raw
            else:
                return data
    params = {"q": city, "appid": API_KEY, "units": units}
    import time
    for attempt in range(2):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if india_validate and _safe_get(data, "sys", "country") != "IN":
                    raise LocationBoundaryError(f"{city} is not located in India.")
                parsed = _parse_weather(data, units)
                parsed["cached"] = False
                save_to_cache(city, units, parsed, data)
                if verbose:
                    return parsed, data
                else:
                    return parsed
            elif response.status_code == 401:
                raise APIKeyError("Invalid API key. Check your .env file.")
            elif response.status_code == 404:
                raise CityNotFoundError(f"City '{city}' not found. Check spelling.")
            else:
                raise NetworkError(f"Unexpected API error: {response.status_code}")
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt == 0:
                time.sleep(1)
                continue
            raise NetworkError("Connection failed after multiple attempts. Check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {e}")