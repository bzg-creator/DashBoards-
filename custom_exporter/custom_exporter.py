
from prometheus_client import start_http_server, Gauge, Info
import requests, time, os

API_KEY = os.getenv("OWM_API_KEY", "b6907d289e10d714a6e88b30761fae22")
CITY    = os.getenv("OWM_CITY", "Astana")
UNITS   = os.getenv("OWM_UNITS", "metric")  # metric = °C, m/s

# ---- Metrics (names align with what you already have) ----
temperature = Gauge("weather_temperature_celsius", "Current temperature in Celsius")
feels_like  = Gauge("weather_feels_like_celsius", "Feels like temperature in Celsius")
humidity    = Gauge("weather_humidity_percent", "Humidity percent")
pressure    = Gauge("weather_pressure_hpa", "Atmospheric pressure in hPa")
wind_speed  = Gauge("weather_wind_speed_mps", "Wind speed in meters per second")
wind_deg    = Gauge("weather_wind_direction_deg", "Wind direction in degrees")
clouds      = Gauge("weather_clouds_percent", "Cloudiness percent")
visibility  = Gauge("weather_visibility_m", "Visibility in meters")
condition   = Gauge("weather_condition_code", "Weather condition numeric code")
resp_ms     = Gauge("weather_api_response_time_ms", "OpenWeather API response time in ms")

exporter_info = Info("custom_exporter_info", "Custom weather exporter info")

def fetch_once():
    start = time.time()
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units={UNITS}"
    r = requests.get(url, timeout=10)
    elapsed = (time.time() - start) * 1000.0
    resp_ms.set(elapsed)

    r.raise_for_status()
    d = r.json()

    temperature.set(d["main"]["temp"])
    feels_like.set(d["main"]["feels_like"])
    humidity.set(d["main"]["humidity"])
    pressure.set(d["main"]["pressure"])
    wind_speed.set(d["wind"]["speed"])
    wind_deg.set(d["wind"].get("deg", 0))
    clouds.set(d["clouds"]["all"])
    visibility.set(d.get("visibility", 0))
    condition.set(d["weather"][0]["id"])

if __name__ == "__main__":
    exporter_info.info({"version": "2.0", "source": "OpenWeather"})
    start_http_server(8000)
    print("✅ Custom exporter on :8000 (every 20s)")
    while True:
        try:
            fetch_once()
        except Exception as e:
            print("Fetch error:", e)
        time.sleep(20)

