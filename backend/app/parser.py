import re
from typing import Dict, Optional, Tuple

INDIAN_STATES_AND_UTS = {
    "andhra pradesh": "Andhra Pradesh",
    "arunachal pradesh": "Arunachal Pradesh",
    "assam": "Assam",
    "bihar": "Bihar",
    "chhattisgarh": "Chhattisgarh",
    "goa": "Goa",
    "gujarat": "Gujarat",
    "haryana": "Haryana",
    "himachal pradesh": "Himachal Pradesh",
    "jharkhand": "Jharkhand",
    "karnataka": "Karnataka",
    "kerala": "Kerala",
    "madhya pradesh": "Madhya Pradesh",
    "maharashtra": "Maharashtra",
    "manipur": "Manipur",
    "meghalaya": "Meghalaya",
    "mizoram": "Mizoram",
    "nagaland": "Nagaland",
    "odisha": "Odisha",
    "orissa": "Odisha",
    "punjab": "Punjab",
    "rajasthan": "Rajasthan",
    "sikkim": "Sikkim",
    "tamil nadu": "Tamil Nadu",
    "telangana": "Telangana",
    "tripura": "Tripura",
    "uttar pradesh": "Uttar Pradesh",
    "uttarakhand": "Uttarakhand",
    "west bengal": "West Bengal",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "nct of delhi": "Delhi",
    "chandigarh": "Chandigarh",
    "puducherry": "Puducherry",
    "pondicherry": "Puducherry",
    "jammu and kashmir": "Jammu & Kashmir",
    "jammu & kashmir": "Jammu & Kashmir",
    "ladakh": "Ladakh",
    "andaman and nicobar islands": "Andaman & Nicobar",
    "dadra and nagar haveli": "Dadra & Nagar Haveli",
    "daman and diu": "Daman & Diu",
    "lakshadweep": "Lakshadweep",
}

PINCODE_PREFIX_TO_STATE = {
    "11": "Delhi",
    "12": "Haryana",
    "13": "Haryana",
    "14": "Punjab",
    "15": "Punjab",
    "16": "Chandigarh",
    "17": "Himachal Pradesh",
    "18": "Jammu & Kashmir",
    "19": "Jammu & Kashmir",
    "20": "Uttar Pradesh",
    "21": "Uttar Pradesh",
    "22": "Uttar Pradesh",
    "23": "Uttar Pradesh",
    "24": "Uttarakhand",
    "25": "Uttar Pradesh",
    "26": "Uttarakhand",
    "27": "Uttar Pradesh",
    "28": "Uttar Pradesh",
    "30": "Rajasthan",
    "31": "Rajasthan",
    "32": "Rajasthan",
    "33": "Rajasthan",
    "34": "Rajasthan",
    "36": "Gujarat",
    "37": "Gujarat",
    "38": "Gujarat",
    "39": "Gujarat",
    "40": "Maharashtra",
    "41": "Maharashtra",
    "42": "Maharashtra",
    "43": "Maharashtra",
    "44": "Maharashtra",
    "45": "Madhya Pradesh",
    "46": "Madhya Pradesh",
    "47": "Madhya Pradesh",
    "48": "Madhya Pradesh",
    "49": "Chhattisgarh",
    "50": "Telangana",
    "51": "Andhra Pradesh",
    "52": "Andhra Pradesh",
    "53": "Andhra Pradesh",
    "56": "Karnataka",
    "57": "Karnataka",
    "58": "Karnataka",
    "59": "Karnataka",
    "60": "Tamil Nadu",
    "61": "Tamil Nadu",
    "62": "Tamil Nadu",
    "63": "Tamil Nadu",
    "64": "Tamil Nadu",
    "67": "Kerala",
    "68": "Kerala",
    "69": "Kerala",
    "70": "West Bengal",
    "71": "West Bengal",
    "72": "West Bengal",
    "73": "West Bengal",
    "74": "West Bengal",
    "75": "Odisha",
    "76": "Odisha",
    "77": "Odisha",
    "78": "Assam",
    "79": "North Eastern States",
    "80": "Bihar",
    "81": "Bihar",
    "82": "Jharkhand",
    "83": "Jharkhand",
    "84": "Bihar",
    "85": "Bihar",
}

