# LangChain and OpenAI integration 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from data_layer import DataLayer
from api_layer import LegoAPI
from models import SearchResult
from dotenv import load_dotenv
import os
import logging
import time
import json

# Configure logging for AI layer
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

class AILayer:
    def __init__(self):
        logger.debug("Initializing AILayer...")
        
        try:
            # Initialize OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                logger.error("❌ OPENAI_API_KEY not found in environment variables")
                raise ValueError("OPENAI_API_KEY is required")
            
            logger.debug("Initializing OpenAI ChatOpenAI...")
            self.llm = ChatOpenAI(api_key=openai_key, model="gpt-4")
            logger.debug("✅ OpenAI ChatOpenAI initialized successfully")
            
            # Initialize data and API layers
            logger.debug("Initializing DataLayer...")
            self.data_layer = DataLayer()
            logger.debug("✅ DataLayer initialized")
            
            logger.debug("Initializing LegoAPI...")
            self.api_layer = LegoAPI()
            logger.debug("✅ LegoAPI initialized")
            
            # Initialize prompt template
            logger.debug("Setting up prompt template...")
            self.prompt = ChatPromptTemplate.from_template("""
                You are a LEGO expert assistant. Use the following context to answer the user's query:
                Structured Data: {structured_data}
                Semantic Search Results: {semantic_results}
                API Data: {api_data}
                User Query: {query}
                Provide a concise, informative response for LEGO collectors.
            """)
            logger.debug("✅ Prompt template initialized")
            
            logger.debug("✅ AILayer initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AILayer: {e}")
            raise

    def process_query(self, query: str) -> SearchResult:
        """Process a user query and return AI-generated response with LEGO sets"""
        logger.debug(f"Processing query: '{query}'")
        start_time = time.time()
        
        try:
            # Validate input
            if not query or not query.strip():
                logger.warning("⚠️ Empty query provided")
                return SearchResult(sets=[], ai_response="Please provide a search query.")
            
            query = query.strip()
            logger.debug(f"✅ Query validated: '{query}'")
            
            # Fetch data from different sources
            logger.debug("Fetching data from multiple sources...")
            
            # 1. SQLite structured data
            logger.debug("Querying SQLite for structured data...")
            sqlite_start = time.time()
            try:
                structured_data = self.data_layer.query_sqlite(
                    "SELECT * FROM lego_sets WHERE name LIKE ?", 
                    (f"%{query}%",)
                )
                sqlite_time = time.time() - sqlite_start
                logger.debug(f"✅ SQLite query completed in {sqlite_time:.2f}s, found {len(structured_data)} sets")
            except Exception as e:
                logger.error(f"❌ SQLite query failed: {e}")
                structured_data = []
            
            # 2. ChromaDB semantic search
            logger.debug("Performing semantic search...")
            semantic_start = time.time()
            try:
                semantic_results = self.data_layer.semantic_search(query)
                semantic_time = time.time() - semantic_start
                logger.debug(f"✅ Semantic search completed in {semantic_time:.2f}s, found {len(semantic_results)} sets")
            except Exception as e:
                logger.error(f"❌ Semantic search failed: {e}")
                semantic_results = []
            
            # 3. External API data
            logger.debug("Fetching external API data...")
            api_start = time.time()
            try:
                api_data = self.api_layer.search_sets(query)
                api_time = time.time() - api_start
                logger.debug(f"✅ API search completed in {api_time:.2f}s, found {len(api_data)} sets")
            except Exception as e:
                logger.error(f"❌ API search failed: {e}")
                api_data = []
            
            # Prepare context for AI
            logger.debug("Preparing context for AI...")
            context = {
                "structured_data": [s.dict() for s in structured_data],
                "semantic_results": [s.dict() for s in semantic_results],
                "api_data": [s.dict() for s in api_data],
                "query": query
            }
            
            logger.debug(f"Context prepared:")
            logger.debug(f"  - Structured data: {len(context['structured_data'])} sets")
            logger.debug(f"  - Semantic results: {len(context['structured_results'])} sets")
            logger.debug(f"  - API data: {len(context['api_data'])} sets")
            
            # Generate AI response
            logger.debug("Generating AI response...")
            ai_start = time.time()
            try:
                formatted_prompt = self.prompt.format(**context)
                logger.debug(f"Formatted prompt length: {len(formatted_prompt)} characters")
                
                response = self.llm.invoke(formatted_prompt)
                ai_time = time.time() - ai_start
                
                logger.debug(f"✅ AI response generated in {ai_time:.2f}s")
                logger.debug(f"Response length: {len(response.content)} characters")
                
            except Exception as e:
                logger.error(f"❌ AI response generation failed: {e}")
                response_content = f"I'm sorry, I encountered an error while processing your query about '{query}'. Please try again."
            else:
                response_content = response.content
            
            # Create SearchResult
            logger.debug("Creating SearchResult...")
            try:
                search_result = SearchResult(sets=api_data, ai_response=response_content)
                logger.debug(f"✅ SearchResult created successfully with {len(api_data)} sets")
            except Exception as e:
                logger.error(f"❌ Failed to create SearchResult: {e}")
                search_result = SearchResult(sets=[], ai_response="Error creating search result.")
            
            total_time = time.time() - start_time
            logger.debug(f"✅ Query processing completed in {total_time:.2f}s")
            
            return search_result
            
        except Exception as e:
            logger.error(f"❌ Query processing failed: {e}")
            logger.error(f"Query: {query}")
            return SearchResult(sets=[], ai_response=f"An error occurred while processing your query: {str(e)}")

    def test_ai_connection(self) -> bool:
        """Test the AI connection and return True if successful"""
        logger.debug("Testing AI connection...")
        
        try:
            test_prompt = "Hello, this is a test message. Please respond with 'Test successful'."
            response = self.llm.invoke(test_prompt)
            
            if response and response.content:
                logger.debug("✅ AI connection test successful")
                logger.debug(f"Test response: {response.content}")
                return True
            else:
                logger.warning("⚠️ AI connection test returned empty response")
                return False
                
        except Exception as e:
            logger.error(f"❌ AI connection test failed: {e}")
            return False

    def get_ai_stats(self) -> dict:
        """Get statistics about the AI layer"""
        logger.debug("Getting AI layer statistics...")
        
        try:
            # Test AI connection
            ai_connected = self.test_ai_connection()
            
            # Get database stats
            db_stats = self.data_layer.get_database_stats()
            
            stats = {
                "ai_connected": ai_connected,
                "database_stats": db_stats,
                "model": "gpt-4",
                "prompt_template_length": len(str(self.prompt))
            }
            
            logger.debug(f"✅ AI layer stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get AI layer stats: {e}")
            return {"error": str(e)}

    def cleanup(self):
        """Clean up AI layer resources"""
        logger.debug("Cleaning up AILayer...")
        try:
            if hasattr(self, 'data_layer'):
                self.data_layer.cleanup()
                logger.debug("✅ DataLayer cleaned up")
        except Exception as e:
            logger.error(f"❌ Error during AILayer cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()