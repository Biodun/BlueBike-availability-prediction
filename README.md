BlueBike availability prediction
==============================

Predict availability of n or more bikes at a [BLUEBike station](https://www.bluebikes.com/) based on the time of the day, weather and location.

BlueBike publishes historical data each quarter. These files include:
*   Trip Duration (seconds)
*   Start Time and Date
*   Stop Time and Date
*   Start Station Name & ID
*   End Station Name & ID
*   Bike ID
*   User Type (Casual = Single Trip or Day Pass user; Member = Annual or Monthly Member)
*   Birth Year
*   Gender, self-reported by member

Unfortunately these files do not include real-time station data such as the number of available bikes at a station). This data is retrieved via their real-time General Bikeshare Feed Specification (GBFS) [feed](https://gbfs.bluebikes.com/gbfs/gbfs.json).

## Implementation plan
My plan is to retrieve realtime station and weather data via the BlueBike GBFS feed and [Dark Sky]() API every 30 minutes using an AWS Lambda function (Station data is updated at varying times per station so 30 minutes should be an acceptable frequency). That data will be stored either in an S3 bucket or in a Database (TBD).
BlueBike posts the trip data for the previous month ~20 days after the month end.

### Database schema

I plan to use a Postgres db for storing station status

Data for a single station from https://gbfs.bluebikes.com/gbfs/es/station_status.json query
```json

{
    "station_id":"107", 
    "num_bikes_available":6,
    "num_ebikes_available":0,
    "num_bikes_disabled":0,
    "num_docks_available":13,
    "num_docks_disabled":0,
    "is_installed":1,
    "is_renting":1,
    "is_returning":1,
    "last_reported": 1581794646,
    "eightd_has_available_keys":false,
    "eightd_active_station_services":
        [{"id":"6523db73-134d-4f62-af6f-78a8515cc83b"}]
}


```
Database schema

```sql
"station_id": varchar
"num_bikes_available": int
"num_ebikes_available": int
"num_bikes_disabled": int
"num_docks_available": int
"num_docks_disabled": int,
"is_installed": int
"is_renting": bool 
"is_returning":bool
"last_reported": timestamp (e.g. 1581794646)
-- Use the request timestamp and station ID as the primary key

CREATE TABLE raw_station_status (
id SERIAL PRIMARY KEY,
station_id VARCHAR(5),
num_bikes_available SMALLINT,
num_ebikes_available SMALLINT,
num_bikes_disabled SMALLINT,
num_docks_available SMALLINT,
num_docks_disabled SMALLINT,
is_installed BOOL,
is_renting BOOL, 
is_returning BOOL, 
last_reported TIMESTAMP,
timestamp_of_data_read_request TIMESTAMP 
);

```
I'll use the `bluebikes` user for accessing the database and inserting data into it. This user will need to be provided with read and insert permissions for this database. The SQL syntax is `GRANT permission ON tablename TO username`
```sql
GRANT SELECT ON raw_station_status TO bluebikes;
GRANT INSERT ON raw_station_status TO bluebikes;
GRANT UPDATE ON raw_station_status TO bluebikes;
GRANT DELETE ON raw_station_status TO bluebikes; 
```


#### Station data
Data for a single station from https://gbfs.bluebikes.com/gbfs/en/station_information.json.

```json
{
        "station_id": "107",
        "external_id": "f834b99d-0de8-11e7-991c-3863bb43a7d0",
        "name": "Ames St at Main St",
        "short_name": "M32037",
        "lat": 42.3625,
        "lon": -71.08822,
        "region_id": 8,
        "rental_methods": [
          "CREDITCARD",
          "KEY"
        ],
        "capacity": 19,
        "rental_url": "https://www.bluebikes.com/app?station_id=107",
        "electric_bike_surcharge_waiver": false,
        "eightd_has_key_dispenser": false,
        "eightd_station_services": [
          {
            "id": "6523db73-134d-4f62-af6f-78a8515cc83b",
            "service_type": "ATTENDED_SERVICE",
            "bikes_availability": "LIMITED",
            "docks_availability": "LIMITED",
            "name": "Valet Service",
            "description": "",
            "schedule_description": "",
            "link_for_more_info": ""
          }
        ],
        "has_kiosk": true
}
```
Proposed database schema for station data

```sql
CREATE TABLE boston_station_data (
station_id  PRIMARY KEY varchar(5),
external_id varchar(37),
station_name varchar(45),
station_short_name varchar(15),
latitude float,
longitude float,
region_code int,
capacity int,

)
```
## Next steps
1. Resolve the issue of stations that have a timestamp of "1970-01-01 19:00:00" i.e. they aren't being updated so the database write fails
1. Write SQL for creating the `station_data` table
1. Update the `station_status` table to reference the `station_id` column as a foreign key
1. Deploy an AWS lambda function to request station data every 30 minutes

### Weather data

If I pull weather data every 30 minutes, that translates to 48 readings per station per day. The daily free request limit for Dark Sky is 1000 API calls so I can only request for 20 weather stations data per day (960 API calls per day).
The cities/muni's in the data set are:
1. Boston
1. Brookline
1. Cambridge
1. Somerville
1. Everett
1. Dorchester

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
