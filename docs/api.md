# UrbanSight API

All event ingestion is validated server-side. The demo backend exposes `GET /health`, `GET /api/dashboard`, `GET /api/road-issues`, `GET /api/road-issues/:id`, `GET /api/buses`, `GET /api/incidents`, `GET /api/traffic`, `GET /api/analytics/*`, `GET /api/reports/daily`, and `POST /api/events`.

Simulation controls are `POST /api/simulation/start`, `/pause`, `/resume`, `/stop`, and `/reset`. The backend emits JSON WebSocket messages at `/ws`: `NEW_ROAD_ISSUE`, `ROAD_ISSUE_UPDATED`, `BUS_LOCATION_UPDATED`, `TRAFFIC_UPDATED`, `MAINTENANCE_UPDATED`, and `SIMULATION_STATUS`.

The real AI adapter `ai-service/run_dashcam.py` posts YOLOv8 vehicle/road-frame events to `POST /api/events`. `ai-service/run_anpr.py` runs local Tesseract OCR on a supplied image; it does not use a fixed plate string. `POST /api/assistant` accepts `{ "question": "..." }`, queries PostgreSQL/PostGIS, and optionally asks Gemini for a concise answer. Configure the Gemini key only in the backend environment variable `rasta_api`.

Event ingestion and maintenance create/update routes are protected by server-side role middleware and rate limiting. The current development adapter authenticates as `TRANSPORT_AUTHORITY`; replace it with JWT/OAuth verification before production deployment. Simulated data is explicitly labeled.
