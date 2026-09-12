"""Real inference adapters.

The default YOLOv8n weights provide real vehicle detections. For pothole/road-damage
classes, set YOLO_WEIGHTS to a locally trained YOLO checkpoint produced from a
labeled road-defect dataset; the adapter never pretends the generic COCO model
recognizes potholes.
"""
from __future__ import annotations
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_yolo(weights: str | None = None):
    from ultralytics import YOLO
    selected = weights or os.getenv("YOLO_WEIGHTS", "yolov8n.pt")
    return YOLO(selected), selected


def detect_frame(model: Any, frame: Any, *, bus_id: str, route_id: str, latitude: float, longitude: float) -> dict[str, Any]:
    result = model(frame, verbose=False)[0]
    names = result.names
    detections = []
    vehicle_counts: dict[str, int] = {}
    for box in result.boxes:
        cls = int(box.cls[0])
        label = str(names[cls])
        confidence = float(box.conf[0])
        xyxy = [round(float(v), 2) for v in box.xyxy[0].tolist()]
        detections.append({"label": label, "confidence": round(confidence, 4), "bbox": xyxy})
        if label in {"car", "motorcycle", "bus", "truck", "bicycle"}:
            vehicle_counts[label] = vehicle_counts.get(label, 0) + 1
    timestamp = datetime.now(timezone.utc).isoformat()
    return {
        "eventId": f"det_{int(datetime.now().timestamp() * 1000)}",
        "busId": bus_id,
        "routeId": route_id,
        "eventType": "TRAFFIC_OBSERVATION",
        "confidence": max([d["confidence"] for d in detections], default=0.0),
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp,
        "severity": "MEDIUM" if sum(vehicle_counts.values()) > 15 else "LOW",
        "evidence": {"imageUrl": None, "videoUrl": None},
        "metadata": {
            "inferenceMode": "REAL_YOLOV8",
            "detector": "ultralytics-yolov8",
            "vehicleTypes": vehicle_counts,
            "vehicleCount": sum(vehicle_counts.values()),
            "detections": detections,
        },
    }


def read_plate(image_path: str) -> dict[str, Any]:
    """Run a real Tesseract OCR pass on an image supplied by the operator."""
    import cv2
    import pytesseract
    image = cv2.imread(str(Path(image_path)))
    if image is None:
        raise FileNotFoundError(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    text = pytesseract.image_to_string(gray, config="--psm 7").strip()
    cleaned = "".join(ch for ch in text.upper() if ch.isalnum())
    return {"plate": cleaned, "confidence": None, "inferenceMode": "REAL_TESSERACT_OCR", "sourceImage": str(image_path)}
