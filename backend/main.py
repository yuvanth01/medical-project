from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
import pytesseract
from PIL import Image
import io

# ----------------------------
# Create FastAPI app
# ----------------------------
app = FastAPI()

# ----------------------------
# Enable CORS (for React)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Configure Tesseract (Windows)
# ----------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ----------------------------
# Connect to MongoDB
# ----------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["medical_db"]
collection = db["medical_bills"]

# ----------------------------
# Upload Endpoint
# ----------------------------
@app.post("/upload-medical-bill/")
async def upload_medical_bill(file: UploadFile = File(...)):

    contents = await file.read()

    # Convert image
    image = Image.open(io.BytesIO(contents))
    image = image.convert("L")  # improve OCR accuracy

    # Extract text
    text = pytesseract.image_to_string(image, config="--psm 6")

    # Prepare data for MongoDB
    bill_data = {
        "filename": file.filename,
        "extracted_text": text,
        "uploaded_at": datetime.now()
    }

    # Insert into MongoDB
    result = collection.insert_one(bill_data)

    return {
        "message": "File processed and stored successfully",
        "id": str(result.inserted_id),
        "extracted_text": text
    }