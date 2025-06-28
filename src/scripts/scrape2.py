import asyncio
import json
from typing import List, TypedDict
from urllib.parse import urlencode
from httpx import AsyncClient, Response

# 1. establish HTTP client with browser-like headers to avoid being blocked
client = AsyncClient(
    headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
    }
)


async def find_locations(query: str) -> List[str]:
    """use rightmove's typeahead api to find location IDs. Returns list of location IDs in most likely order"""
    # rightmove uses two character long tokens so "cornwall" becomes "CO/RN/WA/LL"
    tokenize_query = "".join(c + ("/" if i % 2 == 0 else "") for i, c in enumerate(query.upper(), start=1))
    url = f"https://www.rightmove.co.uk/typeAhead/uknostreet/{tokenize_query.strip('/')}/"
    response = await client.get(url)
    data = json.loads(response.text)
    return [prediction["locationIdentifier"] for prediction in data["typeAheadLocations"]]


async def scrape_search(location_id: str) -> dict:
    RESULTS_PER_PAGE = 24

    def make_url(offset: int) -> str:
        url = "https://www.rightmove.co.uk/api/_search?"
        params = {
            "areaSizeUnit": "sqft",
            "channel": "BUY",  # BUY or RENT
            "currencyCode": "GBP",
            "includeSSTC": "false",
            "index": offset,  # page offset
            "isFetching": "false",
            "locationIdentifier": location_id, #e.g.: "REGION^61294", 
            "numberOfPropertiesPerPage": RESULTS_PER_PAGE,
            "radius": "0.0",
            "sortType": "6",
            "viewType": "LIST",
        }
        return url + urlencode(params)
    first_page = await client.get(make_url(0))
    first_page_data = json.loads(first_page.content)
    total_results = int(first_page_data['resultCount'].replace(',', ''))
    results = first_page_data['properties']
    
    other_pages = []
    # rightmove sets the API limit to 1000 properties
    max_api_results = 1000    
    for offset in range(RESULTS_PER_PAGE, total_results, RESULTS_PER_PAGE):
        # stop scraping more pages when the scraper reach the API limit
        if offset >= max_api_results:
            break
        other_pages.append(client.get(make_url(offset)))
    for response in asyncio.as_completed(other_pages):
        response = await response
        data = json.loads(response.text)
        results.extend(data['properties'])
    return results

# Example run:
async def run():
    cornwall_id = (await find_locations("cornwall"))[0]
    print(cornwall_id)
    cornwall_results = await scrape_search(cornwall_id)
    print(json.dumps(cornwall_results, indent=2))

if __name__ == "__main__":
    asyncio.run(run())