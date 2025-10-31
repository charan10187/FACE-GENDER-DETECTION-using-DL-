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
MODEL_NAME = "google/vit-small-patch16-224-in21k"

def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            response = session.get(URL, params={'id': file_id, 'confirm': value}, stream=True)
            break

    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

model_path = "vit_utkface2.pth"
if not os.path.exists(model_path):
    print("⬇️ Downloading model from Google Drive...")
    file_id = "1vqddsGZ6B4O4bmoHo6ETujq8phPfOrkC" #Google Drive file ID
    download_file_from_google_drive(file_id, model_path)
    print("✅ Model download complete.")

model = ViTForImageClassification.from_pretrained(MODEL_NAME, num_labels=2)
model.load_state_dict(torch.load(model_path, map_location=device))
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
