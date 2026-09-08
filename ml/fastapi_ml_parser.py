"""FastAPI integration for the fine-tuned Indian address NER model."""
from __future__ import annotations

import inspect
import os
from typing import Any, Callable

from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

MODEL_ID = os.getenv("ADDRESS_NER_MODEL", "")
LOCAL_MODEL = os.getenv("ADDRESS_NER_LOCAL_PATH", "")
CONFIDENCE_THRESHOLD = float(os.getenv("ADDRESS_NER_CONFIDENCE", "0.55"))
LABELS = {"HOUSE", "STREET", "LANDMARK", "AREA", "CITY", "STATE", "PIN"}


class MLAddressParser:
    """Lazy-loading NER wrapper that reuses the app's existing geocoder."""

    def __init__(self, geocode: Callable[[str], Any]):
        self.geocode = geocode
        self._ner = None

    def _load_model(self):
        if self._ner is not None:
            return self._ner
        model_path = LOCAL_MODEL or MODEL_ID
        if not model_path:
            raise RuntimeError("Set ADDRESS_NER_MODEL or ADDRESS_NER_LOCAL_PATH before using /parse_ml")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForTokenClassification.from_pretrained(model_path)
        self._ner = pipeline("token-classification", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
        return self._ner

    def extract(self, address: str) -> tuple[dict[str, str], float]:
        entities = self._load_model()(address)
        components: dict[str, list[str]] = {}
        scores: list[float] = []
        for entity in entities:
            label = str(entity.get("entity_group", "")).replace("B-", "").replace("I-", "")
            if label not in LABELS:
                continue
            components.setdefault(label, []).append(str(entity.get("word", "")).strip())
            scores.append(float(entity.get("score", 0.0)))
        confidence = sum(scores) / len(scores) if scores else 0.0
        return {k: " ".join(v) for k, v in components.items()}, confidence

    async def _call_geocoder(self, query: str):
        result = self.geocode(query)
        return await result if inspect.isawaitable(result) else result

    async def parse(self, address: str) -> dict[str, Any]:
        components, confidence = self.extract(address)
        cleaned_query = ", ".join(components.get(k, "") for k in ("HOUSE", "STREET", "AREA", "CITY", "PIN") if components.get(k))
        if confidence < CONFIDENCE_THRESHOLD or not cleaned_query:
            result = await self._call_geocoder(address)
            return {"method": "raw_fallback", "confidence": confidence, "components": components, "query": address, "geocode": result}
        result = await self._call_geocoder(cleaned_query)
        return {"method": "ml", "confidence": confidence, "components": components, "query": cleaned_query, "geocode": result}
