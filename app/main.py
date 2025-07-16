# Streamlit app and main entry point 
import streamlit as st
from ai_layer import AILayer  # If you use AI features
from api_layer import LegoAPI
import logging
import time
import traceback
from typing import Optional

# Configure logging for main app
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize session state for debugging
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False
if 'app_start_time' not in st.session_state:
    st.session_state.app_start_time = time.time()

def initialize_app():
    """Initialize the application and its components"""
    logger.debug("Initializing LEGO AI Assistant application...")
    start_time = time.time()
    
    try:
        # Initialize API layer
        logger.debug("Initializing LegoAPI...")
        lego_api = LegoAPI()
        logger.debug("✅ LegoAPI initialized successfully")
        
        # Initialize AI layer (optional)
        ai_layer = None
        try:
            logger.debug("Initializing AILayer...")
            ai_layer = AILayer()
            logger.debug("✅ AILayer initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ AILayer initialization failed: {e}")
            logger.warning("AI features will be disabled")
        
        init_time = time.time() - start_time
        logger.debug(f"✅ Application initialization completed in {init_time:.2f}s")
        
        return lego_api, ai_layer
        
    except Exception as e:
        logger.error(f"❌ Application initialization failed: {e}")
        logger.error(traceback.format_exc())
        st.error(f"Failed to initialize application: {str(e)}")
        return None, None

def display_debug_info(lego_api: Optional[LegoAPI], ai_layer: Optional[AILayer]):
    """Display debug information in the sidebar"""
    if st.session_state.debug_mode:
        st.sidebar.header("🔧 Debug Information")
        
        # App stats
        uptime = time.time() - st.session_state.app_start_time
        st.sidebar.write(f"**Uptime:** {uptime:.1f}s")
        
        # API stats
        if lego_api:
            try:
                st.sidebar.write("**API Status:** ✅ Connected")
            except Exception as e:
                st.sidebar.write(f"**API Status:** ❌ Error - {str(e)}")
        
        # AI stats
        if ai_layer:
            try:
                ai_stats = ai_layer.get_ai_stats()
                st.sidebar.write(f"**AI Status:** {'✅ Connected' if ai_stats.get('ai_connected') else '❌ Disconnected'}")
            except Exception as e:
                st.sidebar.write(f"**AI Status:** ❌ Error - {str(e)}")

def handle_search(lego_api: LegoAPI, query: str):
    """Handle search functionality with comprehensive error handling"""
    logger.debug(f"Handling search for query: '{query}'")
    start_time = time.time()
    
    try:
        # Validate query
        if not query or not query.strip():
            logger.warning("Empty search query provided")
            st.warning("Please enter a search term.")
            return None
        
        query = query.strip()
        logger.debug(f"✅ Query validated: '{query}'")
        
        # Perform search
        logger.debug("Performing search...")
        with st.spinner("Searching for LEGO sets..."):
            results = lego_api.search_sets(query)
        
        search_time = time.time() - start_time
        logger.debug(f"✅ Search completed in {search_time:.2f}s, found {len(results)} results")
        
        return results
        
    except Exception as e:
        search_time = time.time() - start_time
        logger.error(f"❌ Search failed after {search_time:.2f}s: {e}")
        logger.error(traceback.format_exc())
        st.error(f"An error occurred during search: {str(e)}")
        return None

def handle_set_details(lego_api: LegoAPI, set_id: str):
    """Handle fetching detailed set information"""
    logger.debug(f"Fetching details for set: {set_id}")
    start_time = time.time()
    
    try:
        with st.spinner("Fetching set details..."):
            full_set = lego_api.fetch_set(set_id)
        
        fetch_time = time.time() - start_time
        logger.debug(f"✅ Set details fetched in {fetch_time:.2f}s")
        
        return full_set
        
    except Exception as e:
        fetch_time = time.time() - start_time
        logger.error(f"❌ Failed to fetch set details after {fetch_time:.2f}s: {e}")
        logger.error(traceback.format_exc())
        st.error(f"Failed to fetch set details: {str(e)}")
        return None

