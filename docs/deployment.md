# Deployment runbook

## Database

Create a managed PostgreSQL database with PostGIS enabled. Run the migration and seed exactly once for a new environment:

```bash
psql "$DATABASE_URL" -f database/migrations/001_initial.sql
psql "$DATABASE_URL" -f database/seed/demo.sql
```

Do not rely on the legacy `schema.sql` file for managed deployment unless the working directory is the repository root; it is a local convenience wrapper.

## Render Node backend

Use the repository root as the service root. Install with `npm ci` and start with `npm start`. Set:

```text
DATABASE_URL=<managed PostgreSQL/PostGIS URL>
PORT=10000
NODE_ENV=production
DEMO_MODE=false
JWT_SECRET=<server-side secret>
CORS_ORIGINS=https://<your-vercel-project>.vercel.app
FRONTEND_URL=https://<your-vercel-project>.vercel.app
WEBSOCKET_URL=wss://<your-render-service>.onrender.com/ws
AI_SERVICE_URL=https://<your-ai-service>.onrender.com
ISSUE_RADIUS_METERS=35
OBJECT_STORAGE_ENDPOINT=<S3-compatible endpoint>
OBJECT_STORAGE_ACCESS_KEY=<server-side key>
OBJECT_STORAGE_SECRET_KEY=<server-side secret>
OBJECT_STORAGE_BUCKET=urbansight-evidence
```

The Render health check is `/health`. The backend must be exposed over HTTPS so the separately deployed frontend can use `wss://`.

## Render Python AI service

Use the repository root as the service root. Install with `pip install -r ai-service/requirements.txt` and start with:

```bash
uvicorn app.main:app --app-dir ai-service --host 0.0.0.0 --port $PORT
```

The service health check is `/health`. The HTTP simulation adapters are explicitly labeled in responses. Real YOLO and Tesseract adapters remain available through the command-line programs and should be moved into a worker service for a production inference queue.

## Vercel static frontend

Build the static directory with:

```bash
NEXT_PUBLIC_API_URL=https://<your-render-service>.onrender.com \
NEXT_PUBLIC_WS_URL=wss://<your-render-service>.onrender.com/ws \
DEMO_MODE=false npm run build:frontend
```

The repository `vercel.json` uses `npm ci`, `npm run build`, and `dist` as the output directory. The build embeds these values into `dist/frontend-config.js`; no backend URL is hardcoded in the application controller.

## CORS and WebSocket requirements

Set `CORS_ORIGINS` to the exact Vercel origin, including protocol and without a trailing slash. Add a separate preview origin only when needed. Never use `*` in production. Confirm that the Render reverse proxy allows WebSocket upgrades on `/ws`.

## Evidence storage

Local demo evidence uses `demo://` identifiers and is displayed as `DEMO SIMULATION`. Production deployments must replace these with S3-compatible object URLs and add signed upload/download handling before accepting real imagery or video.
