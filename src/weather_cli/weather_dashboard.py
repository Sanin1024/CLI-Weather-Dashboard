import argparse
import sys
import os
import concurrent.futures
import requests
from .weather import get_weather, get_forecast, CityNotFoundError, APIKeyError, NetworkError, LocationBoundaryError
from .utils import display_weather, display_verbose, display_forecast, display_state_weather, display_location_error
from .config import INDIA_GEOGRAPHY
from .persistence import load_config, save_config, load_favorites, save_favorites
from rich.console import Console

def get_location_from_ip():
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                city = data.get("city")
                if city:
                    return city
    except:
        pass
    return None

def main():
    config = load_config()
    DEFAULT_UNITS = config.get("default_units", "metric")
    DEFAULT_CITY = config.get("default_city")

    parser = argparse.ArgumentParser(description="CLI Weather Dashboard")
    parser.add_argument("--city", help="City name to fetch weather for")
    parser.add_argument("--kerala", action="store_true", help="Show district-wise weather for Kerala")
    parser.add_argument("--units", choices=["metric", "imperial", "standard"], default=DEFAULT_UNITS, help="Units for temperature")
    parser.add_argument("--verbose", action="store_true", help="Show raw API response")
    parser.add_argument("--forecast", action="store_true", help="Show 5-day forecast instead of current weather")
    parser.add_argument("--force", action="store_true", help="Force fresh API fetch, bypass cache")
    parser.add_argument("--save-favorite", action="store_true", help="Save current city to favorites")
    parser.add_argument("--list-favorites", action="store_true", help="List favorite cities")
    parser.add_argument("--remove-favorite", metavar="CITY", help="Remove city from favorites")
    parser.add_argument("--set-default-units", choices=["metric", "imperial", "standard"], help="Set default units for future runs")
    parser.add_argument("--set-default-city", metavar="CITY", help="Set default city for future runs")
    args, unknown_args = parser.parse_known_args()

    console = Console()

    # Handle --India- flags
    india_mode = None
    for arg in unknown_args:
        if arg.startswith('--India-'):
            parts = arg[8:].split('-')
            if len(parts) == 1:
                state = parts[0]
                india_mode = ('state', state)
            elif len(parts) == 2:
                state, district = parts
                india_mode = ('district', state, district)

    if india_mode:
        if india_mode[0] == 'state':
            state = india_mode[1]
            if state in INDIA_GEOGRAPHY:
                args.india_state = state
            else:
                console.print(f"State '{state}' not supported. Supported states: {list(INDIA_GEOGRAPHY.keys())}")
                sys.exit(1)
        elif india_mode[0] == 'district':
            state, district = india_mode[1], india_mode[2]
            args.city = district
            args.india_validate = True

    if args.list_favorites:
        favorites = load_favorites()
        if favorites:
            console.print("Favorite cities:")
            for city in favorites:
                console.print(f"- {city}")
        else:
            console.print("No favorite cities saved.")
        sys.exit(0)

    elif args.remove_favorite:
        favorites = load_favorites()
        if args.remove_favorite in favorites:
            favorites.remove(args.remove_favorite)
            save_favorites(favorites)
            console.print(f"Removed {args.remove_favorite} from favorites.")
        else:
            console.print(f"{args.remove_favorite} not in favorites.")
        sys.exit(0)

    elif args.set_default_units:
        config = load_config()
        config["default_units"] = args.set_default_units
        save_config(config)
        console.print(f"Default units set to {args.set_default_units}")
        sys.exit(0)

    elif args.set_default_city:
        config = load_config()
        config["default_city"] = args.set_default_city
        save_config(config)
        console.print(f"Default city set to {args.set_default_city}")
        sys.exit(0)

    if not args.city and not (hasattr(args, 'kerala') and args.kerala) and not (hasattr(args, 'india_state') and args.india_state):
        favorites = load_favorites()
        if favorites:
            from rich.prompt import Prompt
            if len(favorites) == 1:
                args.city = favorites[0]
            else:
                choices = [f"{i+1}. {fav}" for i, fav in enumerate(favorites)]
                choice = Prompt.ask("Select a favorite city", choices=choices)
                index = int(choice.split(".")[0]) - 1
                args.city = favorites[index]
        elif DEFAULT_CITY:
            args.city = DEFAULT_CITY
        else:
            location = get_location_from_ip()
            if location:
                args.city = location
                console.print(f"Detected location: {location}")
            else:
                console.print("No city specified and could not detect location. Use --city, --India-<State>, --set-default-city, or --list-favorites")
                sys.exit(1)

    # Smart Alias Mapping for API compatibility
    CITY_ALIASES = {
        "wayanad": "Kalpetta",
        "ernakulam": "Kochi",
        "idukki": "Painavu"
    }
    if args.city and args.city.lower() in CITY_ALIASES:
        args.city = CITY_ALIASES[args.city.lower()]

    try:
        # Check if we should fetch a state-wide summary (e.g., --India-Kerala or --kerala)
        target_state = None
        if hasattr(args, 'india_state') and args.india_state:
            target_state = args.india_state
        elif hasattr(args, 'kerala') and args.kerala:
            target_state = "Kerala"

        if target_state:
            if target_state not in INDIA_GEOGRAPHY:
                 console.print(f"State '{target_state}' is not supported yet.")
                 sys.exit(1)
            
            districts = INDIA_GEOGRAPHY[target_state]
            state_data = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_district = {executor.submit(get_weather, dist, args.units, force=args.force): dist for dist in districts}
                for future in concurrent.futures.as_completed(future_to_district):
                    district_name = future_to_district[future]
                    try:
                        data = future.result()
                        state_data.append(data)
                    except Exception as e:
                        console.print(f"Error fetching for {district_name}: {e}")
            display_state_weather(state_data, args.units, target_state)
        elif args.forecast:
            forecast_data = get_forecast(args.city, args.units, force=args.force)
            display_forecast(forecast_data["forecast"], args.units)
            if forecast_data.get("cached"):
                console.print("[dim italic]Forecast data loaded from cache.[/]")
        else:
            india_validate = getattr(args, 'india_validate', False)
            if args.verbose:
                data, raw = get_weather(args.city, args.units, verbose=True, force=args.force, india_validate=india_validate)
                display_verbose(raw)
            else:
                data = get_weather(args.city, args.units, force=args.force, india_validate=india_validate)
            display_weather(data, args.units)
        
        if args.save_favorite and not (hasattr(args, 'kerala') and args.kerala) and not (hasattr(args, 'india_state') and args.india_state):
            favorites = load_favorites()
            if args.city not in favorites and not any(f.lower() == args.city.lower() for f in favorites):
                favorites.append(args.city)
                save_favorites(favorites)
                console.print(f"Saved {args.city} to favorites.")
    except CityNotFoundError as e:
        console.print(f"[bold red]Error:[/] {e}")
    except APIKeyError as e:
        console.print(f"[bold red]API Key Error:[/] {e}")
    except NetworkError as e:
        console.print(f"[bold red]Network Error:[/] {e}")
    except LocationBoundaryError as e:
        display_location_error(str(e))
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()