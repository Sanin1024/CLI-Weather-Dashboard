import subprocess
import sys

def test_main_valid_city_exits_zero():
    result = subprocess.run([sys.executable, "main.py", "--city", "London"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "London" in result.stdout

def test_main_invalid_city_exits_nonzero():
    result = subprocess.run([sys.executable, "main.py", "--city", "InvalidCity"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "not found" in result.stdout or result.stderr

def test_main_missing_city_shows_usage():
    result = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "usage" in result.stderr.lower()