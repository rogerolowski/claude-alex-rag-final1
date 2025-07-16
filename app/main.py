# Streamlit app and main entry point 
import streamlit as st
from ai_layer import AILayer  # If you use AI features
from api_layer import LegoAPI
from search_processor import create_search_processor
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
        
        # Initialize search processor
        logger.debug("Initializing SmartSearchProcessor...")
        search_processor = create_search_processor()
        logger.debug("✅ SmartSearchProcessor initialized successfully")
        
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
        
        return lego_api, search_processor, ai_layer
        
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

def handle_search(lego_api: LegoAPI, search_processor, query: str):
    """Handle search functionality with smart processing and comprehensive error handling"""
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
        
        # Process query with smart search processor
        logger.debug("Processing query with smart search processor...")
        processed_query = search_processor.process_query(query)
        
        # Generate multiple search queries
        search_queries = search_processor.generate_search_queries(processed_query)
        logger.debug(f"Generated search queries: {search_queries}")
        
        # Try each search query until we find results
        all_results = []
        for search_query in search_queries:
            logger.debug(f"Trying search query: '{search_query}'")
            with st.spinner(f"Searching for '{search_query}'..."):
                results = lego_api.search_sets(search_query)
                if results:
                    all_results.extend(results)
                    logger.debug(f"Found {len(results)} results for '{search_query}'")
        
        # Remove duplicates and rank results
        unique_results = list({result.set_id: result for result in all_results}.values())
        ranked_results = search_processor.rank_results(unique_results, processed_query)
        
        search_time = time.time() - start_time
        logger.debug(f"✅ Smart search completed in {search_time:.2f}s, found {len(ranked_results)} unique results")
        
        return ranked_results
        
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
    lego_api, search_processor, ai_layer = initialize_app()
    
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
    
    # AI-Powered LEGO Assistant Interface
    st.header("🤖 AI LEGO Expert Assistant")
    
    # Search input with examples
    st.markdown("""
    **Ask me anything about LEGO! Try these example queries:**
    - `Tell me about the oldest Star Wars sets`
    - `What are the largest Technic sets ever made?`
    - `Give me information about Millennium Falcon sets`
    - `What should I know about LEGO City police stations?`
    - `Tell me about rare LEGO sets from the 1990s`
    - `What are the most expensive LEGO sets?`
    """)
    
    query = st.text_input("Ask about LEGO sets:", placeholder="e.g., Tell me about Star Wars LEGO sets, What are the largest Technic sets?")
    
    if query:
        logger.debug(f"User asked: '{query}'")
        
        # Use AI layer to get comprehensive response
        if ai_layer:
            with st.spinner("🤖 AI is analyzing your query and gathering information..."):
                try:
                    search_result = ai_layer.process_query(query)
                    
                    if search_result and search_result.ai_response:
                        # Display AI response prominently
                        st.markdown("## 🧠 AI Response")
                        st.markdown(search_result.ai_response)
                        
                        # Show related sets if available
                        if search_result.sets and len(search_result.sets) > 0:
                            st.markdown("## 📦 Related LEGO Sets")
                            
                            # Display sets in a nice format
                            for i, lego_set in enumerate(search_result.sets[:5]):  # Show top 5
                                with st.expander(f"**{lego_set.name}** ({lego_set.theme})"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Set ID:** {lego_set.set_id}")
                                        st.write(f"**Theme:** {lego_set.theme}")
                                        st.write(f"**Pieces:** {lego_set.piece_count}")
                                    with col2:
                                        st.write(f"**Year:** {lego_set.release_year or 'N/A'}")
                                        st.write(f"**Price:** {lego_set.price or 'N/A'}")
                                    
                                    if lego_set.description:
                                        st.write(f"**Description:** {lego_set.description}")
                                    
                                    # Button to get full details
                                    if st.button(f"Get full details for {lego_set.set_id}", key=f"details_{i}"):
                                        full_set = handle_set_details(lego_api, lego_set.set_id)
                                        if full_set:
                                            st.success(f"✅ Full details loaded for {full_set.name}")
                        
                        logger.debug("✅ AI response displayed successfully")
                    else:
                        st.warning("No AI response generated. Please try a different query.")
                        
                except Exception as e:
                    logger.error(f"❌ AI processing failed: {e}")
                    st.error(f"Sorry, I encountered an error while processing your query: {str(e)}")
        else:
            st.error("AI layer is not available. Please check your OpenAI API key configuration.")
            
            # Fallback to regular search
            st.info("Falling back to regular search...")
            results = handle_search(lego_api, search_processor, query)
            
            if results and len(results) > 0:
                st.write(f"Found {len(results)} sets:")
                for set_obj in results[:5]:
                    st.write(f"- {set_obj.name} ({set_obj.theme}) - {set_obj.piece_count} pieces")
            else:
                st.info("No sets found for your query.")
    else:
        st.info("👋 Ask me anything about LEGO sets, themes, history, or collecting!")
        
        # Show example queries
        st.markdown("**Example questions:**")
        st.markdown("- *What are the most popular LEGO themes?*")
        st.markdown("- *Tell me about rare LEGO sets*")
        st.markdown("- *What should I know about Technic sets?*")
        st.markdown("- *Give me information about Star Wars LEGO*")
        st.markdown("- *What are the largest LEGO sets ever made?*")
    
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