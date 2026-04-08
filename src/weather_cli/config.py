from dotenv import load_dotenv
import os
import json

load_dotenv()

API_KEY = os.getenv('OPENWEATHER_API_KEY')

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
DEFAULT_UNITS = "metric"



UNITS_LABELS = {
    "metric": "°C",
    "imperial": "°F",
    "standard": "K"
}

INDIA_GEOGRAPHY = {
    "Kerala": [
        "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha",
        "Kottayam", "Painavu", "Kochi", "Thrissur",
        "Palakkad", "Malappuram", "Kozhikode", "Kalpetta",
        "Kannur", "Kasaragod"
    ],
    "Maharashtra": [
        "Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad",
        "Solapur", "Kolhapur", "Amravati", "Nanded", "Sangli", "Jalgaon"
    ],
    "Karnataka": [
        "Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi",
        "Davangere", "Ballari", "Vijayapura", "Kalaburagi", "Shivamogga"
    ],
    "TamilNadu": [
        "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem",
        "Tirunelveli", "Tiruppur", "Vellore", "Erode", "Thoothukkudi"
    ],
    "Delhi": ["Delhi"]
}

CONDITION_EMOJIS = {
    # Thunderstorm
    200: "STORM", 201: "STORM", 202: "STORM", 210: "LIGHTNING", 211: "LIGHTNING", 212: "LIGHTNING", 221: "LIGHTNING", 230: "STORM", 231: "STORM", 232: "STORM",
    # Drizzle
    300: "DRIZZLE", 301: "DRIZZLE", 302: "DRIZZLE", 310: "DRIZZLE", 311: "DRIZZLE", 312: "DRIZZLE", 313: "DRIZZLE", 314: "DRIZZLE", 321: "DRIZZLE",
    # Rain
    500: "RAIN", 501: "RAIN", 502: "RAIN", 503: "RAIN", 504: "RAIN", 511: "SNOW", 520: "RAIN", 521: "RAIN", 522: "RAIN", 531: "RAIN",
    # Snow
    600: "SNOW", 601: "SNOW", 602: "SNOW", 611: "SNOW", 612: "SNOW", 613: "SNOW", 615: "SNOW", 616: "SNOW", 620: "SNOW", 621: "SNOW", 622: "SNOW",
    # Atmosphere
    701: "FOG", 711: "SMOKE", 721: "HAZE", 741: "FOG", 751: "SAND", 761: "DUST", 762: "VOLCANO", 771: "WIND", 781: "TORNADO",
    # Clear
    800: "SUN",
    # Clouds
    801: "SUN_CLOUD", 802: "CLOUD", 803: "CLOUD", 804: "CLOUD"
}