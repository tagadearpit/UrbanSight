"""Fine-tune YOLOv8 on a YOLO-format road-defect dataset.

The dataset YAML and labels are intentionally supplied by the operator because
Kaggle dataset licenses and class names vary. This produces a custom checkpoint
that can be passed to run_dashcam.py with --weights.
"""
import argparse
from ultralytics import YOLO

parser=argparse.ArgumentParser()
parser.add_argument('--data',required=True,help='Path to dataset.yaml')
parser.add_argument('--epochs',type=int,default=20)
parser.add_argument('--imgsz',type=int,default=640)
parser.add_argument('--output',default='runs/road-defects')
a=parser.parse_args()
model=YOLO('yolov8n.pt')
model.train(data=a.data,epochs=a.epochs,imgsz=a.imgsz,project=a.output,name='yolov8n-road-defects')
print('Use runs/road-defects/yolov8n-road-defects/weights/best.pt with run_dashcam.py --weights')
