from fastapi import FastAPI, File, UploadFile
from PIL import Image
import torch
from ultralytics import YOLO
from accelerate import Accelerator

app = FastAPI()
accelerator = Accelerator()

model = YOLO('yolov8n.pt')
model = accelerator.prepare(model)

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    image = Image.open(file.file).convert("RGB")

    results = model(image)

    predictions = []
    for result in results:
        for box in result.boxes:
            predictions.append({
                "class": int(box.cls),
                "confidence": float(box.conf),
                "bbox": [float(coord) for coord in box.xyxy[0]]
            })

    return {"predictions": predictions}
