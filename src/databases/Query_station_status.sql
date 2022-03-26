SELECT id
,station_id
,num_bikes_available
,num_docks_available
,last_reported
,timestamp_of_data_read_request
from blue_bikes.raw_station_status
ORDER BY 
    station_id,
    last_reported;