MAJOR_CITIES = [
    "mumbai", "delhi", "new delhi", "bengaluru", "bangalore", "hyderabad", "ahmedabad",
    "chennai", "kolkata", "surat", "pune", "jaipur", "lucknow", "kanpur", "nagpur",
    "indore", "thane", "bhopal", "visakhapatnam", "patna", "vadodara", "ghaziabad",
    "ludhiana", "agra", "nashik", "faridabad", "meerut", "rajkot", "varanasi", "srinagar",
    "aurangabad", "dhanbad", "amritsar", "navi mumbai", "allahabad", "prayagraj", "ranchi",
    "howrah", "coimbatore", "jabalpur", "gwalior", "vijayawada", "jodhpur", "madurai",
    "raipur", "kota", "guwahati", "chandigarh", "solapur", "hubli", "mysore", "mysuru",
    "gurgaon", "gurugram", "noida", "greater noida", "dehradun", "kochi", "cochin",
    "thiruvananthapuram", "trivandrum", "mangalore", "mangaluru", "shimla", "shillong"
]

LANDMARK_PATTERNS = [
    r"(?:near|nr\.?|nearby|in front of|front of|opp\.?|opposite to|opposite|behind|beside|adjacent to|next to|close to|facing)\s+([^,]+)",
]

HOUSE_PATTERNS = [
    r"(?:flat\s*(?:no\.?|#)?\s*\w+)",
    r"(?:plot\s*(?:no\.?|#)?\s*\w+)",
    r"(?:house\s*(?:no\.?|#)?\s*\w+)",
    r"(?:h\.?\s*no\.?\s*\w+)",
    r"(?:shop\s*(?:no\.?|#)?\s*\w+)",
    r"(?:room\s*(?:no\.?|#)?\s*\w+)",
    r"(?:\d+(?:st|nd|rd|th)\s+floor)",
    r"(?:ground\s+floor|basement|terrace)",
    r"(?:tower\s*[\w\-]+)",
    r"(?:block\s*[\w\-]+)",
    r"(?:phase\s*[\w\-]+)",
    r"(?:sector\s*[\w\-]+)",
    r"(?:[a-zA-Z\s]+(?:building|residency|apartments?|heights?|villa|enclave|society|plaza|complex|homes?))",
]

STREET_PATTERNS = [
    r"\b([a-zA-Z0-9\s]+(?:\broad\b|\brd\b|\bmarg\b|\bstreet\b|\bst\b|\blane\b|\bgali\b|\bpath\b|\bchowk\b|\bcircle\b|\bbypass\b|\bhighway\b|\bexpressway\b|\bavenue\b|\bdrive\b|\bcross\b|\bmain\s+road\b))",
]


def extract_pincode(raw_text: str) -> Tuple[Optional[str], str]:
    """Extracts 6-digit Indian PIN code and returns (pincode, cleaned_text)."""
    match = re.search(r"\b([1-9][0-9]{5})\b", raw_text)
    if match:
        pin = match.group(1)
        cleaned = raw_text[:match.start()] + " " + raw_text[match.end():]
        return pin, cleaned.strip()
    return None, raw_text


def extract_landmark(raw_text: str) -> Tuple[Optional[str], str]:
    """Extracts landmarks like 'near ICICI bank' or 'opp Forum Mall'."""
    for pattern in LANDMARK_PATTERNS:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            landmark_val = match.group(1).strip()
            # Clean off trailing words that might be commas or conjunctions
            landmark_val = re.sub(r"[,;]+.*$", "", landmark_val).strip()
            cleaned = raw_text[:match.start()] + " " + raw_text[match.end():]
            return landmark_val, cleaned.strip()
    return None, raw_text


