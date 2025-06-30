# This notebook stores all of the key functions for:
# Extracting the data
# Cleaning the Data
# Analysing the Data


# IMPORT PACKAGES
# Web - Scraping and API Requests
import requests
from httpx import AsyncClient, Response
from parsel import Selector
import parsel
import jmespath
import asyncio
from urllib.parse import urlencode

# Data Manipulation and Analysis
import pandas as pd
from pprint import pprint 
import json
from typing import List
from typing import TypedDict

# Database Connection
from sqlalchemy import create_engine

# File and System Operations
import os
import sys

# DIRECTORY SETUP

### Find the directory of the current file
__file__ = "functions.py"

current_dir = os.path.dirname(os.path.abspath(__file__))

## Set it to be the current path of the system
sys.path.insert(0,os.path.join(current_dir, '..', '..'))

## Set Up The Paths of the Key Outside Directories/Files
credentials_file_path = os.path.join(current_dir, '..', '..', "credentials.json")
data_folder_path = os.path.join(current_dir, '..', '..', "data")

# REQUESTS SETUP
# 1. establish HTTP client with browser-like headers to avoid being blocked
client = AsyncClient(headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", # mimic browser use (baseline)
    "Accept": "application/json",  # Accept json apis
    "Referer": "https://www.rightmove.co.uk/",  # Helps mimic browser use
})



# THE FUNCTIONS

## EXTRACTION

### Function to find locations
async def find_locations(query: str) -> List[str]:
    """use rightmove's typeahead api to find location IDs. Returns list of location IDs in most likely order"""
    # Tokenize the query string into two-character segments separated by slashes, as required by the API
    tokenize_query = "".join(c + ("/" if i % 2 == 0 else "") for i, c in enumerate(query.upper(), start=1))
    # Construct the URL for the typeahead API using the tokenized query
    url = f"https://www.rightmove.co.uk/typeAhead/uknostreet/{tokenize_query.strip('/')}/"
    # Make an asynchronous GET request to the API
    response = await client.get(url)
    # Parse the JSON response from the API
    data = json.loads(response.text)
    # Extract and return the list of location identifiers from the response
    return [prediction["locationIdentifier"] for prediction in data["typeAheadLocations"]]


### Function to scrape results for a given location for multiple pages
async def scrape_search(location_id: str) -> str:
    """
    Scrapes rental property listings from Rightmove for a given location identifier, handling pagination and returning all results.
    """
    RESULTS_PER_PAGE = 24

    def make_url(offset: int) -> str:
        url = "https://www.rightmove.co.uk/api/_search?"
        params = {
            "areaSizeUnit": "sqm", # the units for the size of each property
            "channel": "RENT",  # BUY or RENT - for my puyrposes, rent is the most relevant
            "currencyCode": "GBP", # chosen currency
            "includeSSTC": "false", # an empty search parameter
            "index": offset, # the number of the search result/property displayed at the start of the page 
            "isFetching": "false", 
            "locationIdentifier": location_id, # the location we wish to search for (London)
            "numberOfPropertiesPerPage": RESULTS_PER_PAGE,
            "radius": "0.0", # how far away we are allowed to be from the geographgical boundaries of the region
            "sortType": "6", # the sorting mechanism for search results
            "viewType": "LIST", # how results appear
        }
        return url + urlencode(params)

    # Build the URL for the first page of results
    url = make_url(0)
    # print(f"Requesting URL: {url}")
    # Send the request to the Rightmove API for the first page
    first_page = await client.get(url)
    # print(f"First page status: {first_page.status_code}")
    # Parse the JSON response from the first page
    first_page_data = first_page.json()
    results = first_page_data["properties"]
    total_results = len(results)

    # Prepare to fetch additional pages if there are more results
    other_pages = []
    # rightmove sets the API limit to 1000 properties, but here max_api_results is set to 20 for demonstration/testing
    max_api_results = 20    
    # The 'index' parameter in the URL specifies the starting property for each page
    for offset in range(RESULTS_PER_PAGE, total_results, RESULTS_PER_PAGE):
        # Stop scraping more pages when the scraper reaches the API limit
        if offset >= max_api_results: 
            break
        # print(f"Scheduling request for offset: {offset}")
        # Schedule the request for the next page
        other_pages.append(client.get(make_url(offset)))
    # Asynchronously (using async) gather and process all additional page responses
    for response in asyncio.as_completed(other_pages):
        response = await response
        # print(f"Received response for additional page: {response.status_code}")
        data = json.loads(response.text)
        results.extend(data['properties'])
    
    # display the number of results that we managed to parse across multiple pages
    total_results = len(results)
    print(f"Found {total_results} properties")
    return results



## CLEANING

### A function that filters out only the desired columns
def filter_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the input DataFrame to retain only the columns relevant for property analysis.

    Args:
        df (pd.DataFrame): The DataFrame to filter. 

    Returns:
        pd.DataFrame: A DataFrame containing only the selected columns of interest.
    """
    # Define the list of columns to keep in the filtered DataFrame
    base_cols = [
        'id',
        'bedrooms',
        'bathrooms',
        'numberOfImages',
        'displayAddress',
        'location.latitude',
        'location.longitude',
        'propertySubType',
        'listingUpdate.listingUpdateReason',
        'listingUpdate.listingUpdateDate',
        'price.amount',
        'price.frequency',
        'premiumListing',
        'featuredProperty',
        'transactionType',
        'students',
        'displaySize',
        'propertyUrl',
        'firstVisibleDate',
        'addedOrReduced',
        'propertyTypeFullDescription'
    ]
    # Assign the columns of interest (can be extended or modified if needed)
    columns_of_interest = base_cols
    # Filter the DataFrame to include only the columns of interest
    filtered_df = df[columns_of_interest]
    # Return the filtered DataFrame
    return filtered_df


# TRAVEL TIME DATA

## Define a function that generates a payload to pass into the API

def create_payload(df: pd.DataFrame, search_id: str="1", transportation_type: str = "public_transport") -> dict:
    """
    Creates a payload dictionary for the TravelTime API using property locations from a DataFrame.
    The payload includes an origin (Bank Station) and destination locations (properties), 
    and sets up the search parameters for a one-to-many public transport commute time query.
    """
    # Define origin (Bank Station - a key commuting hub)
    origin = {
        "id": "Origin",
        "coords": {"lat": 51.513, "lng": -0.088}
    }
    # Ensure the 'id' column is of string type for API compatibility
    df["id"] = df["id"].astype(str)

    # Select and rename latitude/longitude columns for API format
    locations = df[["id", "location.latitude", "location.longitude"]].rename(
        columns={"location.latitude": "lat", "location.longitude": "lng"}
    )

    # Convert DataFrame rows to a list of dicts for each destination
    destinations = locations.to_dict(orient="records")
    destination_locations = [
        {
            "id": d["id"],
            "coords": {"lat": d["lat"], "lng": d["lng"]}
        } for d in destinations
    ]

    # Build the final payload structure for the API request
    payload = {
        "arrival_searches": {
            "one_to_many": [
                {
                    "id": search_id,  # Unique search identifier
                    "departure_location_id": "Origin",  # Start from Bank Station
                    "arrival_location_ids": df["id"].tolist(),  # List of property IDs as destinations
                    "transportation": {"type": transportation_type},  # Mode of transport
                    "travel_time": 10800,  # Max travel time in seconds (3 hours)
                    "arrival_time_period": "weekday_morning",  # Commute time window
                    "properties": ["travel_time", "distance"]  # Data to return
                }
            ]
        },
        "locations": [origin] + destination_locations  # All locations (origin + destinations)
    }

    return payload

