# Unified LEGO API interface 
import requests
from rebrick import Rebrick
from models import LegoSet
from typing import List
from dotenv import load_dotenv
import os
import json

load_dotenv()

# DEBUG: Print the loaded Brickset API key to verify .env loading
print("DEBUG: BRICKSET_API_KEY =", os.getenv("BRICKSET_API_KEY"))
print("DEBUG: REBRICKABLE_API_KEY =", os.getenv("REBRICKABLE_API_KEY"))
print("DEBUG: BRICKOWL_API_KEY =", os.getenv("BRICKOWL_API_KEY"))

# DEBUG: Check if .env file exists and is readable
env_file_path = os.path.join(os.getcwd(), '.env')
print(f"DEBUG: .env file exists: {os.path.exists(env_file_path)}")
if os.path.exists(env_file_path):
    print(f"DEBUG: .env file size: {os.path.getsize(env_file_path)} bytes")

class BricksetAPIv3:
    BASE_URL = "https://brickset.com/api/v3.asmx"

    def __init__(self, api_key: str):
        self.api_key = api_key
        print(f"DEBUG: BricksetAPIv3 initialized with key: {self.api_key[:10]}..." if self.api_key else "DEBUG: BricksetAPIv3 initialized with NO KEY")
        
        # DEBUG: Test API connectivity
        self.test_api_connectivity()

    def test_api_connectivity(self):
        """Test if we can reach the Brickset API endpoint"""
        try:
            print("DEBUG: Testing Brickset API connectivity...")
            response = requests.get(self.BASE_URL, timeout=10)
            print(f"DEBUG: Brickset API endpoint reachable: {response.status_code}")
        except Exception as e:
            print(f"DEBUG: Brickset API connectivity test failed: {e}")

    def get_sets(self, query: str):
        # DEBUG: Print the search query and API key being used
        print(f"DEBUG: get_sets called with query: '{query}'")
        print(f"DEBUG: Using API key: {self.api_key[:10]}..." if self.api_key else "DEBUG: NO API KEY AVAILABLE")
        
        # DEBUG: Validate API key format
        if not self.api_key:
            print("DEBUG: ERROR - No API key provided!")
            return []
        
        if len(self.api_key) < 10:
            print(f"DEBUG: WARNING - API key seems too short: {len(self.api_key)} characters")
        
        # Calls the Brickset getSets API method with correct params wrapper
        payload = {
            "params": {
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
        }
        
        # DEBUG: Print the request payload
        print(f"DEBUG: Request payload: {payload}")
        
        try:
            print(f"DEBUG: Making POST request to: {self.BASE_URL}/getSets")
            response = requests.post(f"{self.BASE_URL}/getSets", json=payload, timeout=30)
            print(f"DEBUG: Response status code: {response.status_code}")
            print(f"DEBUG: Response headers: {dict(response.headers)}")
            print(f"DEBUG: Response content type: {response.headers.get('content-type', 'unknown')}")
            
            # DEBUG: Print the raw API response for troubleshooting
            response_text = response.text
            print("DEBUG: Brickset API response text:", response_text[:500] + "..." if len(response_text) > 500 else response_text)
            
            # DEBUG: Check for common error patterns in response
            if "error" in response_text.lower():
                print("DEBUG: ERROR keyword found in response")
            if "invalid" in response_text.lower():
                print("DEBUG: INVALID keyword found in response")
            if "unauthorized" in response_text.lower():
                print("DEBUG: UNAUTHORIZED keyword found in response")
            if "rate limit" in response_text.lower():
                print("DEBUG: RATE LIMIT keyword found in response")
            
            # Check if response is successful
            if response.status_code != 200:
                print(f"DEBUG: HTTP Error {response.status_code}: {response_text}")
                return []
            
            # Try to parse as JSON first
            try:
                json_data = response.json()
                print(f"DEBUG: Successfully parsed as JSON: {json_data}")
                
                # DEBUG: Analyze JSON structure
                if isinstance(json_data, dict):
                    print(f"DEBUG: JSON keys: {list(json_data.keys())}")
                    if 'sets' in json_data:
                        print(f"DEBUG: Sets array length: {len(json_data['sets'])}")
                    if 'status' in json_data:
                        print(f"DEBUG: Status: {json_data['status']}")
                    if 'message' in json_data:
                        print(f"DEBUG: Message: {json_data['message']}")
                
                return json_data.get("sets", [])
            except Exception as json_error:
                print(f"DEBUG: JSON parse failed: {json_error}")
                print("DEBUG: Response is not JSON, might be XML or error message")
                
                # DEBUG: Try to identify response format
                if response_text.strip().startswith('<'):
                    print("DEBUG: Response appears to be XML")
                elif response_text.strip().startswith('{'):
                    print("DEBUG: Response appears to be JSON but failed to parse")
                else:
                    print("DEBUG: Response format unclear")
                
                return []
                
        except Exception as request_error:
            print(f"DEBUG: Request failed: {request_error}")
            return []

    def get_set_by_id(self, set_id: str):
        # DEBUG: Print the set ID being requested
        print(f"DEBUG: get_set_by_id called with set_id: '{set_id}'")
        
        # Calls getSets with setNumber to fetch a specific set with correct params wrapper
        payload = {
            "params": {
                "apiKey": self.api_key,
                "userHash": "",
                "setNumber": set_id,
                "pageSize": 1,
                "pageNumber": 1
            }
        }
        
        try:
            response = requests.post(f"{self.BASE_URL}/getSets", json=payload, timeout=30)
            print(f"DEBUG: get_set_by_id response status: {response.status_code}")
            
            # DEBUG: Print the raw API response for troubleshooting
            response_text = response.text
            print("DEBUG: Brickset API response text:", response_text[:500] + "..." if len(response_text) > 500 else response_text)
            
            try:
                sets = response.json().get("sets", [])
                print(f"DEBUG: get_set_by_id found {len(sets)} sets")
                return sets[0] if sets else None
            except Exception as e:
                print("DEBUG: JSON decode error:", e)
                return None
        except Exception as e:
            print(f"DEBUG: get_set_by_id request failed: {e}")
            return None

    def test_simple_query(self):
        """Test with a simple, guaranteed-to-work query"""
        print("DEBUG: Testing with simple query 'star'...")
        test_results = self.get_sets("star")
        print(f"DEBUG: Simple query test returned {len(test_results)} results")
        return test_results

class LegoAPI:
    def __init__(self):
        brickset_key = os.getenv("BRICKSET_API_KEY")
        rebrickable_key = os.getenv("REBRICKABLE_API_KEY")
        brickowl_key = os.getenv("BRICKOWL_API_KEY")
        
        print(f"DEBUG: LegoAPI initialization:")
        print(f"DEBUG: - Brickset key: {brickset_key[:10] if brickset_key else 'None'}...")
        print(f"DEBUG: - Rebrickable key: {rebrickable_key[:10] if rebrickable_key else 'None'}...")
        print(f"DEBUG: - BrickOwl key: {brickowl_key[:10] if brickowl_key else 'None'}...")
        
        # DEBUG: Validate all API keys
        if not brickset_key:
            print("DEBUG: ERROR - BRICKSET_API_KEY is missing!")
        if not rebrickable_key:
            print("DEBUG: WARNING - REBRICKABLE_API_KEY is missing!")
        if not brickowl_key:
            print("DEBUG: WARNING - BRICKOWL_API_KEY is missing!")
        
        self.brickset = BricksetAPIv3(api_key=brickset_key)
        self.rebrickable = Rebrick(api_key=rebrickable_key)
        self.brickowl_key = brickowl_key
        
        # DEBUG: Test simple query on initialization
        if brickset_key:
            print("DEBUG: Running initial API test...")
            self.brickset.test_simple_query()

    def fetch_set(self, set_id: str) -> LegoSet:
        """
        Fetches full set details from Brickset, Rebrickable, and BrickOwl APIs and combines them into a LegoSet model.
        Use this when the user selects a set for more info (hybrid approach).
        """
        print(f"DEBUG: fetch_set called for set_id: {set_id}")
        
        # Brickset: Get set details
        brickset_data = self.brickset.get_set_by_id(set_id)
        if not brickset_data:
            raise ValueError(f"Set {set_id} not found in Brickset API.")

        # Rebrickable: Get parts and minifigs
        try:
            rebrickable_data = self.rebrickable.get_set(set_id)
            print(f"DEBUG: Rebrickable data: {rebrickable_data}")
        except Exception as e:
            print(f"DEBUG: Rebrickable error: {e}")
            rebrickable_data = {}

        # BrickOwl: Get pricing
        try:
            brickowl_response = requests.get(
                f"https://api.brickowl.com/v1/catalog/get_set?set_id={set_id}",
                headers={"Authorization": f"Bearer {self.brickowl_key}"}
            ).json()
            print(f"DEBUG: BrickOwl response: {brickowl_response}")
        except Exception as e:
            print(f"DEBUG: BrickOwl error: {e}")
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
        print(f"DEBUG: search_sets called with query: '{query}'")
        
        # DEBUG: Test with simple query if original fails
        brickset_results = self.brickset.get_sets(query)
        print(f"DEBUG: Brickset returned {len(brickset_results)} raw results")
        
        # If no results, try a simpler query as fallback
        if len(brickset_results) == 0 and len(query) > 3:
            print(f"DEBUG: No results for '{query}', trying simpler query...")
            simple_query = query.split()[0]  # Use first word
            brickset_results = self.brickset.get_sets(simple_query)
            print(f"DEBUG: Simpler query '{simple_query}' returned {len(brickset_results)} results")
        
        # Convert to LegoSet objects
        lego_sets = [
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
        
        print(f"DEBUG: search_sets returning {len(lego_sets)} LegoSet objects")
        return lego_sets