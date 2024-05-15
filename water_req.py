import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)



# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 23.8314,
	"longitude": 91.2867,
	"daily": "et0_fao_evapotranspiration",
	"wind_speed_unit": "ms",
    "timezone": "auto",
    "start_date": "2024-03-01",
	"end_date": "2024-03-01"
}
# responses = openmeteo.weather_api(url, params=params)


# Process first location. Add a for-loop for multiple locations or weather models
# response = responses[0]
# print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
# print(f"Elevation {response.Elevation()} m asl")
# print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
# print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Process daily data. The order of variables needs to be the same as requested.
# daily = response.Daily()
# daily_et0_fao_evapotranspiration = daily.Variables(0).ValuesAsNumpy()
# print(daily_et0_fao_evapotranspiration)
# daily_data = {"date": pd.date_range(
# 	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
# 	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
# 	freq = pd.Timedelta(seconds = daily.Interval()),
# 	inclusive = "left"
# )}
# daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration

# daily_dataframe = pd.DataFrame(data = daily_data)
# print(daily_dataframe)


def get_ET0(latitude,longitude,start_date,end_date):
    data = dict(params)
    data["latitude"] = latitude
    data["longitude"] = longitude
    data["start_date"] = start_date
    data["end_date"] = end_date
    
    responses = openmeteo.weather_api(url, params=data)
    daily = responses[0].Daily()
    daily_et0_fao_evapotranspiration = daily.Variables(0).ValuesAsNumpy()
    return list(daily_et0_fao_evapotranspiration)
