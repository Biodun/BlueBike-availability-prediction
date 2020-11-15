# Retrieve 1 month of weather data for one station
# 2020-11-14
# Author: Biodun Iwayemi

#%% Imports
import requests
import pandas as pd
import os 
from dotenv import load_dotenv
from pyprojroot import here

load_dotenv()
DARKSKY_API_KEY = os.getenv("DARK_SKY_SECRET_KEY")

# %% Make a DarkSky API request for historical w
BASE_URL = "https://api.darksky.net/forecast"
BASE_FOLDER = here()
SAVE_PATH = BASE_FOLDER / "data/processed"

latitude  = 42.363796
longitude = -71.1087861286
all_weather_data = []
start_date = '2020-01-01'
end_date = '2020-11-14'
# Retrieve weather data for thGIT e specified
for day in pd.date_range(start_date, end_date, freq='D'):
    # Format timestamp to match what DarkSky API expects
    timestamp = str(day).replace(' ', 'T') #[YYYY]-[MM]-[DD]T[HH]:[MM]:[SS]
    api_request_string =    f"{BASE_URL}/{DARKSKY_API_KEY}/{latitude},{longitude}, {timestamp}"
    historical_data = requests.get(api_request_string)

    # Extract hourly weather measurements
    weather_data = pd.DataFrame(historical_data.json()['hourly']['data'])

    # Parse the timestamps
    weather_data['timestamps'] = weather_data['time'].apply(lambda x: pd.to_datetime(x, unit='s', utc=True))
    weather_data.set_index('timestamps', inplace=True)
    all_weather_data.append(weather_data)

# %% Concatenate all the dataframes into a single dataframe
weather_df = pd.concat(all_weather_data)
weather_df['latitude'] = latitude
weather_df['longitude'] = longitude
weather_df.to_csv(f'{SAVE_PATH}/weather_data_{start_date}__{end_date}.csv')

