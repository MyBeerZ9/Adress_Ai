import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .config import GOOGLE_API_KEY, HOST, PORT, DEBUG
from .models import AddressRequest, ParseResponse, HealthResponse
from .geocoder import parse_and_geocode_address, geocode_with_google
from ml.fastapi_ml_parser import MLAddressParser

logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("addressai")

app = FastAPI(
    title="AddressAI API",
    description="Intelligent Indian Address Parser and Geocoding Service",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="API Root")
async def root():
    return {
        "name": "AddressAI API",
        "description": "Indian Address Parser & Geolocation Engine",
        "version": "1.1.0",
        "endpoints": {
            "parse": "POST /parse",
            "parse_ml": "POST /parse_ml",
            "health": "GET /health",
            "documentation": "GET /docs",
        },
    }


@app.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    return HealthResponse(
        status="healthy",
        service="AddressAI-Backend",
        version="1.1.0",
        google_api_configured=bool(GOOGLE_API_KEY),
    )


@app.post("/parse", response_model=ParseResponse, status_code=status.HTTP_200_OK)
async def parse_address_endpoint(request: AddressRequest):
    raw_addr = request.address.strip()
    if not raw_addr:
        raise HTTPException(status_code=400, detail="Address string cannot be empty")
    logger.info(f"Parsing address: {raw_addr[:60]}...")
    try:
        return await parse_and_geocode_address(raw_addr)
    except Exception as e:
        logger.error(f"Error parsing address '{raw_addr}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred while parsing the address: {str(e)}")


async def ml_geocode(query: str):
    """Adapt the existing async Google geocoder to the ML parser's injected callback."""
    result = await geocode_with_google(query)
    if not result:
        # Keep the API useful when Google has no result/configuration.
        fallback = await parse_and_geocode_address(query)
        return {
            "coordinates": {"lat": fallback.coordinates.lat, "lng": fallback.coordinates.lng},
            "formatted_address": fallback.formatted_address,
            "provider": fallback.provider,
        }
    location = result.get("geometry", {}).get("location", {})
    return {
        "coordinates": {"lat": float(location.get("lat", 0)), "lng": float(location.get("lng", 0))},
        "formatted_address": result.get("formatted_address", query),
        "provider": "google",
        "place_id": result.get("place_id"),
        "location_type": result.get("geometry", {}).get("location_type"),
    }


# The model itself is lazy-loaded by MLAddressParser, so backend startup does not
# download a Hugging Face model. It is loaded on the first /parse_ml request.
ml_parser = MLAddressParser(ml_geocode)


@app.post("/parse_ml", summary="ML-enhanced Indian Address Parser")
async def parse_ml_endpoint(request: AddressRequest):
    raw_addr = request.address.strip()
    if not raw_addr:
        raise HTTPException(status_code=400, detail="Address string cannot be empty")
    try:
        return await ml_parser.parse(raw_addr)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        logger.error(f"ML parsing failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ML parsing failed: {str(exc)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=DEBUG)
