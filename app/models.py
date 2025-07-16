# Pydantic models for data validation 
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import logging

# Configure logging for models
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LegoSet(BaseModel):
    set_id: str = Field(..., description="Unique identifier for the LEGO set")
    name: str = Field(..., description="Name of the LEGO set")
    theme: str = Field(..., description="Theme of the LEGO set")
    piece_count: int = Field(..., ge=0, description="Number of pieces in the set")
    price: Optional[float] = Field(None, ge=0, description="Price of the set")
    release_year: Optional[int] = Field(None, ge=1950, le=2030, description="Year the set was released")
    description: Optional[str] = Field(None, description="Description of the set")

    @validator('set_id')
    def validate_set_id(cls, v):
        logger.debug(f"Validating set_id: {v} (type: {type(v)})")
        # Convert integer to string if needed
        if isinstance(v, int):
            v = str(v)
            logger.debug(f"Converted integer set_id to string: {v}")
        
        if not v or not str(v).strip():
            logger.warning(f"Empty set_id provided: {v}")
            raise ValueError("set_id cannot be empty")
        return str(v).strip()

    @validator('name')
    def validate_name(cls, v):
        logger.debug(f"Validating name: {v}")
        if not v or not v.strip():
            logger.warning(f"Empty name provided: {v}")
            raise ValueError("name cannot be empty")
        return v.strip()

    @validator('theme')
    def validate_theme(cls, v):
        logger.debug(f"Validating theme: {v}")
        if not v or not v.strip():
            logger.warning(f"Empty theme provided: {v}")
            raise ValueError("theme cannot be empty")
        return v.strip()

    @validator('piece_count')
    def validate_piece_count(cls, v):
        logger.debug(f"Validating piece_count: {v}")
        if v < 0:
            logger.warning(f"Invalid piece_count: {v}")
            raise ValueError("piece_count must be non-negative")
        return v

    @validator('price')
    def validate_price(cls, v):
        if v is not None:
            logger.debug(f"Validating price: {v}")
            if v < 0:
                logger.warning(f"Invalid price: {v}")
                raise ValueError("price must be non-negative")
        return v

    @validator('release_year')
    def validate_release_year(cls, v):
        if v is not None:
            logger.debug(f"Validating release_year: {v}")
            if v < 1950 or v > 2030:
                logger.warning(f"Invalid release_year: {v}")
                raise ValueError("release_year must be between 1950 and 2030")
        return v

    def __init__(self, **data):
        logger.debug(f"Creating LegoSet with data: {data}")
        try:
            super().__init__(**data)
            logger.debug(f"✅ LegoSet created successfully: {self.set_id} - {self.name}")
        except Exception as e:
            logger.error(f"❌ Failed to create LegoSet: {e}")
            logger.error(f"Data provided: {data}")
            raise

    def dict(self, *args, **kwargs):
        logger.debug(f"Converting LegoSet to dict: {self.set_id}")
        return super().dict(*args, **kwargs)

class SearchResult(BaseModel):
    sets: List[LegoSet] = Field(..., description="List of LEGO sets found")
    ai_response: Optional[str] = Field(None, description="AI-generated response")

    @validator('sets')
    def validate_sets(cls, v):
        logger.debug(f"Validating sets list: {len(v)} sets")
        if not isinstance(v, list):
            logger.warning(f"Sets must be a list, got: {type(v)}")
            raise ValueError("sets must be a list")
        return v

    def __init__(self, **data):
        logger.debug(f"Creating SearchResult with data: {data}")
        try:
            super().__init__(**data)
            logger.debug(f"✅ SearchResult created successfully with {len(self.sets)} sets")
        except Exception as e:
            logger.error(f"❌ Failed to create SearchResult: {e}")
            logger.error(f"Data provided: {data}")
            raise

    def dict(self, *args, **kwargs):
        logger.debug("Converting SearchResult to dict")
        return super().dict(*args, **kwargs)