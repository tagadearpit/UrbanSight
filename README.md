# UrbanSight — SIH26124

UrbanSight turns public-transport buses into mobile urban-sensing units and presents geotagged road, traffic, incident, and maintenance intelligence to municipal teams.

## Architecture

```text
Edge simulator or real AI adapter → POST /api/events → Node API
→ PostgreSQL/PostGIS transaction → WebSocket → frontend dashboard
```

The database is the source of truth. The frontend hydrates from REST endpoints and applies WebSocket updates. The edge simulator is deterministic and explicitly labeled simulation. `ai-service/run_dashcam.py` performs real YOLOv8 vehicle inference; `run_anpr.py` performs real local Tesseract OCR. The generic bundled YOLO weights do not claim pothole accuracy.

## Local setup from an empty database

Requirements: Node.js 20+, Python 3.11+, PostgreSQL 14+, and PostGIS 3+.

```bash
createdb urbansight
export DATABASE_URL=postgresql://localhost:5432/urbansight
psql "$DATABASE_URL" -f database/migrations/001_initial.sql
psql "$DATABASE_URL" -f database/seed/demo.sql
npm ci
npm run build:frontend
PORT=4173 CORS_ORIGINS=http://localhost:4173 npm start
```

The canonical database process is always **migration first, seed second**. `schema.sql` is a convenience entry point for `psql` and delegates to the same files.

In another terminal:

```bash
npm --prefix edge-simulator ci
BACKEND_URL=http://localhost:4173 SCENARIO=all SPEED=2 npm --prefix edge-simulator start
```

The simulator sends road defects, traffic congestion, incidents, simulated ANPR, bus locations, and evidence metadata. It does not upload raw video.

## AI service

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r ai-service/requirements.txt
uvicorn app.main:app --app-dir ai-service --host 0.0.0.0 --port 8000
```

The FastAPI service clearly labels its HTTP simulation adapters. Real adapters are command-line programs:

```bash
python ai-service/run_dashcam.py --video ai-service/samples/bus_dashcam_clip.mp4 --backend http://localhost:4173 --bus BUS-042 --route R17 --lat 19.076 --lon 72.877 --dry-run
python ai-service/run_anpr.py --image ai-service/samples/plate_poc.png
```

Road-defect inference defaults to the committed `ai-service/models/road-defects-yolov8n.pt` checkpoint, trained on the public CC0 Kaggle Potholes-Detection-YOLOv8 dataset. It contains one `pothole` class. The 30-epoch validation run reported precision 0.799, recall 0.683, mAP50 0.774, and mAP50-95 0.510. These are hackathon-scale CPU results, not production accuracy claims. Override with `--weights` when evaluating another checkpoint.

## Frontend deployment

The static frontend supports same-origin local development and separate Vercel/Render deployment. Build it with:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com \
NEXT_PUBLIC_WS_URL=wss://your-backend.onrender.com/ws \
DEMO_MODE=false npm run build:frontend
```

Deploy the resulting `dist/` directory to Vercel. The backend must allow the exact Vercel origin through `CORS_ORIGINS`.

## Backend API

Important endpoints include:

- `GET /health`
- `GET /api/dashboard`
- `GET /api/road-issues` and `GET /api/road-issues/:id`
- `GET /api/buses` and `GET /api/buses/:id`
- `GET /api/incidents`
- `GET /api/traffic`
- `GET /api/analytics`
- `GET /api/maintenance`
- `POST /api/events`
- `POST /api/maintenance`
- `PATCH /api/maintenance/:id`
- `GET /api/reports/daily`
- `GET /api/search?q=...`
- `POST /api/simulation/start|pause|resume|stop|reset|speed`
- WebSocket `/ws`

Road issue matching uses configurable PostGIS `ST_DWithin`; configure `ISSUE_RADIUS_METERS`. Confidence uses bounded independent-observation fusion: `1 - (1 - prior) * (1 - observation)`, capped below 1.0. Maintenance transitions are validated and timestamped.

## Environment variables

Copy `.env.example` to the backend environment. Never commit real credentials.

- `DATABASE_URL`
- `PORT`
- `NODE_ENV`
- `DEMO_MODE`
- `JWT_SECRET`
- `CORS_ORIGINS`
- `FRONTEND_URL`
- `AI_SERVICE_URL`
- `OBJECT_STORAGE_ENDPOINT`
- `OBJECT_STORAGE_ACCESS_KEY`
- `OBJECT_STORAGE_SECRET_KEY`
- `OBJECT_STORAGE_BUCKET`
- `WEBSOCKET_URL`
- `ISSUE_RADIUS_METERS`
- `NEXT_PUBLIC_API_URL` for the frontend build
- `NEXT_PUBLIC_WS_URL` for the frontend build
- `MAP_TILE_URL` if a different tile provider is used

## Release verification

The implementation audit is maintained in `docs/implementation-audit.md`. It distinguishes checks executed locally from Vercel/Render checks that require deployed URLs and credentials.
