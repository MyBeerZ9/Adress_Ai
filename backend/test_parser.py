import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.parser import parse_indian_address_rules
from app.geocoder import parse_and_geocode_address


async def run_tests():
    test_addresses = [
        "2nd floor, pink building, near ICICI bank, Rajouri Garden, Delhi 110027",
        "Flat 402, Sai Residency, Opp. Forum Mall, Koramangala 7th Block, Bengaluru, Karnataka 560095",
        "Shop No 14, Behind Grand Hotel, Marine Drive, Nariman Point, Mumbai 400021",
        "Plot No 12, Block EP & GP, Near Webel Bhavan, Sector V, Salt Lake, Kolkata 700091",
        "Tower 3, 5th Floor, Cyber Gateway, Near Hitec City Metro Station, Madhapur, Hyderabad 500081",
    ]

    print("=== Testing AddressAI Parser ===")
    for addr in test_addresses:
        print(f"\n[Raw Input]: {addr}")
        result = await parse_and_geocode_address(addr)
        print(f"  -> House/Building : {result.structured_components.house_number}")
        print(f"  -> Landmark       : {result.structured_components.landmark}")
        print(f"  -> Locality       : {result.structured_components.locality}")
        print(f"  -> City           : {result.structured_components.city}")
        print(f"  -> State          : {result.structured_components.state}")
        print(f"  -> PIN            : {result.structured_components.postal_code}")
        print(f"  -> Coordinates    : ({result.coordinates.lat}, {result.coordinates.lng})")
        print(f"  -> Confidence     : {result.confidence_score * 100}%")
        print(f"  -> Provider       : {result.provider}")

    print("\nAll parser tests executed successfully!")


if __name__ == "__main__":
    asyncio.run(run_tests())
