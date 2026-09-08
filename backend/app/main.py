import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .config import GOOGLE_API_KEY, HOST, PORT, DEBUG
from .models import AddressRequest, ParseResponse, HealthResponse
from .geocoder import parse_and_geocode_address

logging.basicConfig(
    level=logging.INFO if not DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("addressai")

app = FastAPI(
    title="AddressAI API",
    description="Intelligent Indian Address Parser and Geocoding Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for local development and deployed frontends
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
        "version": "1.0.0",
        "endpoints": {
            "parse": "POST /parse",
            "health": "GET /health",
            "documentation": "GET /docs",
        },
    }


@app.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    return HealthResponse(
        status="healthy",
        service="AddressAI-Backend",
        version="1.0.0",
        google_api_configured=bool(GOOGLE_API_KEY),
    )


@app.post(
    "/parse",
    response_model=ParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse Indian Address",
    description="Accepts an unstructured Indian address string, extracts structured components, detects landmarks, and returns geocoded coordinates.",
)
async def parse_address_endpoint(request: AddressRequest):
    raw_addr = request.address.strip()
    if not raw_addr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Address string cannot be empty",
        )

    logger.info(f"Parsing address: {raw_addr[:60]}...")
    try:
        response = await parse_and_geocode_address(raw_addr)
        return response
    except Exception as e:
        logger.error(f"Error parsing address '{raw_addr}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing the address: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=DEBUG)
