import json
import os
import time
import tempfile

CACHE_DIR = os.path.expanduser("~/.weathercli")
CACHE_FILE = os.path.join(CACHE_DIR, "cache.json")
CONFIG_FILE = os.path.join(CACHE_DIR, "config.json")
FAVORITES_FILE = os.path.join(CACHE_DIR, "favorites.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_config(config):
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except IOError:
        pass

def get_cached_weather(city, units):
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
    key = f"{city.lower()}_{units}"
    if key in cache:
        entry = cache[key]
        if time.time() - entry["timestamp"] < 600:  # 10 minutes
            return entry["data"], entry["raw"]
    return None

def save_to_cache(city, units, data, raw):
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f:
                cache = json.load(f)
        except (json.JSONDecodeError, IOError):
            cache = {}
    key = f"{city.lower()}_{units}"
    cache[key] = {
        "timestamp": time.time(),
        "data": data,
        "raw": raw
    }
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=CACHE_DIR, delete=False) as temp_file:
            json.dump(cache, temp_file)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.rename(temp_file.name, CACHE_FILE)
    except (IOError, OSError):
        pass  # Silently fail if can't write

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_favorites(favs):
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        with open(FAVORITES_FILE, "w") as f:
            json.dump(favs, f)
    except IOError:
        pass