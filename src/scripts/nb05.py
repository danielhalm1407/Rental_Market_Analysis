

# Response output
import json
import pandas as pd

# File and System Operations
import os
import sys


# url displays
from IPython.display import display, Markdown


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


## Load in the complete data from the corresponding table in the database
logging.info('Getting Data from the Database')
# connect to the database
supabase_engine = sqlq.get_supabase_engine(
    user="postgres",
    password="Roakla_235%",
    host="db.svwbxdbftbrihozrebzl.supabase.co",
    port=5432,
    database="postgres"
)


# extract the table from the database
with supabase_engine.connect() as connection:
    properties_data = pd.read_sql(text(sqlq.GET_PROPERTIES_DATA_SQL_QUERY), connection)
    
logging.info(f'Data found, with {len(properties_data["id"])} properties')


## Help a user find underpriced flats

### ask a user for the budget they have to spend on rent
user_budget_input = input("What is your desired monthly budget on rent? ").strip()
### set the budget as 1000 to default if the user does not input a number
user_budget = int(user_budget_input) if user_budget_input else 1000

sorted_data = rent.find_underpriced(properties_data, user_budget)

