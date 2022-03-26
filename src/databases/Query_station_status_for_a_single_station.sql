select  id
,station_id
,num_bikes_available
,num_ebikes_available
,num_bikes_disabled
,num_docks_available
,num_docks_disabled
,is_installed
,is_renting
,is_returning
,last_reported
,timestamp_of_data_read_request
from blue_bikes.raw_station_status
WHERE station_id = '107';