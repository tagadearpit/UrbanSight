from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .real_detectors import read_plate

app=FastAPI(title='UrbanSight AI Service',version='0.2.0')
class Frame(BaseModel):
    image_url:str|None=None
    image_path:str|None=None
    metadata:dict[str,Any]={}
class Event(BaseModel):
    event_type:str
    confidence:float=Field(ge=0,le=1)
    metadata:dict[str,Any]={}

def simulation_adapter(label:str,frame:Frame):
    return {'mode':'SIMULATION_ADAPTER','detector':label,'events':[],'message':'No production model is installed for this endpoint; use run_dashcam.py for real YOLO inference.'}

@app.get('/health')
def health(): return {'ok':True,'service':'ai-service','realAdapters':['YOLOv8','Tesseract OCR']}

@app.post('/inference/detect')
def detect(frame:Frame): return simulation_adapter('mock-road-detector',frame)

@app.post('/inference/track')
def track(frame:Frame): return simulation_adapter('mock-object-tracker',frame)

@app.post('/inference/anpr')
def anpr(frame:Frame):
    if not frame.image_path:
        raise HTTPException(400,'image_path is required for the real Tesseract ANPR proof of concept')
    try: return read_plate(frame.image_path)
    except FileNotFoundError: raise HTTPException(404,'image_path not found')

@app.post('/inference/traffic')
def traffic(frame:Frame): return simulation_adapter('mock-traffic-detector',frame)
