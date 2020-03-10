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
import psycopg2
from psycopg2 import OperationalError
import sqlalchemy


engine = sqlalchemy.create_engine("postgresql://bluebikes:bluebikes@localhost/blue_bikes")
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
    df = pd.DataFrame.from_dict(station_status_dict)
    # Parse the timestamps in UTC format
    df['timestamp'] = df['last_reported'].apply(lambda x: pd.to_datetime(x, unit='s', utc=True))
    columns_of_interest = ['station_id', 'num_bikes_available', 'num_ebikes_available', 'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled', 
    'is_installed', 'is_renting', 'is_returning', 'timestamp']

    #TODO convert the all the columns with an `is_` prefix to boolean types
    types_to_convert = {'is_installed': bool, 'is_renting': bool, 'is_returning': bool}
    df = df.astype(types_to_convert)

    df = df[columns_of_interest]
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
station_status = retrieve_station_status()['data']['stations']
station_status_df = parse_station_status(station_status)

#%% Write the results to the station_status db table
station_status_df.to_sql(name='station_status', con=connection,if_exists='append', index_label='id')


# %% Create a station info table
station_data = retrieve_station_data()
station_data_df = parse_station_data(station_data)

# %% Write station data to db
station_data_df.to_sql(name='station_data', con=connection, index_label='id')
