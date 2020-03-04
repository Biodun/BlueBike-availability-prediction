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

STATION_INFO_URL = "https://gbfs.bluebikes.com/gbfs/en/station_status.json"
#%%

def retrieve_station_status():
    """ Retrieve bike station status using the BlueBike GBFS
    """
    station_request = requests.get(STATION_INFO_URL)
    json_data = station_request.json()
    return json_data

def parse_station_data(station_data_dict):
    """Parse dict of station status data"""
    df = pd.DataFrame.from_dict(station_data_dict)
    # Parse the timestamps in UTC format
    df['timestamp'] = df['last_reported'].apply(lambda x: pd.to_datetime(x, unit='s', utc=True))
    columns_of_interest = ['station_id', 'num_bikes_available', 'num_ebikes_available', 'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled', 
    'is_installed', 'is_renting', 'is_returning', 'last_reported',  'timestamp']

    return df

#%%
sample_station_data = retrieve_station_status()['data']['stations']
station_df = parse_station_data(sample_station_data)

#%% Create a database table for station data and then write results to the DB

