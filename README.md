# AddressAI 📍🇮🇳

> **Intelligent, Production-Ready Indian Address Parser & Geospatial Visualizer**

AddressAI transforms messy, unstructured Indian addresses (containing floor numbers, landmark references like "near ICICI bank", complex sublocalities, and 6-digit PIN codes) into clean, standardized structured components and renders exact pinpoint geolocations on an interactive map.

---

## 🌟 Features

- **Rule-Based & AI-Driven Address Extraction**:
  - House / Flat / Floor / Plot / Building Name extraction
  - Street / Road / Marg / Lane identification
  - **Landmark Extraction & Enhancement**: Captures "near...", "opp...", "behind...", "facing...", and integrates them directly into geolocation refinement.
  - Sublocality, Area, City, and State parsing (covers all 28 Indian States & 8 UTs + Major Cities).
  - 6-digit Indian PIN Code validation and postal circle matching.
- **Precision Confidence Meter**: Real-time calculated confidence gauge (0–100%) indicating component completeness and geolocation accuracy level (`ROOFTOP`, `RANGE_INTERPOLATED`, `GEOMETRIC_CENTER`, `APPROXIMATE`).
- **Interactive Leaflet Map**:
  - Custom neon pulsing geolocation marker
  - Layer switchers: **Cyber Dark**, **Voyager**, and **OSM Default**
  - Smooth fly-to camera animations on address change
- **Interactive 3D Three.js Background**: High-performance low-poly rotating holographic wireframe globe with glowing data constellation particles and mouse parallax.
- **Glassmorphism UI**: Built with Tailwind CSS, Framer Motion staggered animations, and responsive layouts.
- **JSON Inspector**: Formatted JSON response viewer with 1-click **Copy JSON**, **cURL Snippet**, and **Download .json** file.
- **Multi-Engine Geocoding Resilience**: Seamlessly integrates with Google Geocoding API (`GOOGLE_API_KEY`) and features an automatic fallback to OpenStreetMap (Nominatim) and Indian city heuristic databases.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS with Glassmorphism Design System (`#0f0c29` deep indigo / purple / pink gradient theme)
- **3D Canvas**: Three.js
- **Map & Geospatial**: Leaflet & React-Leaflet
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Celebrations**: Canvas-Confetti

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Server**: Uvicorn
- **HTTP Client**: HTTPX (Asynchronous)
- **Data Validation**: Pydantic v2
- **Config**: Python-Dotenv

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js (v18+ recommended)
- Python (3.10+ recommended)

### 1. Clone & Setup Backend

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Set your Google Maps Geocoding API Key
# Copy .env.example to .env
cp .env.example .env
# Edit .env and paste your GOOGLE_API_KEY
```

Run FastAPI Backend:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API will be live at `http://localhost:8000`  
Interactive Swagger Docs at `http://localhost:8000/docs`

---

### 2. Setup Frontend

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Run Vite dev server
npm run dev
```
Open your browser at `http://localhost:5173`.

---

### 3. One-Click Launcher (Windows)
Double-click `run_dev.bat` in the root folder to spin up both Backend and Frontend in separate windows simultaneously.

---

## 📖 API Documentation

### `POST /parse`
Parses an unstructured address string and returns structured components with coordinates.

#### Request Body
```json
{
  "address": "2nd floor, pink building, near ICICI bank, Rajouri Garden, Delhi 110027"
}
```

#### Response (200 OK)
```json
{
  "original_address": "2nd floor, pink building, near ICICI bank, Rajouri Garden, Delhi 110027",
  "structured_components": {
    "house_number": "2nd floor, pink building",
    "street": null,
    "landmark": "ICICI bank",
    "sublocality": null,
    "locality": "Rajouri Garden",
    "city": "Delhi",
    "state": "Delhi",
    "postal_code": "110027",
    "country": "India"
  },
  "coordinates": {
    "lat": 28.6475,
    "lng": 77.1215
  },
  "confidence_score": 0.94,
  "formatted_address": "2nd floor, pink building, Near ICICI bank, Rajouri Garden, Delhi, 110027, India",
  "landmark_detected": "ICICI bank",
  "provider": "google"
}
```

### `GET /health`
Returns backend health status and checks if the Google Geocoding API is configured.

```json
{
  "status": "healthy",
  "service": "AddressAI-Backend",
  "version": "1.0.0",
  "google_api_configured": true
}
```

---

## 🚢 Deployment Guide

### Deploying Frontend to Vercel
1. Connect your repository to [Vercel](https://vercel.com).
2. Set the Root Directory to `./frontend` or use the root with `vercel.json` included in this repository.
3. Configure environment variable (if your backend is hosted separately):
   - `VITE_API_BASE_URL` = `https://your-backend-domain.onrender.com`
4. Deploy!

### Deploying Backend to Render / Railway / Cloud Run
1. Create a new Web Service on [Render](https://render.com) or [Railway](https://railway.app).
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Environment Variables:
   - `GOOGLE_API_KEY`: *(Optional)* Your Google Geocoding API Key
   - `PORT`: `8000` (or leave default for platform)

A production-ready [backend/Dockerfile](backend/Dockerfile) is also included for containerized deployments.

---

## 🧪 Testing

### Automated Backend Test Script
Run:
```bash
py -c "import httpx, asyncio; async def t(): res = await httpx.AsyncClient().post('http://localhost:8000/parse', json={'address': '2nd floor, pink building, near ICICI bank, Rajouri Garden, Delhi 110027'}); print(res.json()); asyncio.run(t())"
```

---

## 📄 License
MIT License. Built for high-performance geospatial address resolution.
