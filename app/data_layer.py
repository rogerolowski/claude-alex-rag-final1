# SQLite and LangChain Chroma logic 
import sqlite3
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from models import LegoSet
import logging
import time
import os
from typing import List, Optional

# Configure logging for data layer
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DataLayer:
    def __init__(self, db_path="lego.db", collection_name="lego_sets"):
        logger.debug(f"Initializing DataLayer with db_path: {db_path}, collection_name: {collection_name}")
        
        try:
            # Initialize SQLite
            logger.debug("Connecting to SQLite database...")
            self.conn = sqlite3.connect(db_path)
            logger.debug(f"✅ SQLite connection established: {db_path}")
            
            # Initialize LangChain Chroma with HuggingFace embeddings
            logger.debug("Initializing LangChain Chroma with HuggingFace embeddings...")
            self.embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            logger.debug("✅ HuggingFace embeddings initialized")
            
            # Create or get Chroma vectorstore
            logger.debug(f"Setting up Chroma vectorstore: {collection_name}")
            persist_directory = f"./chroma_db_{collection_name}"
            self.vectorstore = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embedding_function,
                collection_name=collection_name
            )
            logger.debug(f"✅ Chroma vectorstore initialized: {persist_directory}")
            
            # Create database table
            self.create_table()
            logger.debug("✅ DataLayer initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize DataLayer: {e}")
            raise

    def create_table(self):
        """Create the SQLite table for storing LEGO sets"""
        logger.debug("Creating SQLite table...")
        try:
            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS lego_sets (
                        set_id TEXT PRIMARY KEY,
                        name TEXT,
                        theme TEXT,
                        piece_count INTEGER,
                        price REAL,
                        release_year INTEGER,
                        description TEXT
                    )
                """)
            logger.debug("✅ SQLite table created/verified successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create table: {e}")
            raise

    def store_set(self, lego_set: LegoSet):
        """Store a LEGO set in both SQLite and ChromaDB"""
        logger.debug(f"Storing LEGO set: {lego_set.set_id} - {lego_set.name}")
        start_time = time.time()
        
        try:
            # Store in SQLite
            logger.debug("Storing in SQLite...")
            with self.conn:
                self.conn.execute("""
                    INSERT OR REPLACE INTO lego_sets (set_id, name, theme, piece_count, price, release_year, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    lego_set.set_id, lego_set.name, lego_set.theme, lego_set.piece_count,
                    lego_set.price, lego_set.release_year, lego_set.description
                ))
            logger.debug("✅ Stored in SQLite successfully")
            
            # Store in LangChain Chroma for semantic search
            logger.debug("Storing in LangChain Chroma...")
            document_text = lego_set.description or lego_set.name
            logger.debug(f"Document text for embedding: {document_text[:100]}...")
            
            # Add document to vectorstore
            self.vectorstore.add_documents(
                documents=[document_text],
                metadatas=[lego_set.dict()],
                ids=[lego_set.set_id]
            )
            logger.debug("✅ Stored in LangChain Chroma successfully")
            
            elapsed_time = time.time() - start_time
            logger.debug(f"✅ Set stored successfully in {elapsed_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to store set {lego_set.set_id}: {e}")
            raise

    def query_sqlite(self, query: str, params=()) -> List[LegoSet]:
        """Query SQLite database and return LEGO sets"""
        logger.debug(f"Querying SQLite: {query} with params: {params}")
        start_time = time.time()
        
        try:
            with self.conn:
                cursor = self.conn.execute(query, params)
                rows = cursor.fetchall()
                logger.debug(f"Found {len(rows)} rows in SQLite")
                
                # Convert rows to LegoSet objects
                sets = []
                for row in rows:
                    try:
                        # Convert row to dict
                        row_dict = {
                            'set_id': str(row[0]) if row[0] is not None else "",  # Ensure set_id is string
                            'name': row[1],
                            'theme': row[2],
                            'piece_count': row[3],
                            'price': row[4],
                            'release_year': row[5],
                            'description': row[6]
                        }
                        lego_set = LegoSet(**row_dict)
                        sets.append(lego_set)
                        logger.debug(f"✅ Converted row to LegoSet: {lego_set.set_id}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to convert row to LegoSet: {e}")
                        logger.warning(f"Row data: {row}")
                        continue
                
                elapsed_time = time.time() - start_time
                logger.debug(f"✅ SQLite query completed in {elapsed_time:.2f}s, returned {len(sets)} sets")
                return sets
                
        except Exception as e:
            logger.error(f"❌ SQLite query failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise

    def search_by_theme(self, theme: str, limit: int = 10) -> List[LegoSet]:
        """Search for sets by theme"""
        logger.debug(f"Searching by theme: {theme}")
        query = """
            SELECT * FROM lego_sets 
            WHERE theme LIKE ? 
            ORDER BY release_year DESC 
            LIMIT ?
        """
        return self.query_sqlite(query, (f"%{theme}%", limit))

    def get_oldest_set_by_theme(self, theme: str) -> Optional[LegoSet]:
        """Get the oldest set for a specific theme"""
        logger.debug(f"Getting oldest set for theme: {theme}")
        query = """
            SELECT * FROM lego_sets 
            WHERE theme LIKE ? AND release_year IS NOT NULL
            ORDER BY release_year ASC 
            LIMIT 1
        """
        results = self.query_sqlite(query, (f"%{theme}%",))
        return results[0] if results else None

    def get_newest_set_by_theme(self, theme: str) -> Optional[LegoSet]:
        """Get the newest set for a specific theme"""
        logger.debug(f"Getting newest set for theme: {theme}")
        query = """
            SELECT * FROM lego_sets 
            WHERE theme LIKE ? AND release_year IS NOT NULL
            ORDER BY release_year DESC 
            LIMIT 1
        """
        results = self.query_sqlite(query, (f"%{theme}%",))
        return results[0] if results else None

    def get_largest_set_by_theme(self, theme: str) -> Optional[LegoSet]:
        """Get the largest set (by piece count) for a specific theme"""
        logger.debug(f"Getting largest set for theme: {theme}")
        query = """
            SELECT * FROM lego_sets 
            WHERE theme LIKE ? AND piece_count IS NOT NULL
            ORDER BY piece_count DESC 
            LIMIT 1
        """
        results = self.query_sqlite(query, (f"%{theme}%",))
        return results[0] if results else None

    def get_smallest_set_by_theme(self, theme: str) -> Optional[LegoSet]:
        """Get the smallest set (by piece count) for a specific theme"""
        logger.debug(f"Getting smallest set for theme: {theme}")
        query = """
            SELECT * FROM lego_sets 
            WHERE theme LIKE ? AND piece_count IS NOT NULL
            ORDER BY piece_count ASC 
            LIMIT 1
        """
        results = self.query_sqlite(query, (f"%{theme}%",))
        return results[0] if results else None

    def search_by_year(self, year: int, limit: int = 10) -> List[LegoSet]:
        """Search for sets by release year"""
        logger.debug(f"Searching by year: {year}")
        query = """
            SELECT * FROM lego_sets 
            WHERE release_year = ? 
            ORDER BY piece_count DESC 
            LIMIT ?
        """
        return self.query_sqlite(query, (year, limit))

    def search_by_set_number(self, set_number: str) -> Optional[LegoSet]:
        """Search for a specific set by set number"""
        logger.debug(f"Searching by set number: {set_number}")
        query = """
            SELECT * FROM lego_sets 
            WHERE set_id = ? 
            LIMIT 1
        """
        results = self.query_sqlite(query, (set_number,))
        return results[0] if results else None

    def semantic_search(self, query: str, n_results=5) -> List[LegoSet]:
        """Perform semantic search using LangChain Chroma"""
        logger.debug(f"Performing semantic search: '{query}' with n_results={n_results}")
        start_time = time.time()
        
        try:
            # Use LangChain Chroma similarity search
            docs = self.vectorstore.similarity_search(query, k=n_results)
            
            logger.debug(f"LangChain Chroma returned {len(docs)} results")
            
            # Convert documents to LegoSet objects
            sets = []
            for doc in docs:
                try:
                    metadata = doc.metadata
                    # Ensure set_id is string in metadata
                    if 'set_id' in metadata and metadata['set_id'] is not None:
                        metadata['set_id'] = str(metadata['set_id'])
                    
                    lego_set = LegoSet(**metadata)
                    sets.append(lego_set)
                    logger.debug(f"✅ Converted document to LegoSet: {lego_set.set_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to convert document to LegoSet: {e}")
                    logger.warning(f"Document metadata: {doc.metadata}")
                    continue
            
            elapsed_time = time.time() - start_time
            logger.debug(f"✅ Semantic search completed in {elapsed_time:.2f}s, returned {len(sets)} sets")
            return sets
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            logger.error(f"Query: {query}")
            raise

    def get_database_stats(self) -> dict:
        """Get statistics about the database"""
        logger.debug("Getting database statistics...")
        
        try:
            # SQLite stats
            with self.conn:
                cursor = self.conn.execute("SELECT COUNT(*) FROM lego_sets")
                sqlite_count = cursor.fetchone()[0]
                
                cursor = self.conn.execute("SELECT COUNT(*) FROM lego_sets WHERE price IS NOT NULL")
                priced_count = cursor.fetchone()[0]
                
                cursor = self.conn.execute("SELECT COUNT(*) FROM lego_sets WHERE release_year IS NOT NULL")
                year_count = cursor.fetchone()[0]
            
            # LangChain Chroma stats
            try:
                chroma_count = len(self.vectorstore.get())
            except Exception as e:
                logger.warning(f"Could not get LangChain Chroma count: {e}")
                chroma_count = "Unknown"
            
            stats = {
                "sqlite_sets": sqlite_count,
                "chroma_sets": chroma_count,
                "priced_sets": priced_count,
                "sets_with_year": year_count
            }
            
            logger.debug(f"✅ Database stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return {"error": str(e)}

    def cleanup(self):
        """Clean up database connections"""
        logger.debug("Cleaning up DataLayer...")
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
                logger.debug("✅ SQLite connection closed")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()