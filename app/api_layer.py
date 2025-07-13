# Unified LEGO API interface 
import requests
from rebrick import Rebrick
from brickse import Brickset
from models import LegoSet
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

class LegoAPI:
    def __init__(self):
        self.brickset = Brickset(api_key=os.getenv("BRICKSET_API_KEY"))
        self.rebrickable = Rebrick(api_key=os.getenv("REBRICKABLE_API_KEY"))
        self.brickowl_key = os.getenv("BRICKOWL_API_KEY")

    def fetch_set(self, set_id: str) -> LegoSet:
        # Brickset: Get set details
        brickset_data = self.brickset.get_set(set_id)
        # Rebrickable: Get parts and minifigs
        rebrickable_data = self.rebrickable.get_set(set_id)
        # BrickOwl: Get pricing
        brickowl_response = requests.get(
            f"https://api.brickowl.com/v1/catalog/get_set?set_id={set_id}",
            headers={"Authorization": f"Bearer {self.brickowl_key}"}
        ).json()

        # Combine data
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
        # Example: Search across APIs
        brickset_results = self.brickset.search(query)
        return [self.fetch_set(set["setID"]) for set in brickset_results[:5]]