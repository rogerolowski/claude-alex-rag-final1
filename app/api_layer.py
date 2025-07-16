# Unified LEGO API interface 
import requests
import brickse
import json
from rebrick import Rebrick
from models import LegoSet
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

# DEBUG: Print the loaded API keys to verify .env loading
print("DEBUG: BRICKSET_API_KEY =", os.getenv("BRICKSET_API_KEY"))
print("DEBUG: BRICKSET_USERNAME =", os.getenv("BRICKSET_USERNAME"))
print("DEBUG: BRICKSET_PASSWORD =", os.getenv("BRICKSET_PASSWORD"))
print("DEBUG: REBRICKABLE_API_KEY =", os.getenv("REBRICKABLE_API_KEY"))
print("DEBUG: BRICKOWL_API_KEY =", os.getenv("BRICKOWL_API_KEY"))

# DEBUG: Check if .env file exists and is readable
env_file_path = os.path.join(os.getcwd(), '.env')
print(f"DEBUG: .env file exists: {os.path.exists(env_file_path)}")
if os.path.exists(env_file_path):
    print(f"DEBUG: .env file size: {os.path.getsize(env_file_path)} bytes")

def init_brickset():
    """Initialize brickse with available credentials"""
    api_key = os.getenv("BRICKSET_API_KEY")
    username = os.getenv("BRICKSET_USERNAME")
    password = os.getenv("BRICKSET_PASSWORD")
    
    if not api_key:
        print("DEBUG: ❌ ERROR - No BRICKSET_API_KEY provided!")
        return False
        
    try:
        if username and password:
            print("DEBUG: 🔐 Initializing brickse with username/password authentication...")
            brickse.init(api_key, username, password)
            print("DEBUG: ✅ brickse initialized with username/password")
        else:
            print("DEBUG: 🔑 Initializing brickse with API key only...")
            brickse.init(api_key)
            print("DEBUG: ✅ brickse initialized with API key only")
            
        return True
        
    except Exception as e:
        print(f"DEBUG: ❌ Failed to initialize brickse: {e}")
        return False

def search_brickset_sets(query: str, page_size=5, page_number=1):
    """Search for LEGO sets using brickse"""
    print(f"DEBUG: search_brickset_sets called with query: '{query}'")
    
    try:
        print("DEBUG: 🔍 Searching for sets using brickse.lego.get_sets...")
        
        # Use brickse to search for sets
        response = brickse.lego.get_sets(query=query)
        
        # Parse the response
        data = json.loads(response.read())
        print(f"DEBUG: ✅ brickse search successful")
        print(f"DEBUG: Response type: {type(data)}")
        
        # Handle different response formats
        if isinstance(data, dict) and 'sets' in data:
            sets = data['sets']
            print(f"DEBUG: ✅ Found {len(sets)} sets")
            return sets
        elif isinstance(data, list):
            print(f"DEBUG: ✅ Found {len(data)} sets (direct list)")
            return data
        else:
            print(f"DEBUG: ⚠️ Unexpected response format: {data}")
            return []
            
    except Exception as e:
        print(f"DEBUG: ❌ brickse search failed: {e}")
        return []

def get_brickset_set(set_id: str):
    """Get a specific LEGO set by ID using brickse"""
    print(f"DEBUG: get_brickset_set called with set_id: '{set_id}'")
    
    try:
        print("DEBUG: 🔍 Getting set details using brickse.lego.get_set...")
        
        # Use brickse to get specific set
        response = brickse.lego.get_set(set_number=set_id)
        data = json.loads(response.read())
        
        print(f"DEBUG: ✅ brickse get_set successful")
        print(f"DEBUG: Response type: {type(data)}")
        
        # Handle different response formats
        if isinstance(data, dict) and 'sets' in data:
            sets = data['sets']
            if sets:
                print(f"DEBUG: ✅ Found set: {sets[0].get('name', 'Unknown')}")
                return sets[0]
        elif isinstance(data, list) and data:
            print(f"DEBUG: ✅ Found set: {data[0].get('name', 'Unknown')}")
            return data[0]
        else:
            print(f"DEBUG: ⚠️ Set not found or unexpected format: {data}")
            return None
            
    except Exception as e:
        print(f"DEBUG: ❌ brickse get_set failed: {e}")
        return None

def test_brickset_api():
    """Test brickse API with a simple query"""
    print("DEBUG: Testing brickse with simple query 'star'...")
    test_results = search_brickset_sets("star")
    print(f"DEBUG: brickse test returned {len(test_results)} results")
    if test_results:
        print("DEBUG: ✅ brickse API test successful")
    else:
        print("DEBUG: ❌ brickse API test failed")
    return test_results

