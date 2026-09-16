from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
data = root / 'ai-service' / 'datasets' / 'road-defects' / 'data.yaml'
output = root / 'runs' / 'road-defects'
cmd = [sys.executable, str(root / 'ai-service' / 'train_road_defects.py'), '--data', str(data), '--epochs', '30', '--output', str(output)]
print('running:', ' '.join(cmd), flush=True)
result = subprocess.run(cmd, cwd=root)
if result.returncode:
    raise SystemExit(result.returncode)
best = output / 'yolov8n-road-defects' / 'weights' / 'best.pt'
target = root / 'ai-service' / 'models' / 'road-defects-yolov8n.pt'
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(best, target)
print(f'copied checkpoint: {target}', flush=True)
