import requests
import os
from dotenv import load_dotenv

load_dotenv()
AZURE_MAPS_SUBSCRIPTION_KEY = os.getenv("AZURE_MAPS_KEY")

def geocode_address(address: str):
    url = "https://atlas.microsoft.com/search/address/json"
    params = {
        "subscription-key": AZURE_MAPS_SUBSCRIPTION_KEY,
        "api-version": "1.0",
        "query": address
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        result = response.json()
        if result.get("results"):
            pos = result["results"][0]["position"]
            return address, pos["lat"], pos["lon"]
    except:
        pass
    return address, None, None