class LegoAPI:
    def __init__(self):
        brickset_key = os.getenv("BRICKSET_API_KEY")
        brickset_username = os.getenv("BRICKSET_USERNAME")
        brickset_password = os.getenv("BRICKSET_PASSWORD")
        rebrickable_key = os.getenv("REBRICKABLE_API_KEY")
        brickowl_key = os.getenv("BRICKOWL_API_KEY")
        
        print(f"DEBUG: LegoAPI initialization:")
        print(f"DEBUG: - Brickset key: {brickset_key[:10] if brickset_key else 'None'}...")
        print(f"DEBUG: - Brickset username: {brickset_username}")
        print(f"DEBUG: - Brickset password: {'*' * len(brickset_password) if brickset_password else 'None'}")
        print(f"DEBUG: - Rebrickable key: {rebrickable_key[:10] if rebrickable_key else 'None'}...")
        print(f"DEBUG: - BrickOwl key: {brickowl_key[:10] if brickowl_key else 'None'}...")
        
        # DEBUG: Validate API keys and credentials
        missing_credentials = []
        if not brickset_key:
            missing_credentials.append("BRICKSET_API_KEY")
        if not brickset_username:
            missing_credentials.append("BRICKSET_USERNAME")
        if not brickset_password:
            missing_credentials.append("BRICKSET_PASSWORD")
        
        if missing_credentials:
            print(f"DEBUG: ⚠️ Missing credentials: {', '.join(missing_credentials)}")
            if "BRICKSET_USERNAME" in missing_credentials or "BRICKSET_PASSWORD" in missing_credentials:
                print("DEBUG: ⚠️ Brickset authentication may be limited without username/password")
        else:
            print("DEBUG: ✅ All Brickset credentials present")
        
        if not rebrickable_key:
            print("DEBUG: ⚠️ WARNING - REBRICKABLE_API_KEY is missing!")
        if not brickowl_key:
            print("DEBUG: ⚠️ WARNING - BRICKOWL_API_KEY is missing!")
        
        # Initialize brickse
        self.brickset_initialized = init_brickset()
        self.rebrickable = Rebrick(api_key=rebrickable_key) if rebrickable_key else None
        self.brickowl_key = brickowl_key
        
        # DEBUG: Test simple query on initialization
        if self.brickset_initialized:
            print("DEBUG: Running initial API test...")
            test_brickset_api()
        else:
            print("DEBUG: Skipping API test - brickse not initialized")

    def fetch_set(self, set_id: str) -> LegoSet:
        """
        Fetches full set details from Brickset, Rebrickable, and BrickOwl APIs and combines them into a LegoSet model.
        Use this when the user selects a set for more info (hybrid approach).
        """
        print(f"DEBUG: fetch_set called for set_id: {set_id}")
        
        # Brickset: Get set details
        brickset_data = get_brickset_set(set_id)
        if not brickset_data:
            raise ValueError(f"Set {set_id} not found in Brickset API.")

        # Rebrickable: Get parts and minifigs
        rebrickable_data = {}
        if self.rebrickable:
            try:
                rebrickable_data = self.rebrickable.get_set(set_id)
                print(f"DEBUG: Rebrickable data: {rebrickable_data}")
            except Exception as e:
                print(f"DEBUG: Rebrickable error: {e}")

        # BrickOwl: Get pricing
        brickowl_response = {}
        if self.brickowl_key:
            try:
                brickowl_response = requests.get(
                    f"https://api.brickowl.com/v1/catalog/get_set?set_id={set_id}",
                    headers={"Authorization": f"Bearer {self.brickowl_key}"}
                ).json()
                print(f"DEBUG: BrickOwl response: {brickowl_response}")
            except Exception as e:
                print(f"DEBUG: BrickOwl error: {e}")

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
        
        # Search using brickse
        brickset_results = search_brickset_sets(query)
        print(f"DEBUG: Brickset returned {len(brickset_results)} raw results")
        
        # If no results, try a simpler query as fallback
        if len(brickset_results) == 0 and len(query) > 3:
            print(f"DEBUG: No results for '{query}', trying simpler query...")
            simple_query = query.split()[0]  # Use first word
            brickset_results = search_brickset_sets(simple_query)
            print(f"DEBUG: Simpler query '{simple_query}' returned {len(brickset_results)} results")
        
        # Convert to LegoSet objects
        lego_sets = [
            LegoSet(
                set_id=s.get("setID", s.get("number", "")),
                name=s.get("name", ""),
                theme=s.get("theme", ""),
                piece_count=s.get("pieces", 0),
                price=None,  # Price and full details fetched only on demand
                release_year=s.get("year", None),
                description=s.get("description", "")
            )
            for s in brickset_results
        ]
        
        print(f"DEBUG: search_sets returning {len(lego_sets)} LegoSet objects")
        return lego_sets