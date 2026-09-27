"""Chapter 0: calling a web API with httpx, and reading the answer."""
import os
import httpx

URL = "https://api.open-meteo.com/v1/forecast"

def max_temperature(latitude: float, longitude: float) -> str:
    params = {"latitude": latitude, "longitude": longitude,
              "daily": "temperature_2m_max", "forecast_days": 1, "timezone": "auto"}
    try:
        response = httpx.get(URL, params=params, timeout=10)
    except httpx.HTTPError as exc:                      # no network, timeout, ...
        return f"ERROR: could not reach the API ({type(exc).__name__})"
    print("status code:", response.status_code)         # 200 = OK, 4xx = your mistake,
    if response.status_code != 200:                    # 5xx = the server's problem
        return f"ERROR: HTTP {response.status_code}: {response.text[:100]}"
    data = response.json()                              # JSON text -> Python dict
    return f"{data['daily']['time'][0]}: max {data['daily']['temperature_2m_max'][0]} C"

if __name__ == "__main__":
    print(max_temperature(18.52, 73.86))                # Pune
    # Secrets such as API keys come from environment variables, never from code:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    print("API key loaded:",
          "yes" if key.startswith("sk-") else "no (check your .env file)")