def main():
    """Main application function"""
    logger.debug("Starting LEGO AI Assistant application...")
    
    # Page configuration
    st.set_page_config(
        page_title="LEGO AI Assistant",
        page_icon="🧱",
        layout="wide"
    )
    
    # Initialize components
    lego_api, ai_layer = initialize_app()
    
    if not lego_api:
        st.error("Failed to initialize the application. Please check your configuration.")
        return
    
    # Main UI
    st.title("🧱 LEGO AI Assistant")
    
    # Debug toggle in sidebar
    st.sidebar.header("Settings")
    st.session_state.debug_mode = st.sidebar.checkbox("Debug Mode", value=st.session_state.debug_mode)
    
    # Display debug info
    display_debug_info(lego_api, ai_layer)
    
    # Search interface
    st.header("Search LEGO Sets")
    
    # Search input
    query = st.text_input("Search for a LEGO set:", placeholder="e.g., star wars, millennium falcon, technic")
    
    if query:
        logger.debug(f"User searched for: '{query}'")
        
        # Perform search
        results = handle_search(lego_api, query)
        
        if results and len(results) > 0:
            logger.debug(f"Displaying {len(results)} search results")
            
            # Show results as a selectable list
            set_names = [f"{s.set_id}: {s.name} ({s.theme})" for s in results]
            selected = st.selectbox("Select a set to view details:", set_names)
            selected_set = results[set_names.index(selected)]
            
            logger.debug(f"User selected set: {selected_set.set_id}")
            
            # Use expander for details
            with st.expander("Show full details and price"):
                if st.button("Fetch details for selected set"):
                    logger.debug(f"User requested details for set: {selected_set.set_id}")
                    
                    full_set = handle_set_details(lego_api, selected_set.set_id)
                    
                    if full_set:
                        logger.debug("Displaying set details")
                        
                        # Display set information
                        st.subheader(full_set.name)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Set ID:** {full_set.set_id}")
                            st.write(f"**Theme:** {full_set.theme}")
                            st.write(f"**Pieces:** {full_set.piece_count}")
                        
                        with col2:
                            st.write(f"**Year:** {full_set.release_year or 'N/A'}")
                            st.write(f"**Price:** {full_set.price or 'N/A'}")
                        
                        if full_set.description:
                            st.write(f"**Description:** {full_set.description}")
                        
                        logger.debug("✅ Set details displayed successfully")
                    else:
                        logger.warning("Failed to display set details")
        else:
            logger.debug("No search results found")
            st.info("No sets found for your search.")
            
            # Show helpful suggestions
            st.write("**Try searching for:**")
            st.write("- Popular themes: 'Star Wars', 'City', 'Technic'")
            st.write("- Set names: 'Millennium Falcon', 'Police Station'")
            st.write("- Set numbers: '75192', '10278'")
    else:
        st.info("Enter a search term to find LEGO sets.")
        
        # Show example searches
        st.write("**Example searches:**")
        st.write("- 'star wars' - Find Star Wars sets")
        st.write("- 'technic' - Find Technic sets")
        st.write("- 'millennium falcon' - Find specific sets")
    
    # Footer with debug info
    if st.session_state.debug_mode:
        st.sidebar.header("📊 Performance")
        uptime = time.time() - st.session_state.app_start_time
        st.sidebar.write(f"**App Uptime:** {uptime:.1f}s")
        
        # Memory usage (if available)
        try:
            import psutil
            memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            st.sidebar.write(f"**Memory Usage:** {memory:.1f} MB")
        except ImportError:
            pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Application crashed: {e}")
        logger.error(traceback.format_exc())
        st.error(f"Application crashed: {str(e)}")
        st.error("Please check the logs for more details.")