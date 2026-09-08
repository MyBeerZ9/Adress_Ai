"""FastAPI integration for an address NER model.

Import `MLAddressParser` into your existing FastAPI app and call `parse_ml_address`.
The geocoding function is deliberately injected so this module can reuse your existing
Google Geocoding implementation without duplicating credentials or HTTP logic.
"""
from __future__ import annotations

import os
from typing import Callable, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

MODEL_ID = os.getenv("ADDRESS_NER_MODEL", "YOUR_HF_USERNAME/indian-address-ner")
LOCAL_MODEL = os.getenv("ADDRESS_NER_LOCAL_PATH", "")
CONFIDENCE_THRESHOLD = float(os.getenv("ADDRESS_NER_CONFIDENCE", "0.55"))

LABELS = {"HOUSE", "STREET", "LANDMARK", "AREA", "CITY", "STATE", "PIN"}


class ParseRequest(BaseModel):
    address: str


class MLAddressParser:
    def __init__(self, geocode: Callable[[str], Any]):
        """geocode(query) should be your existing Google geocoder function."""
        self.geocode = geocode
        model_path = LOCAL_MODEL or MODEL_ID
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.ner = pipeline(
            "token-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
        )

    def extract(self, address: str) -> tuple[dict[str, str], float]:
        entities = self.ner(address)
        components: dict[str, list[str]] = {}
        scores = []
        for entity in entities:
            raw_label = str(entity["entity_group"]).replace("B-", "").replace("I-", "")
            if raw_label not in LABELS:
                continue
            components.setdefault(raw_label, []).append(str(entity["word"]).strip())
            scores.append(float(entity["score"]))
        result = {k: " ".join(v) for k, v in components.items()}
        confidence = sum(scores) / len(scores) if scores else 0.0
        return result, confidence

    def parse(self, address: str) -> dict[str, Any]:
        components, confidence = self.extract(address)
        # Avoid malformed queries when optional fields are absent.
        query_parts = [
            components.get("HOUSE", ""),
            components.get("STREET", ""),
            components.get("AREA", ""),
            components.get("CITY", ""),
            components.get("PIN", ""),
        ]
        cleaned_query = ", ".join(p for p in query_parts if p)

        if confidence < CONFIDENCE_THRESHOLD or not cleaned_query:
            geocode_result = self.geocode(address)
            return {
                "method": "raw_fallback",
                "confidence": confidence,
                "components": components,
                "query": address,
                "geocode": geocode_result,
            }

        geocode_result = self.geocode(cleaned_query)
        return {
            "method": "ml",
            "confidence": confidence,
            "components": components,
            "query": cleaned_query,
            "geocode": geocode_result,
        }


# Example wiring:
# from your_existing_module import google_geocode
# parser = MLAddressParser(google_geocode)
# router = APIRouter()
# @router.post("/parse_ml")
# def parse_ml(req: ParseRequest):
#     try:
#         return parser.parse(req.address)
#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=str(exc))
