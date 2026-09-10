from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from waste_classifier import classify_waste
from ai_classifier import detect_waste

from database import SessionLocal, engine
from models import Base, WasteRecord, ImageRecord, SanitizationRecord

import os
import shutil

Base.metadata.create_all(bind=engine)

class DisposalRequest(BaseModel):
    waste_name: str
    location: str

class SanitizationRequest(BaseModel):
    location: str
    sanitization_type: str
    notes: str

app = FastAPI(
    title="Smart Waste Management System",
    description="Backend for waste segregation, disposal and sanitization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Smart Waste Management System API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "OK"
    }

@app.get("/classify")
def classify(waste: str):

    result = classify_waste(waste)

    return {
        "waste": waste,
        "result": result
    }

@app.post("/dispose")
def record_disposal(data: DisposalRequest):

    result = classify_waste(data.waste_name)

    db = SessionLocal()

    waste = WasteRecord(
        waste_name=data.waste_name,
        category=result["category"],
        bin_type=result["recommended_bin"],
        location=data.location,
        status="Pending Collection"
    )

    db.add(waste)
    db.commit()
    db.refresh(waste)

    db.close()

    return {
        "message": "Waste disposal recorded successfully",
        "id": waste.id,
        "waste": waste.waste_name,
        "category": waste.category,
        "bin": waste.bin_type,
        "location": waste.location,
        "status": waste.status
    }

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):

    upload_folder = "uploads"

    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run AI detection
    detections = detect_waste(file_path)

    db = SessionLocal()

    # Save image information
    image = ImageRecord(
        filename=file.filename,
        file_path=file_path,
        status="AI Analyzed"
    )

    db.add(image)
    db.flush()

    image_id = image.id

    # Save AI detections as waste records
    for detection in detections:

        waste = WasteRecord(
            waste_name=detection["object"],
            category=detection["category"],
            bin_type=detection["recommended_bin"],
            location="Image Upload",
            status="Pending Collection"
        )

        db.add(waste)

    db.commit()

    image_id = image.id
    image_filename = image.filename
    image_path = image.file_path
    image_status = image.status

    db.close()

    return {
    "message": "Image uploaded and analyzed successfully",
    "id": image_id,
    "filename": image_filename,
    "path": image_path,
    "status": image_status,
    "ai_detections": detections
}

@app.post("/sanitization")
def record_sanitization(data: SanitizationRequest):

    db = SessionLocal()

    sanitization = SanitizationRecord(
        location=data.location,
        sanitization_type=data.sanitization_type,
        status="Scheduled",
        notes=data.notes
    )

    db.add(sanitization)
    db.commit()
    db.refresh(sanitization)

    db.close()

    return {
        "message": "Sanitization recorded successfully",
        "id": sanitization.id,
        "location": sanitization.location,
        "sanitization_type": sanitization.sanitization_type,
        "status": sanitization.status,
        "notes": sanitization.notes
    }

@app.get("/dashboard-stats")
def dashboard_stats():

    db = SessionLocal()

    total_waste = db.query(WasteRecord).count()
    total_images = db.query(ImageRecord).count()
    total_sanitization = db.query(SanitizationRecord).count()

    pending_collection = db.query(WasteRecord).filter(
        WasteRecord.status == "Pending Collection"
    ).count()

    db.close()

    return {
        "total_waste": total_waste,
        "total_images": total_images,
        "total_sanitization": total_sanitization,
        "pending_collection": pending_collection
    }

@app.get("/recent-waste")
def recent_waste():

    db = SessionLocal()

    records = (
        db.query(WasteRecord)
        .order_by(WasteRecord.id.desc())
        .limit(10)
        .all()
    )

    result = []

    for waste in records:

        result.append({
            "id": waste.id,
            "waste_name": waste.waste_name,
            "category": waste.category,
            "bin": waste.bin_type,
            "location": waste.location,
            "status": waste.status
        })

    db.close()

    return result

@app.get("/dashboard-stats")
def dashboard_stats():

    db = SessionLocal()

    waste_count = db.query(WasteRecord).count()
    disposal_count = db.query(WasteRecord).count()
    sanitization_count = db.query(SanitizationRecord).count()

    db.close()

    return {
        "ai_detection": waste_count,
        "waste_segregation": waste_count,
        "disposal_tracking": disposal_count,
        "sanitization": sanitization_count
    }