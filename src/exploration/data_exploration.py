# Explore BlueBike data using Streamlit so that I can define the database schema
# Date: Feb 15th 2020
# Author: Biodun

import streamlit as st
import pandas as pd 
import numpy as np
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

STATION_INFO_URL = "https://gbfs.bluebikes.com/gbfs/en/station_information.json"
STATION_STATUS_URL = "https://gbfs.bluebikes.com/gbfs/en/station_status.json"
WEATHER_DATA_URL = "https://api.darksky.net/forecast"

# Load environment variables
load_dotenv(verbose=True)
DARK_SKY_SECRET_KEY = os.getenv("DARK_SKY_SECRET_KEY")

@st.cache
def get_station_data():
    """Get Blue bike station data"""    
    station_data_request = requests.get(STATION_INFO_URL)
    if station_data_request.status_code == 200:
        station_data = station_data_request.json()['data']['stations']
        
        # Parse the station data into a dataframe
        stations = []
        for station in station_data:
            stations.append([station['station_id'], station['name'], station['capacity'], station['lat'], 
        station['lon']])
        station_df = pd.DataFrame(stations, columns=['Station_id', 'Station_name', 'Capacity', 'lat', 'lon'])
        return station_df
    else:
        st.write("An error occurred and couldn't retrieve station data")


def get_station_status():
    """
"station_id": "7",
        "num_bikes_available": 1,
        "num_ebikes_available": 0,
        "num_bikes_disabled": 0,
        "num_docks_available": 14,
        "num_docks_disabled": 0,
        "is_installed": 1,
        "is_renting": 1,
        "is_returning": 1,
        "last_reported": 1581795268,
        "eightd_has_available_keys": false
"""
    station_response = requests.get(STATION_STATUS_URL)
    if station_response.status_code == 200:
        station_status = []
        for station in station_response.json()['data']['stations']:
            #TODO include parsed timestamps
            station_status.append([station['station_id'], station["num_bikes_available"], station['num_docks_available'], station['num_ebikes_available']])
        return pd.DataFrame(station_status, columns=['Station_id', 'num_bikes_available', 'num_docks_available', 'num_ebikes_available'])

@st.cache
def get_current_weather(lat, lon):
    """Get current weather for the specified location from the Dark Sky API"""

    # Build parameters for weather data request
    current_time = datetime.now()
    current_time = str(current_time).replace(' ', 'T').split('.')[0]
    print(f"current time: {current_time}")
    
        # Make API call and exclude minutely and current weather
    URL = f"{WEATHER_DATA_URL}/{DARK_SKY_SECRET_KEY}/{lat},{lon},{current_time}"
    params = {
        "exclude": ['minutely', 'hourly', 'flags']
    }
    print(f"URL: {URL}")
    weather_data_request = requests.get(URL, params=params)
    return weather_data_request.json()


st.title("BlueBike Data Viz")
if st.checkbox("Show BlueBike data"):
    st.subheader('Blue Bike Station Data')
    station_data = get_station_data()
    st.write(station_data)

# Plot Blue Bike data
st.subheader("Boston BlueBike stations")
st.map(station_data)

# Explore the distribution of bike dock capacities
st.subheader("Distribution of bike dock capacities")
st.bar_chart(np.histogram(station_data['Capacity'], bins=50, range=(0,50))[0])

st.subheader("Station location EDA")
# Determine how many towns the bike locations are spread over

station_metadata = pd.read_csv('data/raw/station_data_corrected_header.csv')
st.write(station_metadata)

st.subheader("Distribution of stations by city")
st.bar_chart(station_metadata['District'].value_counts())

# Next steps
# 1. Filter data by station ID and explore all the data for a station

# create a dict mapping from station id to station name
station_id_mapping = {key:value for (idx, (key, value)) in station_data[['Station_name', 'Station_id']].iterrows()}

selected_station = st.sidebar.selectbox(label='Station name', options = sorted(list(station_id_mapping.keys())))
station_id = station_id_mapping[selected_station]
station_lat = station_data.query("Station_id == @station_id")['lat'].values[0]
station_lon = station_data.query("Station_id == @station_id")['lon'].values[0]

print(f"station lat: {station_lat}, station lon: {station_lon}")
# Display station Status for the selected station
st.subheader(f"Station: {selected_station}")
station_status = get_station_status()
st.write(station_status.query("Station_id == @station_id"))
station_weather = get_current_weather(station_lat, station_lon)
st.write(station_weather)
# Retrieve weather data for the specified station

# 3. Determine the min number of weather stations I need to poll for weather data
# 4. Test writing station status data to a Postgres DB
# 5. Test writing weather data to a Postgres DB
# 2. Read pandas JSON parsing documentation and use it to streamline my code