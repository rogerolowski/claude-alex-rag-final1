# LangChain and OpenAI integration 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from data_layer import DataLayer
from api_layer import LegoAPI
from models import SearchResult
from dotenv import load_dotenv
import os

load_dotenv()

class AILayer:
    def __init__(self):
        self.llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4")
        self.data_layer = DataLayer()
        self.api_layer = LegoAPI()
        self.prompt = ChatPromptTemplate.from_template("""
            You are a LEGO expert assistant. Use the following context to answer the user's query:
            Structured Data: {structured_data}
            Semantic Search Results: {semantic_results}
            API Data: {api_data}
            User Query: {query}
            Provide a concise, informative response for LEGO collectors.
        """)

    def process_query(self, query: str) -> SearchResult:
        # Fetch data
        structured_data = self.data_layer.query_sqlite("SELECT * FROM lego_sets WHERE name LIKE ?", (f"%{query}%",))
        semantic_results = self.data_layer.semantic_search(query)
        api_data = self.api_layer.search_sets(query)

        # Combine context
        context = {
            "structured_data": [s.dict() for s in structured_data],
            "semantic_results": [s.dict() for s in semantic_results],
            "api_data": [s.dict() for s in api_data],
            "query": query
        }

        # Generate AI response
        response = self.llm.invoke(self.prompt.format(**context)).content

        return SearchResult(sets=api_data, ai_response=response)