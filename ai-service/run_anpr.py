"""Real ANPR proof of concept. This uses local Tesseract OCR; no plate string is hardcoded."""
import argparse
import json
from app.real_detectors import read_plate

parser=argparse.ArgumentParser()
parser.add_argument('--image',required=True,help='Path to a sample plate image')
args=parser.parse_args()
print(json.dumps(read_plate(args.image),indent=2))
