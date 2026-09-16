from pathlib import Path
import shutil
from ultralytics import YOLO

root = Path(__file__).resolve().parents[1]
run_dir = root / 'runs' / 'road-defects' / 'yolov8n-road-defects'
last = run_dir / 'weights' / 'last.pt'
if not last.exists():
    raise SystemExit(f'missing checkpoint: {last}')
model = YOLO(str(last))
model.train(resume=True)
best = run_dir / 'weights' / 'best.pt'
target = root / 'ai-service' / 'models' / 'road-defects-yolov8n.pt'
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(best, target)
print(f'copied checkpoint: {target}')
