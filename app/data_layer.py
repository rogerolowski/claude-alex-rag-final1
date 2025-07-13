# SQLite and ChromaDB logic 
import sqlite3
from chromadb import Client
from chromadb.utils import embedding_functions
from models import LegoSet

class DataLayer:
    def __init__(self, db_path="lego.db", collection_name="lego_sets"):
        self.conn = sqlite3.connect(db_path)
        self.chroma_client = Client()
        self.collection = self.chroma_client.create_collection(
            name=collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction()
        )
        self.create_table()

    def create_table(self):
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

    def store_set(self, lego_set: LegoSet):
        # Store in SQLite
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO lego_sets (set_id, name, theme, piece_count, price, release_year, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                lego_set.set_id, lego_set.name, lego_set.theme, lego_set.piece_count,
                lego_set.price, lego_set.release_year, lego_set.description
            ))
        # Store in ChromaDB for semantic search
        self.collection.add(
            documents=[lego_set.description or lego_set.name],
            metadatas=[lego_set.dict()],
            ids=[lego_set.set_id]
        )

    def query_sqlite(self, query: str, params=()):
        with self.conn:
            cursor = self.conn.execute(query, params)
            return [LegoSet(**row) for row in cursor.fetchall()]

    def semantic_search(self, query: str, n_results=5):
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return [LegoSet(**meta) for meta in results["metadatas"][0]]