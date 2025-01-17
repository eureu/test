from fastapi import FastAPI, File, UploadFile
from PIL import Image
import torch
from torchvision import transforms
from transformers import AutoImageProcessor, AutoModelForImageClassification
from accelerate import Accelerator

app = FastAPI()
accelerator = Accelerator()

model_name = "nateraw/mobilenetv2-imagenet"
processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)
model.eval()

model = accelerator.prepare(model)

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    image = Image.open(file.file).convert("RGB")
    image = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image)
        predictions = torch.softmax(outputs.logits, dim=-1)
        top_pred = predictions.argmax(-1).item()

    return {"prediction": int(top_pred)}