def extract_state(raw_text: str, pincode: Optional[str] = None) -> Tuple[Optional[str], str]:
    """Detects Indian state from text or infers from pincode."""
    text_lower = raw_text.lower()
    for key, formal_name in sorted(INDIAN_STATES_AND_UTS.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"\b" + re.escape(key) + r"\b"
        match = re.search(pattern, text_lower)
        if match:
            cleaned = raw_text[:match.start()] + " " + raw_text[match.end():]
            return formal_name, cleaned.strip()

    if pincode and len(pincode) == 6:
        prefix = pincode[:2]
        if prefix in PINCODE_PREFIX_TO_STATE:
            return PINCODE_PREFIX_TO_STATE[prefix], raw_text

    return None, raw_text


def extract_city(raw_text: str) -> Tuple[Optional[str], str]:
    """Detects major Indian cities in the address string."""
    text_lower = raw_text.lower()
    for city in sorted(MAJOR_CITIES, key=lambda x: len(x), reverse=True):
        pattern = r"\b" + re.escape(city) + r"\b"
        match = re.search(pattern, text_lower)
        if match:
            matched_city = raw_text[match.start():match.end()].title()
            cleaned = raw_text[:match.start()] + " " + raw_text[match.end():]
            # Normalize naming
            if city in ["bengaluru", "bangalore"]:
                matched_city = "Bengaluru"
            elif city in ["delhi", "new delhi"]:
                matched_city = "Delhi"
            elif city in ["gurgaon", "gurugram"]:
                matched_city = "Gurugram"
            return matched_city, cleaned.strip()
    return None, raw_text


def extract_house_and_building(raw_text: str) -> Tuple[Optional[str], str]:
    """Extracts house number, flat number, floor, or building/society name."""
    found_parts = []
    remaining = raw_text

    # Split by comma first to preserve logical tokens
    tokens = [t.strip() for t in remaining.split(",") if t.strip()]
    tokens_to_keep = []

    for token in tokens:
        is_house = False
        for p in HOUSE_PATTERNS:
            if re.search(p, token, re.IGNORECASE):
                found_parts.append(token)
                is_house = True
                break
        if not is_house:
            # Check for leading number like "402" or "B-12"
            if re.match(r"^[A-Za-z]?\s*[-/]?\s*\d+[A-Za-z0-9\-/]*$", token.strip()):
                found_parts.append(token)
            else:
                tokens_to_keep.append(token)

    house_str = ", ".join(found_parts) if found_parts else None
    cleaned_str = ", ".join(tokens_to_keep)
    return house_str, cleaned_str


def extract_street(raw_text: str) -> Tuple[Optional[str], str]:
    """Extracts street/road names."""
    tokens = [t.strip() for t in raw_text.split(",") if t.strip()]
    street_parts = []
    tokens_to_keep = []

    for token in tokens:
        matched = False
        for p in STREET_PATTERNS:
            if re.search(p, token, re.IGNORECASE):
                street_parts.append(token)
                matched = True
                break
        if not matched:
            tokens_to_keep.append(token)

    street_str = ", ".join(street_parts) if street_parts else None
    cleaned_str = ", ".join(tokens_to_keep)
    return street_str, cleaned_str


def parse_indian_address_rules(raw_address: str) -> Dict[str, Optional[str]]:
    """
    Parses a raw unstructured Indian address into structured components:
    house_number, street, landmark, sublocality, locality, city, state, postal_code, country
    """
    cleaned = raw_address.strip()

    # Step 1: Extract PIN code
    pincode, cleaned = extract_pincode(cleaned)

    # Step 2: Extract Landmark
    landmark, cleaned = extract_landmark(cleaned)

    # Step 3: Extract State
    state, cleaned = extract_state(cleaned, pincode)

    # Step 4: Extract City
    city, cleaned = extract_city(cleaned)

    # Step 5: Extract House / Building / Floor
    house, cleaned = extract_house_and_building(cleaned)

    # Step 6: Extract Street / Road
    street, cleaned = extract_street(cleaned)

    # Step 7: The remaining components are sublocality / locality
    remaining_parts = [p.strip() for p in re.split(r"[,;]+", cleaned) if p.strip()]

    sublocality = None
    locality = None

    if len(remaining_parts) >= 2:
        sublocality = remaining_parts[0]
        locality = ", ".join(remaining_parts[1:])
    elif len(remaining_parts) == 1:
        locality = remaining_parts[0]

    # If city is missing but state is a City/UT like Delhi or Chandigarh
    if not city and state in ["Delhi", "Chandigarh", "Puducherry"]:
        city = state

    return {
        "house_number": house,
        "street": street,
        "landmark": landmark,
        "sublocality": sublocality,
        "locality": locality,
        "city": city,
        "state": state,
        "postal_code": pincode,
        "country": "India",
    }
