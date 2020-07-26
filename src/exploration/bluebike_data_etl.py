"""
Date: 3rd March 2020
Author: Biodun Iwayemi

ETL for Bluebikes data:
* Data retrieval
* Timestamp parsing
* Saving data to a Postgres DB
"""
#%%

import requests
import pandas as pd 
import json 
import sqlalchemy
from datetime import datetime
from pathlib import Path
from time import sleep
from dotenv import load_dotenv
import os

#%% Import environment variables
load_dotenv()
DB_URL = os.getenv("AWS_POSTGRES_HOST")

#%%
DATA_PATH = Path("../../data/interim/")
WEATHER_SAVE_DATA_PATH = DATA_PATH / 'weather'
STATION_SAVE_DATA_PATH = DATA_PATH / 'stationdata'
#%%
# engine = sqlalchemy.create_engine("postgresql://bluebikes:bluebikes@localhost/blue_bikes")
engine = sqlalchemy.create_engine(f"postgresql://bluebikes:bluebikes_1@{DB_URL}/bike_shares")
# engine = sqlalchemy.create_engine(f"postgresql://postgres:postgresBio1@{DB_URL}/bike_shares")


connection = engine.connect()

#%%
STATION_STATUS_URL = "https://gbfs.bluebikes.com/gbfs/en/station_status.json"
STATION_INFORMATION_URL = "https://gbfs.bluebikes.com/gbfs/en/station_information.json"
#%%

def retrieve_station_status():
    """ Retrieve bike station status using the BlueBike GBFS
    """
    station_request = requests.get(STATION_STATUS_URL)
    json_data = station_request.json()
    return json_data

def parse_station_status(station_status_dict):
    """Parse dict of station status data"""
    df = pd.DataFrame.from_dict(station_status_dict['data']['stations'])
    # Parse the timestamps in UTC format
    df['last_reported'] = df['last_reported'].apply(lambda x: pd.to_datetime(x, unit='s', utc=True))
    data_read_timestamp = pd.to_datetime(station_status_dict['last_updated'], unit='s')
    df['timestamp_of_data_read_request'] = data_read_timestamp
    # df['data_read_timestamp'] = data_read_timestamp
    # Add a year column
    df['year_station_last_reported'] = df['last_reported'].apply(lambda x: x.year)
    # columns_of_interest = ['station_id', 'num_bikes_available', 'num_ebikes_available', 'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled', 
    # 'is_installed', 'is_renting', 'is_returning', 'timestamp']

    #TODO convert the all the columns with an `is_` prefix to boolean types
    types_to_convert = {'is_installed': bool, 'is_renting': bool, 'is_returning': bool}
    df = df.astype(types_to_convert)

    # df = df[columns_of_interest]
    df.reset_index(drop=True, inplace=True)
    return df

def retrieve_station_data():
    """Retrieve station data"""
    station_data_request = requests.get(STATION_INFORMATION_URL)
    return station_data_request.json()

def parse_station_data(station_data):
    """Parse station data"""
    
    station_data_df = pd.DataFrame.from_dict(station_data['data']['stations'])
    station_data_df['timestamp'] = pd.to_datetime(station_data['last_updated'], unit='s', utc=True)
    columns_to_keep = ['station_id', 'external_id', 'name', 'short_name', 'lat', 'lon',
       'region_id', 'rental_methods', 'capacity', 'rental_url',
       'electric_bike_surcharge_waiver', 'eightd_has_key_dispenser',
       'has_kiosk']
    return station_data_df
#%%
station_status = retrieve_station_status()
station_status_df = parse_station_status(station_status)


#%% save data to disk
timestamp = f"{str(datetime.now()).split('.')[0].replace(' ', '_' )}"
filename = STATION_SAVE_DATA_PATH / f"blue_bike_station_status_{timestamp}.csv"
station_status_df.to_csv(filename)

#%% Filter out stations with a year of 1970
station_status_df = station_status_df[['station_id', 'num_bikes_available', 'num_ebikes_available',
       'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled',
       'is_installed', 'is_renting', 'is_returning', 'last_reported', 'timestamp_of_data_read_request']]
#%% Write the results to the station_status db table
station_status_df.to_sql(schema='blue_bikes', name='raw_station_status', con=connection,
if_exists='append', index=False)


# %% Create a station info table
station_data = retrieve_station_data()
station_data_df = parse_station_data(station_data)

# %% Write station data to db
station_data_df.to_sql(name='station_data', con=connection, index_label='id', index=False)

#%% Poll station data every 10 minutes
loop_control_variable = True
N_MINS_TO_SLEEP = 10 * 60 # 10 minutes or 600 seconds
while loop_control_variable:
    # Retrieve station data
    station_status = retrieve_station_status()
    station_status_df = parse_station_status(station_status)
    # Save results to disk
    timestamp = f"{str(datetime.now()).split('.')[0].replace(' ', '_' )}"
    filename = STATION_SAVE_DATA_PATH / f"blue_bike_station_status_{timestamp}.csv"
    station_status_df.to_csv(filename)
    print(f'Saved data at {timestamp} to disk')
    station_status_df = station_status_df[['station_id', 'num_bikes_available', 'num_ebikes_available',
       'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled',
       'is_installed', 'is_renting', 'is_returning', 'last_reported', 'timestamp_of_data_read_request']]
    station_status_df.to_sql(schema='blue_bikes', name='raw_station_status', con=connection,if_exists='append', index=False)
    print('Wrote data to DB')
    sleep(N_MINS_TO_SLEEP)


# %%
