

# Response output
import json
import pandas as pd

# File and System Operations
import os
import sys

# Data Visualisation
import seaborn as sns
import matplotlib.pyplot as plt

# Regressions
from sklearn.linear_model import LinearRegression

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
engine = sqlq.get_sql_engine(f"{data_folder_path}/properties.db")
with engine.connect() as connection:
    properties_data = pd.read_sql(text(sqlq.GET_PROPERTIES_DATA_SQL_QUERY), connection)
logging.info(f'Data found, with {len(properties_data["id"])} properties')


## Filter out only the monthly Contracts
reg_data = properties_data[properties_data["priceFrequency"] == "monthly"]

# make sure price per bed is between 100 and 10k (not null or inf)
reg_data = reg_data[pd.to_numeric(reg_data["price_per_bed"], errors="coerce").between(100, 10000)]

## Make A Scatter Plot of Rent Per Bed Against Travel Time
# allow the user to choose
show_plot = input("Do you want to display the plot? (y/n): ").strip().lower()

if show_plot == 'y':
    sns.regplot(x='travel_time', y='price_per_bed', data=reg_data)
    plt.xlabel('Travel Time')
    plt.ylabel('Price per Bed')
    plt.title('Price per Bed vs Travel Time with Line of Best Fit')
    plt.show()
else:
    print("Plot display skipped.")



# MAKE PREDICTIONS OF RENT PER BED BASED ON THE RENTAL DATA

# Select features and target
X = reg_data[['travel_time', 'bathrooms']]
y = reg_data['price_per_bed']

# Create and fit model
model = LinearRegression()
model.fit(X, y)

# To generate predictions 
predictions = model.predict(X)

# Add predictions to dataframe
reg_data.loc[:,'predicted_price_per_bed'] = predictions


# Save Out The Data With Predictions
# Save the filled-in dataframe into the pre-existing table, replacing the incomplete with the complete data
sqlq.make_table(reg_data, "properties_data", engine, if_exists='replace')

