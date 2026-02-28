from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
from PIL import Image
from openai import OpenAI
import pytesseract
import io
import os
import json


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


client_db = MongoClient("mongodb://localhost:27017/")
db = client_db["medical_db"]
collection = db["medical_bills"]


client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_medical_summary(extracted_text):

    prompt = f"""
You are a medical assistant AI.

From the following medical bill text:

{extracted_text}

Extract and generate:

1. Patient Name
2. Age (if available)
3. Detailed explanation of health issue
4. Detailed explanation of medications and their purpose
5. Short medical summary
6. Preventive suggestions

Return strictly valid JSON in this format:

{{
  "patient_name": "",
  "age": "",
  "health_issue_detailed_explanation": "",
  "medication_detailed_explanation": "",
  "medical_summary": "",
  "preventive_suggestions": ""
}}
"""

    try:
        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a medical assistant AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        ai_text = response.choices[0].message.content

        try:
            return json.loads(ai_text)
        except:
            return {
                "error": "AI did not return valid JSON",
                "raw_response": ai_text
            }

    except Exception as e:
        return {"error": str(e)}


@app.post("/upload-medical-bill/")
async def upload_medical_bill(file: UploadFile = File(...)):

    try:
        contents = await file.read()

       
        image = Image.open(io.BytesIO(contents))
        image = image.convert("L")  # improve OCR accuracy

        
        extracted_text = pytesseract.image_to_string(image, config="--psm 6")

       
        ai_summary = generate_medical_summary(extracted_text)

       
        bill_data = {
            "filename": file.filename,
            "extracted_text": extracted_text,
            "ai_summary": ai_summary,
            "uploaded_at": datetime.now()
        }

        result = collection.insert_one(bill_data)

        return {
            "message": "File processed, AI summary generated and stored successfully",
            "id": str(result.inserted_id),
            "ai_summary": ai_summary
        }

    except Exception as e:
        return {"error": str(e)}