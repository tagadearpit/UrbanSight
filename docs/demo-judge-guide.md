# UrbanSight demo and judge guide

## Lead with the strongest complete loop

Start the edge simulator, show a bus event entering `POST /api/events`, watch the backend spatially correlate repeated observations in PostgreSQL/PostGIS, and show the WebSocket issue update on the map. Create a work order, move it through maintenance status, and show the persisted state in the maintenance API. This is the complete **detection → correlation → decision → maintenance** loop.

Then switch to the focused AI deep dive. Run `ai-service/run_dashcam.py` against a short dashcam clip or a validation image from `ai-service/datasets/road-defects/`. The runner uses a custom Ultralytics YOLOv8n checkpoint trained for potholes and maps the highest-confidence `pothole` detection to the backend-compatible `POTHOLE` event type. Vehicle-only frames retain the `TRAFFIC_OBSERVATION` path. Run `ai-service/run_anpr.py --image <plate-image>` to demonstrate a real Tesseract OCR pass. These are deliberately scoped adapters; the simulator remains the only simulated edge source.

The included road-defect training run used the public CC0 Kaggle `Potholes-Detection-YOLOv8` dataset: 1,581 training images, 396 validation images, and one class, `pothole`. After 30 epochs, the final validation metrics were **precision 0.799**, **recall 0.683**, **mAP50 0.774**, and **mAP50-95 0.510** across 395 validation images and 1,394 instances. A real validation image emitted a `POTHOLE` event with confidence **0.731**. These are small hackathon-scale proof-of-concept measurements on CPU, not production accuracy or embedded-device FPS benchmarks.

## Honest scope statement

“UrbanSight's fusion engine, PostgreSQL/PostGIS persistence, REST APIs, WebSocket updates, maintenance workflow and dashboard are live. The detector proof-of-concept runs a custom road-defect YOLOv8n checkpoint on footage and maps potholes to `POTHOLE` events; vehicle-only frames retain traffic observation behavior. The ANPR proof-of-concept runs real Tesseract OCR. The deterministic simulator is provided for repeatable SIH demonstrations. The reported pothole metrics are hackathon-scale validation results, not production accuracy.”

## Direct answers

**What model and accuracy/FPS?** The default proof-of-concept checkpoint is `ai-service/models/road-defects-yolov8n.pt`, trained for 30 epochs on the public one-class pothole dataset. Validation results were precision 0.799, recall 0.683, mAP50 0.774, and mAP50-95 0.510. No production FPS claim is made; the training and validation run used CPU in the sandbox.

**How do you control false positives?** Each detection is geotagged and time-stamped. Nearby compatible detections are fused with a PostGIS spatial query. Independent bus observations increase confidence through `1 - (1-c1)(1-c2)...`; repeated observations also raise the severity decision. Operators retain the evidence trail.

**What is the bandwidth budget?** The edge uploads compact event metadata and optional cropped evidence, not continuous raw video. See `docs/edge-bandwidth.md` for an illustrative 99.7% reduction estimate and its assumptions.

**Is the ANPR result real?** The CLI uses local Tesseract OCR on the supplied image. It returns the OCR output; it does not hardcode a plate. The output is labeled `REAL_TESSERACT_OCR` and should be evaluated as a proof of concept.

**What is simulated?** Only `edge-simulator/` and its deterministic scenario events. Mock AI endpoints in `ai-service/app/main.py` are explicitly labeled simulation adapters and are not presented as production inference.

## Optional assistant

`POST /api/assistant` accepts a natural-language authority question, queries PostgreSQL for road issues, traffic, incidents and overdue maintenance, and sends only that structured context to Gemini. Set the backend environment variable `rasta_api` to enable it. It is an analytics interface, not the primary product and not a generic chatbot.
