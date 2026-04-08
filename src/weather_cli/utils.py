from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich import box
from rich.syntax import Syntax
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from .config import UNITS_LABELS, CONDITION_EMOJIS
from .weather import degrees_to_cardinal
from .persistence import load_favorites, save_favorites
import json
import os

def _is_extreme_temp(temp, units):
    # Convert to Celsius for check
    if units == "metric":
        c = temp
    elif units == "imperial":
        c = (temp - 32) * 5 / 9
    else:  # standard
        c = temp - 273.15
    return c > 30 or c < 0

def display_weather(data: dict, units: str) -> None:
    console = Console()
    unit_symbol = UNITS_LABELS[units]
    emoji = CONDITION_EMOJIS.get(data.get("condition_code"), "")

    # Prepare values
    wind_speed = data["wind_speed"]
    if units == "metric":
        wind_speed *= 3.6  # m/s to km/h
    wind_unit = "km/h" if units == "metric" else "mph"
    visibility_km = data.get("visibility", 0) / 1000 if data.get("visibility") else "N/A"

    # Layout
    layout = Layout()
    layout.split(
        Layout(name="top", ratio=4),
        Layout(name="footer", size=3)
    )
    layout["top"].split_row(
        Layout(name="main", ratio=2),
        Layout(name="sidebar", ratio=1)
    )

    # Main panel
    temp_text = Text(f"{emoji} {data['temperature']:.1f}{unit_symbol}", style="bold yellow")
    temp_text.append(f"\nFeels like {data['feels_like']:.1f}{unit_symbol}", style="dim")
    condition_text = Text(f"\n{data['condition']}", style="white")
    main_content = Align.center(temp_text + condition_text)
    main_panel = Panel(main_content, title=f"Weather in {data['city']}, {data['country']}")
    layout["main"].update(main_panel)

    # Sidebar
    visibility_str = f"Visibility: {visibility_km:.1f} km" if visibility_km != "N/A" else "Visibility: N/A"
    sidebar_content = (
        f"Humidity: {data['humidity']}%\n"
        f"Pressure: {data['pressure']} hPa\n"
        f"Wind: {wind_speed:.1f} {wind_unit} {degrees_to_cardinal(data.get('wind_deg'))}\n"
        f"Clouds: {data['clouds']}%\n"
        f"{visibility_str}"
    )
    sidebar_panel = Panel(sidebar_content, title="Details")
    layout["sidebar"].update(sidebar_panel)

    # Footer
    cached_indicator = " (Cached)" if data.get("cached", False) else ""
    footer_content = f"Sunrise: {data['sunrise']} | Sunset: {data['sunset']} | Last Updated: {data['last_updated']}{cached_indicator}"
    footer_panel = Panel(footer_content, title_align="center")
    layout["footer"].update(footer_panel)

    console.print(layout)

def display_verbose(raw_json: dict) -> None:
    console = Console()
    syntax = Syntax(json.dumps(raw_json, indent=2), "json", theme="monokai", line_numbers=True)
    console.print(syntax)

def display_forecast(forecast_list, units):
    console = Console()
    unit_symbol = UNITS_LABELS[units]
    table = Table(title="5-Day Forecast", expand=True, box=box.ROUNDED, padding=(0, 2), show_lines=True)
    table.add_column("Date", style="bold", no_wrap=False, min_width=12)
    table.add_column("High (Time)", style="yellow", justify="center")
    table.add_column("Low (Time)", style="cyan", justify="center")
    table.add_column("Condition", no_wrap=False, ratio=1)
    table.add_column("Rain Prob", style="blue", justify="center")
    for day in forecast_list:
        high_str = f"{day['high']:.1f}{unit_symbol}\n({day['high_time']})"
        low_str = f"{day['low']:.1f}{unit_symbol}\n({day['low_time']})"
        rain_str = f"{day['rain_probability']:.0f}%"
        table.add_row(day["date"], high_str, low_str, day["condition"], rain_str)
    console.print(table)

    # ASCII Trend for Highs
    if forecast_list:
        highs = [day['high'] for day in forecast_list]
        min_temp = min(highs)
        max_temp = max(highs)
        range_temp = max_temp - min_temp if max_temp != min_temp else 1
        sparkline = ""
        chars = "_.-~=+*#"
        for temp in highs:
            index = int((temp - min_temp) / range_temp * 7)
            sparkline += chars[min(index, 6)]
        
        console.print(f"Temperature Trend (Highs): {sparkline}")

def display_state_weather(data_list, units, state="Kerala"):
    console = Console()
    unit_symbol = UNITS_LABELS[units]
    table = Table(title=f"{state} District-wise Weather", expand=True, box=box.ROUNDED, padding=(0, 2), show_lines=True)
    table.add_column("District", style="bold", no_wrap=False, min_width=15)
    table.add_column("Temperature", style="yellow", justify="center")
    table.add_column("Condition", no_wrap=False, ratio=1)
    table.add_column("Humidity", justify="center")
    for data in data_list:
        table.add_row(data["city"], f"{data['temperature']:.1f}{unit_symbol}", data["condition"], f"{data['humidity']}%")
    console.print(table)

def display_location_error(message):
    console = Console()
    panel = Panel(f"[red]{message}[/red]", title="Location Error")
    console.print(panel)