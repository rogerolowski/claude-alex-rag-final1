# SQLite and ChromaDB logic 
import sqlite3
from chromadb import Client
from chromadb.utils import embedding_functions
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
            
            # Initialize ChromaDB
            logger.debug("Initializing ChromaDB client...")
            self.chroma_client = Client()
            logger.debug("✅ ChromaDB client initialized")
            
            # Create or get collection
            logger.debug(f"Setting up ChromaDB collection: {collection_name}")
            try:
                self.collection = self.chroma_client.get_collection(name=collection_name)
                logger.debug(f"✅ Retrieved existing collection: {collection_name}")
            except Exception as e:
                logger.debug(f"Collection not found, creating new one: {e}")
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction()
                )
                logger.debug(f"✅ Created new collection: {collection_name}")
            
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
            
            # Store in ChromaDB for semantic search
            logger.debug("Storing in ChromaDB...")
            document_text = lego_set.description or lego_set.name
            logger.debug(f"Document text for embedding: {document_text[:100]}...")
            
            self.collection.add(
                documents=[document_text],
                metadatas=[lego_set.dict()],
                ids=[lego_set.set_id]
            )
            logger.debug("✅ Stored in ChromaDB successfully")
            
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
                            'set_id': row[0],
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

    def semantic_search(self, query: str, n_results=5) -> List[LegoSet]:
        """Perform semantic search using ChromaDB"""
        logger.debug(f"Performing semantic search: '{query}' with n_results={n_results}")
        start_time = time.time()
        
        try:
            results = self.collection.query(
                query_texts=[query], 
                n_results=n_results
            )
            
            logger.debug(f"ChromaDB returned {len(results['metadatas'][0])} results")
            
            # Convert metadata to LegoSet objects
            sets = []
            for i, metadata in enumerate(results["metadatas"][0]):
                try:
                    lego_set = LegoSet(**metadata)
                    sets.append(lego_set)
                    logger.debug(f"✅ Converted metadata to LegoSet: {lego_set.set_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to convert metadata to LegoSet: {e}")
                    logger.warning(f"Metadata: {metadata}")
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
            
            # ChromaDB stats
            try:
                chroma_count = self.collection.count()
            except Exception as e:
                logger.warning(f"Could not get ChromaDB count: {e}")
                chroma_count = "Unknown"
            
            stats = {
                "sqlite_sets": sqlite_count,
                "chromadb_sets": chroma_count,
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