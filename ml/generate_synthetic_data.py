#!/usr/bin/env python3
"""Generate synthetic BIO-tagged Indian address NER data as JSONL.

The generator intentionally uses public, real-world locality/street/landmark names
and combines them with synthetic house numbers and Hinglish templates. The generated
labels are useful for bootstrapping a model, but real annotated addresses should be
added before production use.

Output format per line:
{"text": "...", "tokens": [...], "ner_tags": [...]} 
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

SEED = 42
N = 5000
OUT = Path(__file__).with_name("synthetic_addresses.jsonl")
rng = random.Random(SEED)

STATES = {
    "Delhi": ["Delhi"],
    "Uttar Pradesh": ["Ghaziabad", "Noida", "Lucknow", "Kanpur", "Varanasi", "Prayagraj"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Karnataka": ["Bengaluru", "Mysuru"],
    "West Bengal": ["Kolkata"],
    "Tamil Nadu": ["Chennai", "Coimbatore"],
    "Telangana": ["Hyderabad"],
    "Rajasthan": ["Jaipur", "Jodhpur"],
    "Gujarat": ["Ahmedabad", "Surat"],
    "Bihar": ["Patna"],
    "Madhya Pradesh": ["Bhopal", "Indore"],
    "Haryana": ["Gurugram", "Faridabad"],
}

AREAS = [
    "Indirapuram", "Vaishali", "Vasundhara", "Kaushambi", "Raj Nagar", "Crossings Republik",
    "Sector 62", "Sector 18", "Dwarka", "Rohini", "Lajpat Nagar", "Saket", "Karol Bagh",
    "Connaught Place", "Andheri West", "Bandra West", "Powai", "Hinjewadi", "Kothrud",
    "Whitefield", "Koramangala", "Salt Lake", "New Town", "Gomti Nagar", "Aliganj",
    "Banjara Hills", "Hitech City", "Viman Nagar", "Adyar", "T Nagar", "Malviya Nagar",
]

STREETS = [
    "MG Road", "Main Road", "Station Road", "Link Road", "Ring Road", "Market Road",
    "Nehru Road", "Gandhi Road", "Park Street", "Church Road", "School Road", "Temple Road",
    "Canal Road", "Service Road", "College Road", "Road No 4", "Road No 7", "80 Feet Road",
    "NH 24", "GT Road", "Outer Ring Road", "Sector 5 Road", "Indira Road",
]

LANDMARKS = [
    "near Shipra Mall", "opposite Metro Station", "behind Vaishali Metro", "near City Mall",
    "beside Hanuman Mandir", "near the railway station", "opposite Apollo Hospital",
    "near ISKCON Temple", "behind the post office", "near Central Park", "next to DLF Mall",
    "near Akshardham Temple", "opposite the bus stand", "near the main market",
    "beside the police station", "near the flyover", "opposite the college gate",
]

HOUSE_PATTERNS = [
    "{n}", "House No {n}", "H No {n}", "Flat {n}", "Plot {n}", "{n}/{m}", "B-{n}", "C-{n}", "Gali {n}, House {m}",
]

TEMPLATES = [
    "{house}, {street}, {area}, {landmark}, {city}, {state}, {pin}",
    "{house} {street}, {area}, {city} {state} {pin}",
    "{house}, {landmark}, {street}, {area}, {city}, {pin}",
    "{house} {street} {area}, {landmark}, {city}, {state}",
    "{house}, {area}, {street}, {city}, {state} - {pin}",
    "{house}, {street}, {area}. Landmark: {landmark}. {city}, {state} {pin}",
]

HINGLISH_PREFIXES = [
    "", "near ", "ke paas ", "ke samne ", "bilkul near ", "opposite ", "behind ",
]


def pin_for_state(state: str) -> str:
    ranges = {
        "Delhi": (110001, 110099), "Uttar Pradesh": (201001, 226099), "Maharashtra": (400001, 440099),
        "Karnataka": (560001, 570099), "West Bengal": (700001, 743099), "Tamil Nadu": (600001, 641099),
        "Telangana": (500001, 509099), "Rajasthan": (302001, 342099), "Gujarat": (380001, 395099),
        "Bihar": (800001, 854099), "Madhya Pradesh": (462001, 482099), "Haryana": (121001, 136099),
    }
    lo, hi = ranges[state]
    return str(rng.randint(lo, hi))


def words(text: str) -> list[str]:
    # Preserve punctuation as separate tokens so BIO spans can be reconstructed.
    return re.findall(r"[\w/-]+|[^\w\s]", text, flags=re.UNICODE)


def label_tokens(text: str, fields: dict[str, str]) -> tuple[list[str], list[str]]:
    tokens = words(text)
    labels = ["O"] * len(tokens)
    for field, value in fields.items():
        if not value:
            continue
        target = words(value)
        for i in range(len(tokens) - len(target) + 1):
            if tokens[i : i + len(target)] == target and all(x == "O" for x in labels[i : i + len(target)]):
                labels[i] = f"B-{field}"
                for j in range(1, len(target)):
                    labels[i + j] = f"I-{field}"
                break
    return tokens, labels


def make_example() -> dict:
    state = rng.choice(list(STATES))
    city = rng.choice(STATES[state])
    area = rng.choice(AREAS)
    street = rng.choice(STREETS)
    landmark = rng.choice(LANDMARKS)
    n, m = rng.randint(1, 999), rng.randint(1, 99)
    house = rng.choice(HOUSE_PATTERNS).format(n=n, m=m)
    pin = pin_for_state(state)

    # Add light code-mixing without making labels ambiguous.
    landmark = rng.choice([landmark, landmark.replace("near ", "ke paas "), landmark.replace("opposite ", "ke samne ")])
    values = {"HOUSE": house, "STREET": street, "AREA": area, "LANDMARK": landmark, "CITY": city, "STATE": state, "PIN": pin}
    text = rng.choice(TEMPLATES).format(**{k.lower(): v for k, v in values.items()})
    tokens, tags = label_tokens(text, values)
    return {"text": text, "tokens": tokens, "ner_tags": tags}


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    with OUT.open("w", encoding="utf-8") as f:
        while len(seen) < N:
            ex = make_example()
            if ex["text"] in seen:
                continue
            seen.add(ex["text"])
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(seen)} examples to {OUT}")


if __name__ == "__main__":
    main()
