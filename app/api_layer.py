# Unified LEGO API interface 
import requests
from rebrick import Rebrick
from models import LegoSet
from typing import List
from dotenv import load_dotenv
import os
import json

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

class BricksetAPIv3:
    LOGIN_URL = "https://brickset.com/api/v3.asmx/login"
    GETSETS_URL = "https://brickset.com/api/v3.asmx/getSets"

    def __init__(self, api_key, username=None, password=None):
        self.api_key = api_key
        print(f"DEBUG: BricksetAPIv3 initialized with key: {self.api_key[:10]}..." if self.api_key else "DEBUG: BricksetAPIv3 initialized with NO KEY")
        print(f"DEBUG: BricksetAPIv3 initialized with username: {username}")
        
        # Optional authentication - try login if credentials provided
        if username and password:
            print("DEBUG: Attempting login with username/password...")
            self.user_hash = self._login(username, password)
            if self.user_hash:
                print(f"DEBUG: ✅ Login successful, user_hash: {self.user_hash[:10]}...")
                print("DEBUG: ✅ Authentication verified - API calls will work")
            else:
                print("DEBUG: ❌ Login failed - API access may be limited")
                print("DEBUG: ❌ Please check your Brickset credentials in .env file")
        else:
            print("DEBUG: ⚠️ No username/password provided - using API key only")
            print("DEBUG: ⚠️ Note: Brickset may require authentication for most endpoints")
            self.user_hash = None
        
        # DEBUG: Test API connectivity
        self.test_api_connectivity()

    def test_api_connectivity(self):
        """Test if we can reach the Brickset API endpoint"""
        try:
            print("DEBUG: Testing Brickset API connectivity...")
            response = requests.get(self.GETSETS_URL, timeout=10)
            print(f"DEBUG: ✅ Brickset API endpoint reachable: {response.status_code}")
        except Exception as e:
            print(f"DEBUG: ❌ Brickset API connectivity test failed: {e}")

    def _login(self, username, password):
        try:
            print(f"DEBUG: Sending login request to {self.LOGIN_URL}")
            resp = requests.post(
                self.LOGIN_URL,
                json={"params": {
                    "apiKey": self.api_key,
                    "username": username,
                    "password": password
                }},
                timeout=10,
            )
            print(f"DEBUG: Login response status: {resp.status_code}")
            
            resp.raise_for_status()
            data = resp.json()
            print(f"DEBUG: Login response data: {data}")
            
            if data and len(data) > 0 and "hash" in data[0]:
                user_hash = data[0]["hash"]
                print(f"DEBUG: ✅ Successfully extracted user_hash: {user_hash[:10]}...")
                return user_hash
            else:
                print("DEBUG: ❌ Login response missing hash")
                print(f"DEBUG: Response structure: {data}")
                return None
                
        except requests.exceptions.HTTPError as e:
            print(f"DEBUG: ❌ HTTP Error during login: {e}")
            if e.response.status_code == 401:
                print("DEBUG: ❌ 401 Unauthorized - Check your username/password")
            elif e.response.status_code == 403:
                print("DEBUG: ❌ 403 Forbidden - Check your API key")
            return None
        except Exception as e:
            print(f"DEBUG: ❌ Login failed with exception: {e}")
            return None

    def get_sets(self, query, page_size=5, page_number=1):
        # DEBUG: Print the search query and authentication status
        print(f"DEBUG: get_sets called with query: '{query}'")
        print(f"DEBUG: Using API key: {self.api_key[:10]}..." if self.api_key else "DEBUG: ❌ NO API KEY AVAILABLE")
        print(f"DEBUG: Using user_hash: {self.user_hash[:10] if self.user_hash else 'None'}...")
        
        # DEBUG: Validate API key
        if not self.api_key:
            print("DEBUG: ❌ ERROR - No API key provided!")
            return []
        
        if len(self.api_key) < 10:
            print(f"DEBUG: ⚠️ WARNING - API key seems too short: {len(self.api_key)} characters")
        
        # Build payload with conditional userHash
        params = {
            "apiKey": self.api_key,
            "query": query,
            "pageSize": page_size,
            "pageNumber": page_number
        }
        
        # Add userHash if available
        if self.user_hash:
            params["userHash"] = self.user_hash
            print("DEBUG: ✅ Including userHash in request")
        else:
            print("DEBUG: ⚠️ No userHash available - API may reject request")
        
        payload = {"params": params}

        # DEBUG: Print the request payload
        print(f"DEBUG: Request payload: {payload}")
        
        try:
            print(f"DEBUG: Making POST request to: {self.GETSETS_URL}")
            r = requests.post(self.GETSETS_URL, json=payload, timeout=30)
            print(f"DEBUG: Response status code: {r.status_code}")
            print(f"DEBUG: Response headers: {dict(r.headers)}")
            print(f"DEBUG: Response content type: {r.headers.get('content-type', 'unknown')}")
            
            # DEBUG: Print the raw API response for troubleshooting
            response_text = r.text
            print("DEBUG: Brickset API response text:", response_text[:500] + "..." if len(response_text) > 500 else response_text)
            
            # DEBUG: Check for common error patterns in response
            if "error" in response_text.lower():
                print("DEBUG: ⚠️ ERROR keyword found in response")
            if "invalid" in response_text.lower():
                print("DEBUG: ⚠️ INVALID keyword found in response")
            if "unauthorized" in response_text.lower():
                print("DEBUG: ❌ UNAUTHORIZED keyword found in response")
            if "rate limit" in response_text.lower():
                print("DEBUG: ⚠️ RATE LIMIT keyword found in response")
            if "authentication" in response_text.lower():
                print("DEBUG: ❌ AUTHENTICATION keyword found in response")
            if "missing parameter" in response_text.lower():
                print("DEBUG: ❌ MISSING PARAMETER - may need userHash")
            
            r.raise_for_status()
            json_data = r.json()
            print(f"DEBUG: ✅ Successfully parsed as JSON: {json_data}")
            
            # DEBUG: Analyze JSON structure
            if isinstance(json_data, dict):
                print(f"DEBUG: JSON keys: {list(json_data.keys())}")
                if 'sets' in json_data:
                    print(f"DEBUG: ✅ Sets array length: {len(json_data['sets'])}")
                if 'status' in json_data:
                    print(f"DEBUG: Status: {json_data['status']}")
                if 'message' in json_data:
                    print(f"DEBUG: Message: {json_data['message']}")
            
            return json_data.get("sets", [])
                
        except requests.exceptions.HTTPError as e:
            print(f"DEBUG: ❌ HTTP Error during API call: {e}")
            if e.response.status_code == 401:
                print("DEBUG: ❌ 401 Unauthorized - Authentication failed")
                if not self.user_hash:
                    print("DEBUG: 💡 Try adding username/password to .env file")
            elif e.response.status_code == 403:
                print("DEBUG: ❌ 403 Forbidden - Access denied")
            elif e.response.status_code == 500:
                print("DEBUG: ❌ 500 Server Error - may be missing required parameters")
                if not self.user_hash:
                    print("DEBUG: 💡 Try adding username/password to .env file")
            return []
        except Exception as request_error:
            print(f"DEBUG: ❌ Request failed: {request_error}")
            return []

    def get_set_by_id(self, set_id: str):
        # DEBUG: Print the set ID being requested
        print(f"DEBUG: get_set_by_id called with set_id: '{set_id}'")
        
        if not self.user_hash:
            print("DEBUG: ⚠️ No user_hash available - API may reject request")
        
        params = {
            "apiKey": self.api_key,
            "setNumber": set_id,
            "pageSize": 1,
            "pageNumber": 1
        }
        
        # Add userHash if available
        if self.user_hash:
            params["userHash"] = self.user_hash
            print("DEBUG: ✅ Including userHash in request")
        else:
            print("DEBUG: ⚠️ No userHash available - API may reject request")
        
        payload = {"params": params}
        
        try:
            response = requests.post(self.GETSETS_URL, json=payload, timeout=30)
            print(f"DEBUG: get_set_by_id response status: {response.status_code}")
            
            # DEBUG: Print the raw API response for troubleshooting
            response_text = response.text
            print("DEBUG: Brickset API response text:", response_text[:500] + "..." if len(response_text) > 500 else response_text)
            
            response.raise_for_status()
            sets = response.json().get("sets", [])
            print(f"DEBUG: ✅ get_set_by_id found {len(sets)} sets")
            return sets[0] if sets else None
        except Exception as e:
            print(f"DEBUG: ❌ get_set_by_id request failed: {e}")
            return None

    def test_simple_query(self):
        """Test with a simple, guaranteed-to-work query"""
        print("DEBUG: Testing with simple query 'star'...")
        test_results = self.get_sets("star")
        print(f"DEBUG: Simple query test returned {len(test_results)} results")
        if test_results:
            print("DEBUG: ✅ API test successful - authentication working")
        else:
            print("DEBUG: ❌ API test failed - check credentials")
            if not self.user_hash:
                print("DEBUG: 💡 Try adding username/password to .env file")
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
        
        self.brickset = BricksetAPIv3(api_key=brickset_key, username=brickset_username, password=brickset_password)
        self.rebrickable = Rebrick(api_key=rebrickable_key)
        self.brickowl_key = brickowl_key
        
        # DEBUG: Test simple query on initialization
        if brickset_key:
            print("DEBUG: Running initial API test...")
            self.brickset.test_simple_query()
        else:
            print("DEBUG: Skipping API test - missing API key")

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