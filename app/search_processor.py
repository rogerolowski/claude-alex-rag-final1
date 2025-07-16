#!/usr/bin/env python3
"""
Smart Search Processor for LEGO AI Assistant
Handles natural language queries, fuzzy matching, and semantic search
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from rapidfuzz import process, fuzz
from models import LegoSet

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SmartSearchProcessor:
    """Processes natural language queries and converts them to searchable terms"""
    
    def __init__(self):
        # Common LEGO themes and their variations
        self.theme_mappings = {
            'star wars': ['star wars', 'starwars', 'sw', 'starwar'],
            'city': ['city', 'lego city', 'town'],
            'technic': ['technic', 'technical'],
            'friends': ['friends', 'lego friends'],
            'ninjago': ['ninjago', 'ninja go', 'ninja'],
            'architecture': ['architecture', 'architectural'],
            'creator': ['creator', 'creative'],
            'duplo': ['duplo', 'duplo blocks'],
            'bionicle': ['bionicle', 'bionicles'],
            'marvel': ['marvel', 'superheroes', 'avengers'],
            'dc': ['dc', 'batman', 'superman'],
            'harry potter': ['harry potter', 'hp', 'wizarding world'],
            'minecraft': ['minecraft', 'mine craft'],
            'jurassic world': ['jurassic world', 'jurassic park', 'dinosaurs'],
            'speed champions': ['speed champions', 'cars', 'racing'],
            'ideas': ['ideas', 'lego ideas', 'fan designed'],
            'expert': ['expert', 'expert level', 'adult'],
            'classic': ['classic', 'basic', 'traditional']
        }
        
        # Time-related keywords
        self.time_keywords = {
            'oldest': ['oldest', 'first', 'earliest', 'original'],
            'newest': ['newest', 'latest', 'recent', 'current'],
            'vintage': ['vintage', 'retro', 'classic', 'old'],
            'modern': ['modern', 'new', 'contemporary', 'recent']
        }
        
        # Size-related keywords
        self.size_keywords = {
            'largest': ['largest', 'biggest', 'huge', 'massive'],
            'smallest': ['smallest', 'tiny', 'mini', 'small'],
            'medium': ['medium', 'average', 'normal']
        }
        
        # Price-related keywords
        self.price_keywords = {
            'expensive': ['expensive', 'costly', 'premium', 'high price'],
            'cheap': ['cheap', 'inexpensive', 'affordable', 'low price'],
            'free': ['free', 'no cost', 'zero price']
        }

    def extract_theme(self, query: str) -> Optional[str]:
        """Extract theme from query using fuzzy matching"""
        query_lower = query.lower()
        
        for theme, variations in self.theme_mappings.items():
            for variation in variations:
                if variation in query_lower:
                    logger.debug(f"Found theme: {theme}")
                    return theme
        
        # Try fuzzy matching for themes
        all_themes = list(self.theme_mappings.keys())
        best_match = process.extractOne(query_lower, all_themes, scorer=fuzz.partial_ratio)
        
        if best_match and best_match[1] > 70:  # 70% similarity threshold
            logger.debug(f"Fuzzy matched theme: {best_match[0]} (score: {best_match[1]})")
            return best_match[0]
        
        return None

    def extract_time_modifier(self, query: str) -> Optional[str]:
        """Extract time-related modifiers from query"""
        query_lower = query.lower()
        
        for modifier, keywords in self.time_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    logger.debug(f"Found time modifier: {modifier}")
                    return modifier
        
        return None

    def extract_size_modifier(self, query: str) -> Optional[str]:
        """Extract size-related modifiers from query"""
        query_lower = query.lower()
        
        for modifier, keywords in self.size_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    logger.debug(f"Found size modifier: {modifier}")
                    return modifier
        
        return None

    def extract_price_modifier(self, query: str) -> Optional[str]:
        """Extract price-related modifiers from query"""
        query_lower = query.lower()
        
        for modifier, keywords in self.price_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    logger.debug(f"Found price modifier: {modifier}")
                    return modifier
        
        return None

    def extract_year(self, query: str) -> Optional[int]:
        """Extract year from query"""
        # Look for 4-digit years
        year_pattern = r'\b(19|20)\d{2}\b'
        matches = re.findall(year_pattern, query)
        
        if matches:
            year = int(matches[0])
            logger.debug(f"Found year: {year}")
            return year
        
        return None

    def extract_set_number(self, query: str) -> Optional[str]:
        """Extract set number from query"""
        # Look for patterns like "set 12345" or "12345"
        set_pattern = r'\b(\d{3,6})\b'
        matches = re.findall(set_pattern, query)
        
        if matches:
            set_number = matches[0]
            logger.debug(f"Found set number: {set_number}")
            return set_number
        
        return None

    def process_query(self, query: str) -> Dict:
        """Process natural language query and extract search parameters"""
        logger.debug(f"Processing query: '{query}'")
        
        result = {
            'original_query': query,
            'theme': self.extract_theme(query),
            'time_modifier': self.extract_time_modifier(query),
            'size_modifier': self.extract_size_modifier(query),
            'price_modifier': self.extract_price_modifier(query),
            'year': self.extract_year(query),
            'set_number': self.extract_set_number(query),
            'keywords': self.extract_keywords(query)
        }
        
        logger.debug(f"Processed query result: {result}")
        return result

    def extract_keywords(self, query: str) -> List[str]:
        """Extract general keywords from query"""
        # Remove common words and extract meaningful keywords
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'set', 'sets', 'lego'}
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        logger.debug(f"Extracted keywords: {keywords}")
        return keywords

    def generate_search_queries(self, processed_query: Dict) -> List[str]:
        """Generate multiple search queries based on processed query"""
        queries = []
        
        # Original query
        queries.append(processed_query['original_query'])
        
        # Theme-based queries
        if processed_query['theme']:
            queries.append(processed_query['theme'])
            if processed_query['time_modifier']:
                queries.append(f"{processed_query['time_modifier']} {processed_query['theme']}")
        
        # Set number query
        if processed_query['set_number']:
            queries.append(processed_query['set_number'])
        
        # Keyword-based queries
        if processed_query['keywords']:
            queries.extend(processed_query['keywords'])
        
        # Remove duplicates and empty queries
        queries = list(set([q.strip() for q in queries if q.strip()]))
        
        logger.debug(f"Generated search queries: {queries}")
        return queries

    def rank_results(self, results: List[LegoSet], processed_query: Dict) -> List[LegoSet]:
        """Rank results based on query relevance"""
        if not results:
            return results
        
        scored_results = []
        
        for lego_set in results:
            score = 0
            
            # Theme matching
            if processed_query['theme'] and processed_query['theme'].lower() in lego_set.theme.lower():
                score += 10
            
            # Year matching for time modifiers
            if processed_query['time_modifier'] and lego_set.release_year:
                if processed_query['time_modifier'] == 'oldest' and lego_set.release_year < 2000:
                    score += 5
                elif processed_query['time_modifier'] == 'newest' and lego_set.release_year > 2010:
                    score += 5
            
            # Size matching
            if processed_query['size_modifier'] and lego_set.piece_count:
                if processed_query['size_modifier'] == 'largest' and lego_set.piece_count > 1000:
                    score += 3
                elif processed_query['size_modifier'] == 'smallest' and lego_set.piece_count < 100:
                    score += 3
            
            # Price matching
            if processed_query['price_modifier'] and lego_set.price:
                if processed_query['price_modifier'] == 'expensive' and lego_set.price > 100:
                    score += 3
                elif processed_query['price_modifier'] == 'cheap' and lego_set.price < 50:
                    score += 3
            
            # Keyword matching in name and description
            for keyword in processed_query['keywords']:
                if keyword.lower() in lego_set.name.lower():
                    score += 2
                if lego_set.description and keyword.lower() in lego_set.description.lower():
                    score += 1
            
            scored_results.append((lego_set, score))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the sets
        ranked_results = [set_obj for set_obj, score in scored_results]
        
        logger.debug(f"Ranked {len(ranked_results)} results")
        return ranked_results

def create_search_processor() -> SmartSearchProcessor:
    """Create and return a search processor instance"""
    return SmartSearchProcessor() 