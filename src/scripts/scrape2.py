import asyncio
from httpx import AsyncClient

async def fetch_html(url):
    async with AsyncClient(headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
    }) as client:
        response = await client.get(url)
        print(response.text)  # Full HTML of the page
        return response.text

url = "https://www.rightmove.co.uk/properties/163907069#/"
asyncio.run(fetch_html(url))
