# Edge processing and bandwidth budget

```mermaid
flowchart LR
  A[Bus camera + GPS] --> B[Edge YOLO / OCR / tracker]
  B --> C[Crop + metadata + confidence]
  C --> D[POST /api/events]
  D --> E[PostgreSQL/PostGIS]
  E --> F[WebSocket dashboard]
```

The bus-side adapter reads frames, runs inference locally, and uploads only an event payload: event ID, bus and route, GPS, timestamp, class/confidence, bounding boxes, and an optional cropped evidence image. It does **not** upload continuous raw video in the normal path. A production deployment can retain raw video locally for a short evidence window and upload it only after an operator-approved incident.

For a transparent estimate, a 1080p H.264 stream at 2 Mbps is approximately 900 MB per hour. If the edge samples one frame per second and emits a compact JSON event only when a vehicle/road event is detected, a 1 KB metadata payload for 10 events per minute is approximately 0.6 MB per hour; adding 30 cropped 80 KB evidence images per hour is approximately 2.4 MB per hour. That is roughly **99.7% lower than continuous video** in this illustrative workload. Actual savings vary with scene density, image quality, evidence retention, and detector threshold.

These numbers are estimates for architecture discussion, not measured embedded-hardware benchmarks. The repository's `ai-service/run_dashcam.py` demonstrates the real detector-to-event boundary.
