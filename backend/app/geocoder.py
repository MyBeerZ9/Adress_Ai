import logging
from typing import Dict, Any, Optional, Tuple
import httpx
from .config import GOOGLE_API_KEY
from .parser import parse_indian_address_rules
from .models import StructuredComponents, Coordinates, ParseResponse

logger = logging.getLogger(__name__)

# Fallback coordinates for major Indian metro regions if external APIs are unreachable
FALLBACK_CITY_COORDINATES = {
    "Delhi": (28.6139, 77.2090),
    "New Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Bangalore": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Chandigarh": (30.7333, 76.7794),
    "Noida": (28.5355, 77.3910),
    "Gurugram": (28.4595, 77.0266),
    "Gurgaon": (28.4595, 77.0266),
}


def extract_components_from_google_result(result: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Extracts structured components from Google Geocoding response."""
    components: Dict[str, Optional[str]] = {
        "house_number": None,
        "street": None,
        "landmark": None,
        "sublocality": None,
        "locality": None,
        "city": None,
        "state": None,
        "postal_code": None,
        "country": "India",
    }

    addr_components = result.get("address_components", [])
    for comp in addr_components:
        types = comp.get("types", [])
        long_name = comp.get("long_name", "")

        if "street_number" in types or "subpremise" in types or "premise" in types:
            if not components["house_number"]:
                components["house_number"] = long_name
            else:
                components["house_number"] += f", {long_name}"
        elif "route" in types:
            components["street"] = long_name
        elif "sublocality_level_1" in types or "sublocality" in types:
            components["sublocality"] = long_name
        elif "locality" in types or "sublocality_level_2" in types:
            if not components["locality"]:
                components["locality"] = long_name
        elif "administrative_area_level_2" in types:
            components["city"] = long_name
        elif "administrative_area_level_1" in types:
            components["state"] = long_name
        elif "postal_code" in types:
            components["postal_code"] = long_name
        elif "point_of_interest" in types or "establishment" in types:
            components["landmark"] = long_name

    if not components["city"] and components["locality"]:
        components["city"] = components["locality"]

    return components


def calculate_confidence_score(
    components: StructuredComponents,
    location_type: str = "APPROXIMATE",
    has_pincode: bool = False,
    has_landmark: bool = False,
) -> float:
    """
    Computes a realistic confidence score between 0.0 and 1.0 based on:
    - Number of matched structured components
    - Validity of PIN code
    - Landmark extraction
    - Geocoding accuracy level (ROOFTOP, RANGE_INTERPOLATED, GEOMETRIC_CENTER, APPROXIMATE)
    """
    score = 0.35  # base score

    # Field presence bonuses
    if components.postal_code and len(components.postal_code) == 6:
        score += 0.20
    if components.state:
        score += 0.10
    if components.city:
        score += 0.10
    if components.locality:
        score += 0.08
    if components.sublocality:
        score += 0.05
    if components.street:
        score += 0.05
    if components.house_number:
        score += 0.07
    if components.landmark or has_landmark:
        score += 0.05

    # Location type bonus
    if location_type == "ROOFTOP":
        score += 0.10
    elif location_type == "RANGE_INTERPOLATED":
        score += 0.06
    elif location_type == "GEOMETRIC_CENTER":
        score += 0.03

    return round(min(score, 0.99), 2)


async def geocode_with_google(address: str, landmark_query: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Calls Google Geocoding API."""
    if not GOOGLE_API_KEY:
        return None

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "components": "country:IN",
        "key": GOOGLE_API_KEY,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params)
            data = resp.json()
            if data.get("status") == "OK" and data.get("results"):
                return data["results"][0]

            # If raw address failed and landmark query is provided, retry with landmark query
            if landmark_query:
                params["address"] = landmark_query
                resp = await client.get(url, params=params)
                data = resp.json()
                if data.get("status") == "OK" and data.get("results"):
                    return data["results"][0]

        except Exception as e:
            logger.error(f"Google Geocoding API error: {e}")

    return None


