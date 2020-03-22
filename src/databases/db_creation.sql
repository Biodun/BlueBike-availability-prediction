-- Database setup
-- #######
--
-- createdb bike_shares
-- psql bike_shares
CREATE DATABASE bike_shares;
CREATE SCHEMA blue_bikes;
CREATE ROLE readwrite;
-- Allow this role to connect to this database
GRANT CONNECT ON DATABASE bike_shares TO readwrite;
-- Allow this role to use the schema and create new objects in the schema
GRANT USAGE, CREATE ON SCHEMA blue_bikes TO readwrite;

-- Create the database tables
CREATE TABLE blue_bikes.raw_station_status (
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
last_reported TIMESTAMPTZ,
timestamp_of_data_read_request TIMESTAMPTZ 
);

-- Grant access to the relevant tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA blue_bikes TO readwrite;
-- Allow this role to have similar permissions on any tables created in the future
ALTER DEFAULT PRIVILEGES IN SCHEMA blue_bikes GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO readwrite; 
-- Allow this user to write to all sequences in the schema
GRANT USAGE ON ALL SEQUENCES IN SCHEMA blue_bikes TO readwrite; 
ALTER DEFAULT PRIVILEGES IN SCHEMA blue_bikes GRANT USAGE ON SEQUENCES TO readwrite;

-- Create user
CREATE USER bluebikes WITH PASSWORD 'bluebikes_1';
GRANT readwrite TO bluebikes;