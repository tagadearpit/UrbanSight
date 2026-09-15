# UrbanSight implementation audit

Audit date: 2026-09-11. This document is intentionally honest about what was and was not executed in the current sandbox.

## What was fixed

The release now has a canonical PostGIS migration and seed path with all routes referenced by the seed, including R17–R24. Compose mounts the migration and seed directly instead of mounting a wrapper with invalid container-relative paths. The backend was replaced with a transactional implementation covering event validation, bus location persistence, traffic and incident processing, PostGIS `ST_DWithin` road-issue correlation, bounded confidence fusion, persisted severity reasons, WebSocket broadcasts, simulation controls, reports, search, structured errors, CORS, rate limiting, and maintenance transition validation.

The frontend now uses runtime-configurable API and WebSocket URLs, hydrates primary state from backend endpoints, shows loading/error states, updates from WebSocket messages, provides working map layer filters, search, report downloads, evidence responses, maintenance actions, speed controls, Settings and Profile views, and no longer contains toast-only action handlers. The simulator now supports deterministic all/road/traffic/incident scenarios and moving bus coordinates. Root package locking and a static production build script were added. Render and Vercel deployment metadata and environment documentation were added.

## Verification matrix

| Requested sequence | Result in this sandbox | Evidence or limitation |
|---|---|---|
| 1. Fresh database creation | **Not executed** | `psql` and PostgreSQL binaries are absent. Package installation was attempted but `apt-get update` timed out. |
| 2. PostgreSQL/PostGIS migration | **Not executed** | SQL files were reviewed and canonicalized, but no local PostGIS server was available. |
| 3. Database seed | **Not executed** | Seed was reviewed for foreign-key consistency and route coverage, but not run. |
| 4. Backend startup | **Verified** | Node backend starts without a database and serves the frontend; database-dependent routes return structured `DATABASE_NOT_CONFIGURED`. |
| 5. AI service startup | **Verified** | `uvicorn app.main:app --app-dir ai-service ...` started and `GET /health` returned HTTP 200. |
| 6. Frontend production build | **Verified** | `npm run build:frontend` completed and produced `dist/index.html`, `dist/app.js`, and `dist/frontend-config.js`. Production URL substitution was also tested. |
| 7. Simulator startup | **Verified** | Simulator started with `SCENARIO=all SPEED=2` and generated deterministic events. |
| 8. Simulator → POST `/api/events` | **Partially verified** | Simulator issued real POST requests; they returned structured HTTP 503 because the database was unavailable. |
| 9. Event → PostgreSQL | **Not executed** | Blocked by absent PostgreSQL. Backend transaction code is present. |
| 10. PostGIS issue correlation | **Not executed** | Blocked by absent PostGIS. Backend uses configurable `ST_DWithin`. |
| 11. WebSocket → frontend | **Partially verified** | WebSocket code and frontend connection were inspected; no database-backed event could be emitted in this sandbox. |
| 12. Map update | **Not executed end-to-end** | Leaflet rendering and layer handlers are present; live data was unavailable. |
| 13. KPI update | **Not executed end-to-end** | KPI values are sourced from `/api/dashboard`; database was unavailable. |
| 14. Second observation → same issue | **Not executed** | Requires PostGIS and a running database. |
| 15. Maintenance creation | **Not executed against PostgreSQL** | UI handler and backend POST route are implemented; database was unavailable. |
| 16. Maintenance persistence after refresh | **Not executed** | Requires database. |
| 17. Repair verification | **Not executed** | Legal transition chain is implemented, but persistence needs database verification. |
| 18. Analytics update | **Not executed against PostgreSQL** | Backend SQL and frontend hydration are implemented. |
| 19. Report generation | **Not executed against PostgreSQL** | Backend report route and JSON download action are implemented. |
| 20. Vercel frontend → Render backend API | **Not executed** | No deployed Vercel/Render URLs or credentials were supplied. Build-time URL injection was verified with an example URL. |
| 21. Vercel frontend → Render WebSocket | **Not executed** | No deployed Render WebSocket endpoint was supplied. Configurable `NEXT_PUBLIC_WS_URL` support was verified. |

## UI interaction audit

The landing page, Get started, Enter command centre, How it works, Capabilities, Impact, and Explore signal links were inspected in the browser. Dashboard navigation was exercised for Settings and Profile. The release source was also audited for `onclick` handlers: no remaining action is implemented as a toast-only handler. Controls now map to backend/API operations or actual client actions:

