from ultralytics import YOLO
from waste_classifier import classify_waste

# Use the lightweight ONNX model
model = YOLO("best.onnx")


def detect_waste(image_path: str):
    results = model(image_path, imgsz=320)

    detections = []

    for result in results:
        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            class_name = result.names[class_id]

            waste_result = classify_waste(class_name)

            detections.append({
                "object": class_name,
                "confidence": round(confidence, 2),
                "category": waste_result["category"],
                "recommended_bin": waste_result["recommended_bin"]
            })

    return detections