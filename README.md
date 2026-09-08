# AddressAI 📍🇮🇳

> Intelligent Indian address parser with a rule-based `/parse` endpoint and an optional multilingual ML `/parse_ml` pipeline.

## Existing app

The existing app is a React/Vite frontend plus FastAPI backend. Keep `/parse` unchanged while testing the ML path.

## ML enhancement

`raw address → XLM-R token classifier → HOUSE/STREET/LANDMARK/AREA/CITY/STATE/PIN → cleaned Google query → coordinates`

If average NER confidence is below the configured threshold, `/parse_ml` falls back to the original raw Google geocoding path.

### ML files

- `ml/generate_synthetic_data.py` — creates ~5,000 varied BIO-tagged JSONL examples using real Indian locality/street/landmark names plus synthetic house numbers and Hinglish templates.
- `ml/train_address_ner_colab.ipynb` — Google Colab training notebook using `xlm-roberta-base`, Hugging Face `Trainer`, seqeval precision/recall/F1, and Hugging Face Hub upload.
- `ml/fastapi_ml_parser.py` — reusable FastAPI parser that can be wired to the existing Google geocoder.
- `ml/requirements.txt` — ML dependencies.

## 1. Generate the synthetic dataset

```bash
python ml/generate_synthetic_data.py
```

Creates `ml/synthetic_addresses.jsonl` with 5,000 unique examples. Synthetic data is only a bootstrap; add consented/anonymized human-labeled addresses before production benchmarking.

## 2. Fine-tune in free Google Colab

Open `ml/train_address_ner_colab.ipynb` in Colab. Upload `synthetic_addresses.jsonl`, run all cells, and sign in with a Hugging Face write token when prompted.

Replace:

```text
YOUR_HF_USERNAME/indian-address-ner
```

with your own Hugging Face model repository. The notebook trains `xlm-roberta-base`, reports precision/recall/F1/accuracy, and pushes the model + tokenizer to the Hub.

## 3. FastAPI integration

Install ML dependencies in the backend environment:

```bash
pip install -r ml/requirements.txt
```

Set these environment variables; never commit tokens:

```text
ADDRESS_NER_MODEL=YOUR_HF_USERNAME/indian-address-ner
ADDRESS_NER_LOCAL_PATH=
ADDRESS_NER_CONFIDENCE=0.55
GOOGLE_API_KEY=your_existing_google_key
```

Then adapt this wiring to the existing backend geocoder function:

```python
from fastapi import APIRouter, HTTPException
from ml.fastapi_ml_parser import MLAddressParser, ParseRequest
from your_existing_module import google_geocode

router = APIRouter()
parser = MLAddressParser(google_geocode)

@router.post('/parse_ml')
def parse_ml(req: ParseRequest):
    try:
        return parser.parse(req.address)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

app.include_router(router)
```

If the existing Google function is async or has a different signature, create a small wrapper rather than duplicating Google credentials/client logic.

## 4. Combine with `/parse`

Keep the original endpoint:

```text
POST /parse       → existing rule-based/raw geocoding behavior
POST /parse_ml    → ML extraction + cleaned geocoding, with raw fallback
```

In React, add a simple method selector. Send the same request body to either endpoint. The ML response contains `method`, `confidence`, `components`, `query`, and `geocode`, so the UI can show what happened.

A gradual rollout is recommended: compare both methods first, evaluate on a held-out real dataset, then make ML the default only if it improves the desired metrics.

## 5. Test `/parse_ml`

```bash
curl -X POST http://localhost:8000/parse_ml \
  -H "Content-Type: application/json" \
  -d '{"address":"H No 42, MG Road, Indirapuram, ke paas Shipra Mall, Ghaziabad, Uttar Pradesh 201014"}'
```

## Existing quick start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend defaults to `http://localhost:5173`; FastAPI runs at `http://localhost:8000`.

## Free-resource note

The training pipeline is designed for free Google Colab and Hugging Face resources. Google Geocoding itself is a separate service and can require billing/credits depending on the current Google Maps Platform account and pricing, so this project does not claim that Google API usage is always free.

## Production-data warning

Real addresses can contain sensitive location information. Only train/evaluate on addresses you are authorized to use; anonymize personal identifiers and keep a separate held-out test set. Synthetic performance should not be presented as production accuracy.

## License

MIT License.
