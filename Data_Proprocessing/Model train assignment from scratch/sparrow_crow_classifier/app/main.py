from fastapi import FastAPI, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import io
from pathlib import Path

app = FastAPI()

# Setup directories
Path("app/static").mkdir(exist_ok=True)
Path("app/templates").mkdir(exist_ok=True)

# Setup templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Load model
model_path = "models/sparrow_crow_classifier.h5"
model = load_model(model_path)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    
    # Preprocess image
    img = image.load_img(io.BytesIO(contents), target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0
    
    # Predict
    prediction = model.predict(img_array)
    class_name = "crow" if prediction[0][0] > 0.5 else "sparrow"
    confidence = float(prediction[0][0] if class_name == "crow" else 1 - prediction[0][0])
    
    print("Hellow Danish")

    return {
        "class": class_name,
        "confidence": confidence
    }