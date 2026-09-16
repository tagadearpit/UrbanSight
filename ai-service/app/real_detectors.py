"""Real YOLO and Tesseract inference adapters for UrbanSight edge events."""
from __future__ import annotations
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFECT_EVENT_TYPES = {
    "pothole": "POTHOLE",
    "potholes": "POTHOLE",
    "road_damage": "ROAD_DAMAGE",
    "road damage": "ROAD_DAMAGE",
    "waterlogging": "WATERLOGGING",
    "water_logging": "WATERLOGGING",
    "missing_infrastructure": "MISSING_INFRASTRUCTURE",
    "missing infrastructure": "MISSING_INFRASTRUCTURE",
    "missing_signage": "MISSING_INFRASTRUCTURE",
    "missing signage": "MISSING_INFRASTRUCTURE",
    "pedestrian_risk": "PEDESTRIAN_RISK",
    "pedestrian risk": "PEDESTRIAN_RISK",
}
VEHICLE_LABELS = {"car", "motorcycle", "bus", "truck", "bicycle"}


def load_yolo(weights: str | None = None):
    from ultralytics import YOLO
    default = Path(__file__).resolve().parents[1] / "models" / "road-defects-yolov8n.pt"
    selected = weights or os.getenv("YOLO_WEIGHTS", str(default))
    return YOLO(selected), selected


def _label_name(names: Any, cls: int) -> str:
    return str(names[cls] if isinstance(names, (dict, list, tuple)) else cls).strip()


def detect_frame(model: Any, frame: Any, *, bus_id: str, route_id: str, latitude: float, longitude: float) -> dict[str, Any]:
    result = model(frame, verbose=False)[0]
    names = result.names
    detections = []
    vehicle_counts: dict[str, int] = {}
    defect_candidates: list[tuple[float, str]] = []
    for box in result.boxes:
        cls = int(box.cls[0])
        label = _label_name(names, cls)
        normalized = label.lower().replace("-", "_").strip()
        confidence = float(box.conf[0])
        xyxy = [round(float(v), 2) for v in box.xyxy[0].tolist()]
        detections.append({"label": label, "confidence": round(confidence, 4), "bbox": xyxy})
        if normalized in VEHICLE_LABELS:
            vehicle_counts[normalized] = vehicle_counts.get(normalized, 0) + 1
        if normalized in DEFECT_EVENT_TYPES:
            defect_candidates.append((confidence, DEFECT_EVENT_TYPES[normalized]))

    defect_confidence, defect_event_type = max(defect_candidates, default=(None, None))
    is_defect = defect_event_type is not None
    event_type = defect_event_type if is_defect else "TRAFFIC_OBSERVATION"
    event_confidence = defect_confidence if is_defect else max((d["confidence"] for d in detections), default=0.0)
    vehicle_count = sum(vehicle_counts.values())
    timestamp = datetime.now(timezone.utc).isoformat()
    event: dict[str, Any] = {
        "eventId": f"det_{int(datetime.now().timestamp() * 1000)}",
        "busId": bus_id,
        "routeId": route_id,
        "eventType": event_type,
        "confidence": round(float(event_confidence), 4),
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp,
        "severity": "HIGH" if is_defect and float(event_confidence) >= 0.85 else ("MEDIUM" if vehicle_count > 15 else "LOW"),
        "metadata": {
            "inferenceMode": "REAL_YOLOV8_ROAD_DEFECTS" if is_defect else "REAL_YOLOV8",
            "detector": "ultralytics-yolov8n-road-defects",
            "vehicleTypes": vehicle_counts,
            "vehicleCount": vehicle_count,
            "detections": detections,
        },
    }
    if image_url := os.getenv("URBANSIGHT_EVIDENCE_IMAGE_URL"):
        event["evidence"] = {"imageUrl": image_url}
    elif video_url := os.getenv("URBANSIGHT_EVIDENCE_VIDEO_URL"):
        event["evidence"] = {"videoUrl": video_url}
    return event


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
