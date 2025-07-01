
# Running scripts asynchronously
import asyncio

# Response output
import json
import pandas as pd

# File and System Operations
import os
import sys

# Saving out data
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

# open the json data
logging.info('Importing Scraped Data')
with open(f"{data_folder_path}/rightmove_properties.json", "r", encoding="utf-8") as f:
    data = json.load(f)

logging.info('Cleaning Scraped Data')
# normalise the data
data_norm = pd.json_normalize(data, max_level = 1)

# filter out only the desired columns
filtered_df = rent.filter_df(data_norm)

# clean the column names
clean_df = rent.clean_column_names(filtered_df)
logging.info('Scraped Data Cleaned')



# Save out to a database

## Get the database engine
logging.info("Connecting to the Database...")
engine = sqlq.get_sql_engine(f"{data_folder_path}/properties.db")



## Execute the CREATE TABLE query to create a blank table
with engine.connect() as connection:
    connection.execute(text(sqlq.CREATE_TABLE_SQL_QUERY))

## Save the dataframe into that table, extending it by default
sqlq.make_table(clean_df, "properties_data", engine)
logging.info('Saved to Database')
