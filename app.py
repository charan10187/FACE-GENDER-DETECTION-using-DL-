from flask import Flask, render_template, request, jsonify
import torch
from PIL import Image
from torchvision import transforms
from transformers import ViTForImageClassification
import os, requests

app = Flask(__name__)

# ✅ Check device (GPU or CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# ✅ Load Vision Transformer Model
MODEL_NAME = "nateraw/vit-age-classifier"
model = ViTForImageClassification.from_pretrained(MODEL_NAME)
model.to(device).eval()


# ✅ Image transformation
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# ✅ Image preprocessing
def preprocess_image(image):
    image = image.convert("RGB")
    return transform(image).unsqueeze(0).to(device)

# ✅ Prediction function
def predict_age_gender(image):
    img_tensor = preprocess_image(image)
    with torch.no_grad():
        outputs = model(img_tensor).logits
    age_pred = outputs[0, 0].item() * 100  # Scale as needed
    gender_pred = "Male" if outputs[0, 1].item() < 0.5 else "Female"
    return {"age": f"{age_pred:.2f}", "gender": gender_pred}

# ✅ Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    image = Image.open(file)
    result = predict_age_gender(image)
    return jsonify(result)

@app.route("/capture", methods=["POST"])
def capture():
    if "image" not in request.files:
        return jsonify({"error": "No image captured"}), 400
    
    file = request.files["image"]
    image = Image.open(file)
    result = predict_age_gender(image)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
