# Web - Scraping and API Requests
import requests
from httpx import AsyncClient, Response
from parsel import Selector
import parsel
import jmespath
import asyncio

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

# 1. establish HTTP client with browser-like headers to avoid being blocked
client = AsyncClient(
    headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
    }
)

class PropertyResult(TypedDict):
    """this is what our result dataset will look like"""
    id: str
    available: bool
    archived: bool
    phone: str
    bedrooms: int
    bathrooms: int
    type: str
    property_type: str
    tags: list
    description: str
    title: str
    subtitle: str
    price: str
    price_sqft: str
    address: dict
    latitude: float
    longitude: float
    features: list
    history: dict
    photos: list
    floorplans: list
    agency: dict
    industryAffiliations: list
    nearest_airports: list
    nearest_stations: list
    sizings: list
    brochures: list

### Define a function that parses rightmove property data to only get the relevant fields
def parse_property(data) -> PropertyResult:
    """parse rightmove cache data for proprety information"""
    # here we define field name to JMESPath mapping
    parse_map = {
        "id": "id",
        "available": "status.published",
        "archived": "status.archived",
        "phone": "contactInfo.telephoneNumbers.localNumber",
        "bedrooms": "bedrooms",
        "bathrooms": "bathrooms",
        "type": "transactionType",
        "property_type": "propertySubType",
        "tags": "tags",
        "description": "text.description",
        "title": "text.pageTitle",
        "subtitle": "text.propertyPhrase",
        "price": "prices.primaryPrice",
        "price_sqft": "prices.pricePerSqFt",
        "address": "address",
        "latitude": "location.latitude",
        "longitude": "location.longitude",
        "features": "keyFeatures",
        "history": "listingHistory",
        "photos": "images[*].{url: url, caption: caption}",
        "floorplans": "floorplans[*].{url: url, caption: caption}",
        "agency": """customer.{
            id: branchId, 
            branch: branchName, 
            company: companyName, 
            address: displayAddress, 
            commercial: commercial, 
            buildToRent: buildToRent,
            isNew: isNewHomeDeveloper
        }""",
        "industryAffiliations": "industryAffiliations[*].name",
        "nearest_airports": "nearestAirports[*].{name: name, distance: distance}",
        "nearest_stations": "nearestStations[*].{name: name, distance: distance}",
        "sizings": "sizings[*].{unit: unit, min: minimumSize, max: maximumSize}",
        "brochures": "brochures",
    }
    results = {}
    for key, path in parse_map.items():
        value = jmespath.search(path, data)
        results[key] = value
    return results


    
def find_json_objects(text: str, decoder=json.JSONDecoder()):
    """Find JSON objects in text, and generate decoded JSON data"""
    pos = 0
    while True:
        match = text.find("{", pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1


# This function will find the PAGE_MODEL javascript variable and extract it 
def extract_property(response: Response) -> dict:
    """extract property data from rightmove PAGE_MODEL javascript variable"""
    selector = Selector(response.text)
    data = selector.xpath("//script[contains(.,'PAGE_MODEL = ')]/text()").get()
    if not data:
        print(f"page {response.url} is not a property listing page")
        return
    json_data = list(find_json_objects(data))[0]
    return json_data["propertyData"]

### Define the primary scraping function that takes urls and returns the data
async def scrape_properties(urls: List[str]) -> List[dict]:
    """
    Scrape Rightmove property listings from a list of URLs,
    parse relevant fields, and save all results to a single JSON file.
    """
    # Prepare asynchronous GET requests for all URLs using the shared client
    to_scrape = [client.get(url) for url in urls]

    # List to store parsed property data
    properties = []

    # Asynchronously process each response as it completes
    for response in asyncio.as_completed(to_scrape):
        # Await the HTTP response for the property page
        response = await response

        # Extract and parse the property data from the response
        prop = parse_property(extract_property(response))

        # Add the parsed property data to the list
        properties.append(prop)

    # Save all parsed properties as a single JSON array to disk
    with open("../../data/rightmove_properties.json", "w", encoding="utf-8") as f:
        json.dump(properties, f, indent=2)

    # Return the list of parsed property dictionaries
    return properties




async def run():
    data = await scrape_properties([
        "https://www.rightmove.co.uk/properties/163907069#/",
        "https://www.rightmove.co.uk/properties/163907291#/",
    ])

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
