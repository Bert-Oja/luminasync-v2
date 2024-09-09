from datetime import datetime

import requests


class WeatherAPIInterfaceException(Exception):
    pass


class WeatherAPIInterface:
    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.current_date = datetime.now().strftime("%Y-%m-%d")

    def fetch_weather_data(self):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.current_date,
            "end_date": self.current_date,
            "hourly": "temperature_2m,cloudcover,rain",
        }
        try:
            # Make the API call
            response = requests.get(url, params=params, timeout=30)
            data = response.json()

            # Extract hourly data
            hourly_forecast = data["hourly"]
            temperatures = hourly_forecast["temperature_2m"]
            cloud_cover = hourly_forecast["cloudcover"]
            rain = hourly_forecast["rain"]

            # Calculate the daily average for each parameter
            avg_temperature = sum(temperatures) / len(temperatures)
            avg_cloud_cover = sum(cloud_cover) / len(cloud_cover)
            total_rain = sum(rain)  # Total rainfall for the day

            return {
                "temperature": avg_temperature,
                "cloud_cover": avg_cloud_cover,
                "rain": total_rain,
            }
        except requests.exceptions.RequestException as e:
            raise WeatherAPIInterfaceException(
                f"Error fetching weather data: {e}"
            ) from e