| Control family | Implemented operation |
|---|---|
| Start, Pause, Resume, Stop, Reset | `/api/simulation/*` and WebSocket simulation status |
| 1x, 2x, 5x, 10x | `/api/simulation/speed` |
| Map filters | Rebuild Leaflet layer selection from backend data |
| Search | `/api/search` |
| View issue/bus | Backend detail request |
| Create work order | `POST /api/maintenance` |
| Advance status | `PATCH /api/maintenance/:id` with legal-transition validation |
| View evidence | Evidence endpoint with explicit `DEMO_SIMULATION` response |
| Generate report/open report | `GET /api/reports/daily` and JSON download |
| Export summary/snapshot | Actual JSON file download |
| Notifications | Backend-loaded incident count or empty state |
| Settings/Profile | Dedicated views, including offline configuration/profile state |

Because the database was unavailable, data-dependent controls could not be completed successfully against real persisted records. They show structured errors rather than pretending success.

## Exact commands used

```bash
unzip -q /home/ubuntu/upload/UrbanSight-SIH26124-ai-complete.zip -d /home/ubuntu/urbansight-release
cd /home/ubuntu/urbansight-release/urbansight
npm install --package-lock-only --ignore-scripts
npm ci --ignore-scripts
npm run build:frontend
npm --prefix backend ci --ignore-scripts
npm --prefix edge-simulator ci --ignore-scripts
node --check app.js
node --check backend/src/server.js
node --check edge-simulator/src/index.js
node --check scripts/build-frontend.mjs
python3 -m py_compile ai-service/app/main.py ai-service/app/real_detectors.py ai-service/run_dashcam.py ai-service/run_anpr.py ai-service/train_road_defects.py ai-service/make_test_clip.py
PORT=4183 node backend/src/server.js
python3 -m uvicorn app.main:app --app-dir ai-service --host 127.0.0.1 --port 8000
BACKEND_URL=http://127.0.0.1:4183 SCENARIO=all SPEED=2 npm --prefix edge-simulator start
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:4183/health
curl -X POST http://127.0.0.1:4184/api/events -H 'content-type: application/json' -d '{}'
NEXT_PUBLIC_API_URL=https://api.example.invalid NEXT_PUBLIC_WS_URL=wss://api.example.invalid/ws DEMO_MODE=false npm run build:frontend
```

The attempted database prerequisite was:

```bash
sudo apt-get update -qq
sudo apt-get install -y -qq postgresql postgresql-contrib postgis postgresql-16-postgis-3
```

It could not complete because the package metadata refresh timed out in the sandbox. Therefore this audit does not claim the database-dependent sequence passed.

## Exact deployment environment variables

### Render Node backend

`DATABASE_URL`, `PORT`, `NODE_ENV=production`, `DEMO_MODE=false`, `JWT_SECRET`, `CORS_ORIGINS`, `FRONTEND_URL`, `WEBSOCKET_URL`, `AI_SERVICE_URL`, `ISSUE_RADIUS_METERS`, `OBJECT_STORAGE_ENDPOINT`, `OBJECT_STORAGE_ACCESS_KEY`, `OBJECT_STORAGE_SECRET_KEY`, and `OBJECT_STORAGE_BUCKET`.

### Render AI service

`PORT` and any model-service variables required by the selected inference deployment. The current FastAPI service does not require a secret for its health or simulation adapters.

### Vercel frontend build

`NEXT_PUBLIC_API_URL=https://<backend>.onrender.com`, `NEXT_PUBLIC_WS_URL=wss://<backend>.onrender.com/ws`, and `DEMO_MODE=false`. `MAP_TILE_URL` may be set if the tile provider is changed.

## Remaining limitations

The requested full end-to-end acceptance sequence is **not complete in this sandbox** because a real PostgreSQL/PostGIS service and deployed Vercel/Render environments were unavailable. The final ZIP should be treated as an improved, auditable release candidate, not as proof that steps 1–3, 9–21 have passed in production. The production authentication adapter is still an interface boundary rather than a complete JWT/OAuth issuer integration. Production object-storage upload/signing is documented but the local demo evidence adapter remains `demo://`.

## Judge-demo workflow update

