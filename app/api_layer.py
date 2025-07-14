# Unified LEGO API interface 
import requests
from rebrick import Rebrick
from models import LegoSet
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

# DEBUG: Print the loaded Brickset API key to verify .env loading
print("DEBUG: BRICKSET_API_KEY =", os.getenv("BRICKSET_API_KEY"))

class BricksetAPIv3:
    BASE_URL = "https://brickset.com/api/v3.asmx"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_sets(self, query: str):
        # Calls the Brickset getSets API method
        payload = {
            "apiKey": self.api_key,
            "userHash": "",
            "query": query,
            "theme": "",
            "subtheme": "",
            "setNumber": "",
            "year": "",
            "owned": "",
            "wanted": "",
            "orderBy": "",
            "pageSize": 5,
            "pageNumber": 1
        }
        response = requests.post(f"{self.BASE_URL}/getSets", data=payload)
        # DEBUG: Print the raw API response for troubleshooting
        print("DEBUG: Brickset API response text:", response.text)
        try:
            return response.json().get("sets", [])
        except Exception as e:
            print("DEBUG: JSON decode error:", e)
            return []

    def get_set_by_id(self, set_id: str):
        # Calls getSets with setNumber to fetch a specific set
        payload = {
            "apiKey": self.api_key,
            "userHash": "",
            "setNumber": set_id,
            "pageSize": 1,
            "pageNumber": 1
        }
        response = requests.post(f"{self.BASE_URL}/getSets", data=payload)
        # DEBUG: Print the raw API response for troubleshooting
        print("DEBUG: Brickset API response text:", response.text)
        try:
            sets = response.json().get("sets", [])
            return sets[0] if sets else None
        except Exception as e:
            print("DEBUG: JSON decode error:", e)
            return None

class LegoAPI:
    def __init__(self):
        self.brickset = BricksetAPIv3(api_key=os.getenv("BRICKSET_API_KEY"))
        self.rebrickable = Rebrick(api_key=os.getenv("REBRICKABLE_API_KEY"))
        self.brickowl_key = os.getenv("BRICKOWL_API_KEY")

    def fetch_set(self, set_id: str) -> LegoSet:
        """
        Fetches full set details from Brickset, Rebrickable, and BrickOwl APIs and combines them into a LegoSet model.
        Use this when the user selects a set for more info (hybrid approach).
        """
        # Brickset: Get set details
        brickset_data = self.brickset.get_set_by_id(set_id)
        if not brickset_data:
            raise ValueError(f"Set {set_id} not found in Brickset API.")

        # Rebrickable: Get parts and minifigs
        try:
            rebrickable_data = self.rebrickable.get_set(set_id)
        except Exception:
            rebrickable_data = {}

        # BrickOwl: Get pricing
        try:
            brickowl_response = requests.get(
                f"https://api.brickowl.com/v1/catalog/get_set?set_id={set_id}",
                headers={"Authorization": f"Bearer {self.brickowl_key}"}
            ).json()
        except Exception:
            brickowl_response = {}

        # Combine data into LegoSet
        lego_set = LegoSet(
            set_id=set_id,
            name=brickset_data.get("name", ""),
            theme=brickset_data.get("theme", ""),
            piece_count=rebrickable_data.get("num_parts", 0),
            price=brickowl_response.get("retail_price", None),
            release_year=brickset_data.get("year", None),
            description=brickset_data.get("description", "")
        )
        return lego_set

    def search_sets(self, query: str) -> List[LegoSet]:
        """
        Hybrid approach: Quickly searches for LEGO sets using the Brickset API and returns a list of LegoSet models with basic info (no price).
        When the user selects a set, call fetch_set(set_id) to get full details and price.
        """
        brickset_results = self.brickset.get_sets(query)
        return [
            LegoSet(
                set_id=s["setID"],
                name=s["name"],
                theme=s["theme"],
                piece_count=s.get("pieces", 0),
                price=None,  # Price and full details fetched only on demand
                release_year=s.get("year", None),
                description=s.get("description", "")
            )
            for s in brickset_results
        ]