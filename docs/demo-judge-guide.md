# UrbanSight demo and judge guide

## Lead with the strongest complete loop

Start the edge simulator, show a bus event entering `POST /api/events`, watch the backend spatially correlate repeated observations in PostgreSQL/PostGIS, and show the WebSocket issue update on the map. Create a work order, move it through maintenance status, and show the persisted state in the maintenance API. This is the complete **detection → correlation → decision → maintenance** loop.

Then switch to the focused AI deep dive. Run `ai-service/run_dashcam.py` against a short dashcam clip. The runner uses real Ultralytics YOLOv8 inference and posts vehicle detections and counts into the same event contract. Run `ai-service/run_anpr.py --image <plate-image>` to demonstrate a real Tesseract OCR pass. These are deliberately scoped adapters; the simulator remains the only simulated edge source.

The included smoke fixtures demonstrate the adapters without a backend: `ai-service/samples/bus_dashcam_clip.mp4` produced two real YOLOv8n events with one detected bus per sampled frame at confidences **0.8767** and **0.8731**. `ai-service/samples/plate_poc.png` produced `MH12AB1234` through real Tesseract OCR and returned `REAL_TESSERACT_OCR`. These are proof-of-concept measurements on the sandbox, not production accuracy or embedded-device FPS benchmarks.

## Honest scope statement

“UrbanSight's fusion engine, PostgreSQL/PostGIS persistence, REST APIs, WebSocket updates, maintenance workflow and dashboard are live. The detector proof-of-concept runs real YOLOv8 inference on footage, and the ANPR proof-of-concept runs real Tesseract OCR. The deterministic simulator is provided for repeatable SIH demonstrations. Production pothole accuracy requires a domain-trained checkpoint and validation set; the generic COCO YOLOv8n checkpoint is used for real vehicle detection unless `YOLO_WEIGHTS` points to a road-defect checkpoint.”

## Direct answers

**What model and accuracy/FPS?** The proof-of-concept uses Ultralytics YOLOv8n weights or a configured custom checkpoint. Do not claim pothole accuracy for generic COCO weights. Report measured FPS on the target hardware and validation mAP for the custom checkpoint; this repository does not invent those benchmarks.

**How do you control false positives?** Each detection is geotagged and time-stamped. Nearby compatible detections are fused with a PostGIS spatial query. Independent bus observations increase confidence through `1 - (1-c1)(1-c2)...`; repeated observations also raise the severity decision. Operators retain the evidence trail.

**What is the bandwidth budget?** The edge uploads compact event metadata and optional cropped evidence, not continuous raw video. See `docs/edge-bandwidth.md` for an illustrative 99.7% reduction estimate and its assumptions.

**Is the ANPR result real?** The CLI uses local Tesseract OCR on the supplied image. It returns the OCR output; it does not hardcode a plate. The output is labeled `REAL_TESSERACT_OCR` and should be evaluated as a proof of concept.

**What is simulated?** Only `edge-simulator/` and its deterministic scenario events. Mock AI endpoints in `ai-service/app/main.py` are explicitly labeled simulation adapters and are not presented as production inference.

## Optional assistant

`POST /api/assistant` accepts a natural-language authority question, queries PostgreSQL for road issues, traffic, incidents and overdue maintenance, and sends only that structured context to Gemini. Set the backend environment variable `rasta_api` to enable it. It is an analytics interface, not the primary product and not a generic chatbot.