The release now includes an integrated backend simulation sequence at the Start Simulation control. It defaults to 2x and immediately emits a persisted pothole event for BUS-042/R17, then a same-location pothole observation for BUS-031/R17, followed by traffic congestion, waterlogging, incident, and simulated ANPR events. The simulation snapshot exposes status, current bus, route, event count, and latest detection for the visible demo panel. The second pothole uses the same physical defect type and PostGIS radius so it is fused into one issue; confidence, observation count, supporting buses, severity, and reason are updated.

The frontend now includes a compact LIVE DEMO SIMULATION panel with Start, Pause, Resume, Stop, Reset, and 1x/2x/5x/10x controls. Selected issue details are displayed on Overview, Map, and Issues views. Search is now a non-blocking result panel instead of a browser prompt/alert. Notifications and evidence responses use the application toast surface. A persisted `/api/maintenance/:id/rescan` action verifies a resolved work order with an explicit `AI_RESCAN_SIMULATION` result, updates the maintenance and road-issue statuses to `REPAIR_VERIFIED`, and records an audit entry.

These paths are source- and syntax-verified. They still require a real PostgreSQL/PostGIS instance for full execution because the current sandbox does not provide one; the final audit therefore continues to distinguish implementation from end-to-end database proof.

## Final release-pass verification — 2026-09-12

The latest release pass corrected the Render Python service command to `uvicorn app.main:app --app-dir ai-service --host 0.0.0.0 --port $PORT` and corrected `vercel.json` to use `npm ci`, `npm run build`, and `dist` as the output directory. A production-style build was executed with `NEXT_PUBLIC_API_URL=https://urbansight-backend.onrender.com` and `NEXT_PUBLIC_WS_URL=wss://urbansight-backend.onrender.com/ws`; the generated configuration contained those HTTPS/WSS values and no localhost placeholders. The frontend now updates the existing bus marker directly for `BUS_LOCATION_UPDATED` instead of hydrating every dashboard endpoint.

Passed in this environment: ZIP integrity; root `npm ci`; `npm run build`; backend and simulator dependency installation; JavaScript syntax checks for frontend, backend, simulator, and build script; Python compilation checks for the AI service scripts; AI service startup and `/health` HTTP 200; static core-schema table identifier checks; seed route coverage checks for R17 and R24; and production URL injection checks.

Not verified because required external infrastructure is unavailable: empty PostgreSQL/PostGIS first boot, migrations and seed execution, database-backed event persistence, PostGIS correlation, database-backed WebSocket event flow, full maintenance persistence, and live Vercel/Render deployment connectivity. Docker, `psql`, `pg_isready`, Vercel CLI, Render CLI, and configured deployment connectors are unavailable in this session. No deployment is claimed without actual service credentials or a connected deployment project.

## Confirmed bug-fix pass — 2026-09-15

### Fixes applied

1. `ai-service/app/real_detectors.py`: real YOLO events no longer include `evidence.imageUrl: None` or `evidence.videoUrl: None`. The optional evidence object is omitted when no artifact exists, matching the backend Zod contract.
2. `backend/src/server.js`: the traffic trend query now uses explicit `AS hour` and `AS value` aliases.
3. Removed unused `backend/src/security.js` and `backend/src/db-client.js` because the backend did not import them and retained its own inline implementations.
4. `backend/src/server.js`: production authentication now verifies HS256 JWT signatures using `JWT_SECRET`, checks expiration, extracts `role` or `roles`, and enforces the route's required role list. Invalid or absent tokens return 401; valid tokens proceed to the database guard.

### Verification executed

Passed: JavaScript syntax checks for frontend, backend, simulator, and build script; Python compilation checks for all AI service scripts; real-detector payload regression with a fake YOLO result; regression checks for the evidence omission, traffic alias, JWT HMAC primitives, and role claim path; AI service startup with `/health` returning HTTP 200; production-mode backend without a database returning 401 for missing authentication and 401 for a malformed token; valid HS256 JWT reaching the database guard and returning the expected HTTP 503 `DATABASE_NOT_CONFIGURED`; `npm ci`; `npm run build`; and required `dist` artifact checks.

### Not executed

The requested live PostgreSQL/PostGIS sequence was not executed in this sandbox because `psql`, `pg_isready`, Docker, and PostgreSQL server binaries are unavailable. Therefore the following remain **NOT VERIFIED — requires live PostgreSQL/PostGIS**: migration, seed, `/health` with PostGIS version, `/api/traffic` against a real database, real YOLO HTTP 201 ingestion, simulator persistence, PostGIS correlation, and database-backed analytics. The supplied live-DB results were not available inside this session, so no live result is claimed.
