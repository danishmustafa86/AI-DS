

# main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import torch
from torchvision import transforms, models
from PIL import Image
import io
import os

app = FastAPI()

# Load the model
model = models.resnet18(pretrained=False)
model.fc = torch.nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load("model/cat_dog_model.pth", map_location="cpu"))
model.eval()

# Class names from folder order
class_names = ['cats', 'dogs']

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor()
])

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        image = transform(image).unsqueeze(0)  # Add batch dimension
        with torch.no_grad():
            outputs = model(image)
            _, predicted = torch.max(outputs, 1)
            label = class_names[predicted.item()]
        return {"prediction": label}
    except Exception as e:
        return JSONResponse(status_code=500, content={"eror": str(e)})
