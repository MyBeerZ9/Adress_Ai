from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AddressRequest(BaseModel):
    address: str = Field(..., min_length=3, description="Raw unstructured Indian address string", example="2nd floor, pink building, near ICICI bank, Rajouri Garden, Delhi 110027")


class StructuredComponents(BaseModel):
    house_number: Optional[str] = Field(None, description="House number, flat, floor, or building name", example="2nd floor, pink building")
    street: Optional[str] = Field(None, description="Street name, road, or lane", example="Main Ring Road")
    landmark: Optional[str] = Field(None, description="Prominent landmark (near, opp, behind, etc.)", example="ICICI bank")
    sublocality: Optional[str] = Field(None, description="Sublocality, sector, or block", example="Rajouri Garden Block A")
    locality: Optional[str] = Field(None, description="Locality or area", example="Rajouri Garden")
    city: Optional[str] = Field(None, description="City, district, or municipal corporation", example="Delhi")
    state: Optional[str] = Field(None, description="State or Union Territory", example="Delhi")
    postal_code: Optional[str] = Field(None, description="6-digit Indian PIN code", example="110027")
    country: str = Field("India", description="Country")


class Coordinates(BaseModel):
    lat: float = Field(..., description="Latitude", example=28.6475)
    lng: float = Field(..., description="Longitude", example=77.1215)


class ParseResponse(BaseModel):
    original_address: str
    structured_components: StructuredComponents
    coordinates: Coordinates
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    formatted_address: str
    landmark_detected: Optional[str] = None
    provider: str = Field(..., description="Geocoding provider used (google / osm_fallback / heuristics)")
    raw_geocoder_data: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    google_api_configured: bool
