"""Run real YOLOv8 inference on a short dashcam clip and POST events to UrbanSight.

Example:
  python run_dashcam.py --video samples/bus_dashcam.mp4 --backend http://localhost:4173 \
      --bus BUS-042 --route R17 --lat 19.076 --lon 72.877

The runner is an adapter at the edge boundary. It sends compact detections and
vehicle counts, not raw video, to the backend. GPS can be replaced by a real
bus telemetry feed later.
"""
from __future__ import annotations
import argparse
import time
import requests
import cv2
from app.real_detectors import load_yolo, detect_frame

parser = argparse.ArgumentParser()
parser.add_argument("--video", required=True)
parser.add_argument("--backend", default="http://localhost:4173")
parser.add_argument("--bus", default="BUS-042")
parser.add_argument("--route", default="R17")
parser.add_argument("--lat", type=float, default=19.076)
parser.add_argument("--lon", type=float, default=72.877)
parser.add_argument("--weights", default=None)
parser.add_argument("--sample-every", type=int, default=5)
parser.add_argument("--dry-run", action="store_true", help="Run real inference and print events without POSTing")
args = parser.parse_args()
model, weights = load_yolo(args.weights)
cap = cv2.VideoCapture(args.video)
if not cap.isOpened():
    raise RuntimeError(f"Could not open video: {args.video}")
frame_no = 0
sent = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame_no += 1
    if frame_no % args.sample_every:
        continue
    event = detect_frame(model, frame, bus_id=args.bus, route_id=args.route, latitude=args.lat, longitude=args.lon)
    if args.dry_run:
        print({"eventType": event["eventType"], "confidence": event["confidence"], "vehicleCount": event["metadata"]["vehicleCount"], "detector": event["metadata"]["detector"]})
    else:
        response = requests.post(f"{args.backend}/api/events", json=event, timeout=15)
        response.raise_for_status()
    sent += 1
    print(f"frame={frame_no} mode={'dry-run' if args.dry_run else 'POST'} vehicles={event['metadata']['vehicleCount']} weights={weights}")
    time.sleep(0.02)
cap.release()
print(f"sent={sent} real YOLO events to {args.backend}")
