
# Running scripts asynchronously
import asyncio

# Response output
import json

# File and System Operations
import os
import sys

# Tracking
import logging


# Set up logging to debug/ keep track

logging.basicConfig(format='%(asctime)s [%(levelname)s] [%(filename)s] %(message)s', level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)


# DIRECTORY SETUP

### Find the directory of the current file
__file__ = "nb01.py"

logging.info('Finding current Path')
current_dir = os.path.dirname(os.path.abspath(__file__))

## Set the parent to be the current path of the system
# # (so one can import the custom package)
logging.info('Importing Custom Package...')
sys.path.insert(0,os.path.join(current_dir, '..'))
import rental_utils
from rental_utils import functions as rent
# Note that whenever rent.function_name is called, 
# all the required packages are imported in the background anyway
logging.info('Imported Custom Package')


## Set Up The Paths of the Key Outside Directories/Files
logging.info('Setting up other paths...')
credentials_file_path = os.path.join(current_dir, '..', '..', "credentials.json")
data_folder_path = os.path.join(current_dir, '..', '..', "data")




# PRIMARY RUNNING

## Ask the user for a chosen UK City
location_input = input("Please type a UK town or city (default: London): ")
if not location_input.strip():
    location_input = "london"
print(f"You entered: {location_input}")

## Ask the user for how many properties they wish to systematically go through
total_results_input = input("How many flats do you want to scrape through? (Default, 250): ")
if not total_results_input.strip():
    total_results_input = 250
print(f"You entered: {total_results_input}")


# Run the scraping
async def run():
    chosen_id = (await rent.find_locations(location_input))[0]
    logging.info(f'City id found to be: {chosen_id}')
    chosen_results = await rent.scrape_search(chosen_id, int(total_results_input))
    print_input = input("Print Results? [y/n]")
    if str.lower(print_input) == "y":
        print(json.dumps(chosen_results, indent=2))

    # Output the raw-ish data to a json    
    logging.info('Saving Json Output')
    with open(f"{data_folder_path}/rightmove_properties.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(chosen_results, indent=2))
    logging.info(f'Json output saved to {data_folder_path}/rightmove_properties.json')

if __name__ == "__main__":
    asyncio.run(run())




