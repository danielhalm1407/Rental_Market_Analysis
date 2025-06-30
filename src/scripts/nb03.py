
# Response output
import json
import pandas as pd

# File and System Operations
import os
import sys

# Saving out data
import requests
from sqlalchemy import inspect, text

# Tracking
import logging


# Set up logging to debug/ keep track

logging.basicConfig(format='%(asctime)s [%(levelname)s] [%(filename)s] %(message)s', level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)


# DIRECTORY SETUP

### Find the directory of the current file
__file__ = "nb02.py"

logging.info('Finding current Path')
current_dir = os.path.dirname(os.path.abspath(__file__))

## Set the parent to be the current path of the system
# # (so one can import the custom package)
logging.info('Importing Custom Package...')
sys.path.insert(0,os.path.join(current_dir, '..'))
import rental_utils
# Import the functions sub-package
from rental_utils import functions as rent
# Note that whenever rent.function_name is called, 
# all the required packages are imported in the background anyway

# Import the sql queries sub-package
from rental_utils import sql_queries as sqlq

logging.info('Imported Custom Package')


## Set Up The Paths of the Key Outside Directories/Files
logging.info('Setting up other paths...')
credentials_file_path = os.path.join(current_dir, '..', '..', "credentials.json")
data_folder_path = os.path.join(current_dir, '..', '..', "data")




# PRIMARY RUNNING

## Get The Credentials
with open(credentials_file_path, "r") as f:
    credentials = json.load(f)

logging.info(f'The Following Credentials Will Be Used:{credentials}')


## Load in the data from the corresponding table in the database
logging.info('Getting Data from the Database')
engine = sqlq.get_sql_engine(f"{data_folder_path}/properties.db")
with engine.connect() as connection:
    rightmove_data = pd.read_sql(text(sqlq.GET_PROPERTIES_DATA_SQL_QUERY), connection)
logging.info(f'Data found, with {len(rightmove_data["id"])} properties')

## Set Up The Headers
logging.info("Creating Payload and Setting Up Headers")
headers = {
    "Content-Type": "application/json",
    "X-Application-Id": credentials["app_id"],
    "X-Api-Key": credentials["api_key"]
}

## Create the Payload Based on our data
payload_1 = rent.create_payload(rightmove_data)


logging.info("Payload Ready, Making the Request...")
## Make the request to get the travel times
### Make the request
response = requests.post(
    "https://api.traveltimeapp.com/v4/time-filter/fast",
    headers= headers,
    data=json.dumps(payload_1)
)
### Log if the response was OK
if response.status_code == 200:
    logging.info("Received Valid Response")
else: 
    logging.info("Received Invalid Response")


### Get the nested part of the json response that is relevant
results = response.json()["results"][0]["locations"]

### Convert to DataFrame
df_results = pd.DataFrame([
    {
        "id": loc["id"],
        "distance": loc["properties"]["distance"],
        "travel_time": loc["properties"]["travel_time"]
    }
    for loc in results
])

### Merge this dataframe with the original dataframe
properties_data = df_results.merge(
    rightmove_data.drop(columns=["travel_time","distance"]),
      on="id", how="left")

# Save the filled-in dataframe into the pre-existing table, replacing the incomplete with the complete data
sqlq.make_table(properties_data, "properties_data", engine, if_exists='replace')
logging.info("Saved Travel Time Data to the DataBase")