async def geocode_with_osm(query: str) -> Optional[Dict[str, Any]]:
    """Fallback geocoding using OpenStreetMap Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "AddressAI-Parser/1.0 (contact@addressai.local)"}
    params = {
        "q": f"{query}, India",
        "format": "json",
        "addressdetails": 1,
        "limit": 1,
        "countrycodes": "in",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                results = resp.json()
                if results and len(results) > 0:
                    return results[0]
        except Exception as e:
            logger.error(f"OSM Nominatim Geocoding error: {e}")

    return None


async def parse_and_geocode_address(raw_address: str) -> ParseResponse:
    """
    Main parsing orchestrator:
    1. Parse with rule-based Indian address parser
    2. Attempt Google Geocoding API with landmark enhancement
    3. Fallback to OpenStreetMap / Indian Geocoding heuristics if needed
    4. Reconcile structured components & calculate confidence
    """
    rule_parsed = parse_indian_address_rules(raw_address)
    landmark = rule_parsed.get("landmark")
    city = rule_parsed.get("city")
    locality = rule_parsed.get("locality")
    state = rule_parsed.get("state")
    pincode = rule_parsed.get("postal_code")

    # Build landmark-enhanced search query if available
    landmark_query = None
    if landmark:
        landmark_parts = [landmark]
        if locality:
            landmark_parts.append(locality)
        if city:
            landmark_parts.append(city)
        if state:
            landmark_parts.append(state)
        if pincode:
            landmark_parts.append(pincode)
        landmark_query = ", ".join(landmark_parts)

    google_result = await geocode_with_google(raw_address, landmark_query)

    if google_result:
        provider = "google"
        geometry = google_result.get("geometry", {})
        loc = geometry.get("location", {})
        lat = float(loc.get("lat", 28.6139))
        lng = float(loc.get("lng", 77.2090))
        location_type = geometry.get("location_type", "APPROXIMATE")
        formatted_address = google_result.get("formatted_address", raw_address)

        google_components = extract_components_from_google_result(google_result)

        # Merge rule-parsed and google-extracted components
        final_components = StructuredComponents(
            house_number=rule_parsed.get("house_number") or google_components.get("house_number"),
            street=rule_parsed.get("street") or google_components.get("street"),
            landmark=landmark or google_components.get("landmark"),
            sublocality=rule_parsed.get("sublocality") or google_components.get("sublocality"),
            locality=rule_parsed.get("locality") or google_components.get("locality"),
            city=rule_parsed.get("city") or google_components.get("city"),
            state=rule_parsed.get("state") or google_components.get("state"),
            postal_code=pincode or google_components.get("postal_code"),
            country="India",
        )

        confidence = calculate_confidence_score(
            final_components,
            location_type=location_type,
            has_pincode=bool(pincode),
            has_landmark=bool(landmark),
        )

        return ParseResponse(
            original_address=raw_address,
            structured_components=final_components,
            coordinates=Coordinates(lat=lat, lng=lng),
            confidence_score=confidence,
            formatted_address=formatted_address,
            landmark_detected=landmark,
            provider=provider,
            raw_geocoder_data={"location_type": location_type, "place_id": google_result.get("place_id")},
        )

    # Fallback to OpenStreetMap
    osm_query = ", ".join([p for p in [locality, city, state, pincode] if p]) or raw_address
    osm_result = await geocode_with_osm(osm_query)

    if osm_result:
        provider = "openstreetmap"
        lat = float(osm_result.get("lat", 28.6139))
        lng = float(osm_result.get("lon", 77.2090))
        formatted_address = osm_result.get("display_name", raw_address)
        osm_addr = osm_result.get("address", {})

        final_components = StructuredComponents(
            house_number=rule_parsed.get("house_number"),
            street=rule_parsed.get("street") or osm_addr.get("road"),
            landmark=landmark,
            sublocality=rule_parsed.get("sublocality") or osm_addr.get("suburb"),
            locality=rule_parsed.get("locality") or osm_addr.get("neighbourhood") or osm_addr.get("suburb"),
            city=city or osm_addr.get("city") or osm_addr.get("town") or osm_addr.get("state_district"),
            state=state or osm_addr.get("state"),
            postal_code=pincode or osm_addr.get("postcode"),
            country="India",
        )

        confidence = calculate_confidence_score(
            final_components,
            location_type="GEOMETRIC_CENTER",
            has_pincode=bool(pincode),
            has_landmark=bool(landmark),
        )

        return ParseResponse(
            original_address=raw_address,
            structured_components=final_components,
            coordinates=Coordinates(lat=lat, lng=lng),
            confidence_score=confidence,
            formatted_address=formatted_address,
            landmark_detected=landmark,
            provider=provider,
            raw_geocoder_data={"osm_id": osm_result.get("osm_id"), "type": osm_result.get("type")},
        )

    # Fallback to City Heuristics
    fallback_lat, fallback_lng = (28.6139, 77.2090)
    for city_key, coords in FALLBACK_CITY_COORDINATES.items():
        if (city and city_key.lower() in city.lower()) or city_key.lower() in raw_address.lower():
            fallback_lat, fallback_lng = coords
            break

    final_components = StructuredComponents(
        house_number=rule_parsed.get("house_number"),
        street=rule_parsed.get("street"),
        landmark=landmark,
        sublocality=rule_parsed.get("sublocality"),
        locality=locality,
        city=city or "Delhi",
        state=state or "Delhi",
        postal_code=pincode,
        country="India",
    )

    confidence = calculate_confidence_score(
        final_components,
        location_type="APPROXIMATE",
        has_pincode=bool(pincode),
        has_landmark=bool(landmark),
    )

    formatted_parts = [
        final_components.house_number,
        final_components.street,
        f"Near {final_components.landmark}" if final_components.landmark else None,
        final_components.sublocality,
        final_components.locality,
        final_components.city,
        final_components.state,
        final_components.postal_code,
        "India",
    ]
    formatted_address = ", ".join([p for p in formatted_parts if p])

    return ParseResponse(
        original_address=raw_address,
        structured_components=final_components,
        coordinates=Coordinates(lat=fallback_lat, lng=fallback_lng),
        confidence_score=confidence,
        formatted_address=formatted_address,
        landmark_detected=landmark,
        provider="heuristic_fallback",
        raw_geocoder_data={"note": "Geocoded using Indian city heuristic coordinates"},
    )
