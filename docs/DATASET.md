# Road-defect dataset

UrbanSight's road-defect detector was trained with the public [Potholes-Detection-YOLOv8 dataset on Kaggle](https://www.kaggle.com/datasets/anggadwisunarto/potholes-detection-yolov8), reported by its publisher as **CC0 / Public Domain**. The source contains 1,581 training images, 396 validation images, YOLO-format bounding-box labels, and one class: `pothole`.

The raw images and labels are intentionally **not shipped in this repository**. Download the dataset from Kaggle and place it at `ai-service/datasets/road-defects/` with `train/images`, `train/labels`, `valid/images`, `valid/labels`, and `data.yaml` before retraining.

The trained checkpoint remains tracked at `ai-service/models/road-defects-yolov8n.pt`. The recorded 30-epoch validation results were precision **0.799**, recall **0.683**, mAP50 **0.774**, and mAP50-95 **0.510**. These are hackathon-scale results, not production accuracy claims.

To retrain after downloading the dataset:

```bash
python3 scripts/train-road-defects-release.py
```

The training helper expects the portable repository-relative paths in `ai-service/datasets/road-defects/data.yaml` and copies the resulting best checkpoint into `ai-service/models/road-defects-yolov8n.pt`.
