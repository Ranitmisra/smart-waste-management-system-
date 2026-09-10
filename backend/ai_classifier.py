import numpy as np
from PIL import Image
import onnxruntime as ort

from waste_classifier import classify_waste


# Load the lightweight ONNX model
session = ort.InferenceSession(
    "best.onnx",
    providers=["CPUExecutionProvider"]
)

input_name = session.get_inputs()[0].name

class_names = [
    "banana",
    "bottle",
    "paper",
    "cardboard",
    "battery",
    "mobile_phone"
]


def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)

    area1 = max(0, box1[2] - box1[0]) * max(0, box1[3] - box1[1])
    area2 = max(0, box2[2] - box2[0]) * max(0, box2[3] - box2[1])

    union = area1 + area2 - intersection

    if union == 0:
        return 0

    return intersection / union


def nms(boxes, scores, threshold=0.45):
    order = np.argsort(scores)[::-1]

    keep = []

    while len(order) > 0:
        current = order[0]
        keep.append(current)

        remaining = []

        for index in order[1:]:
            iou = calculate_iou(boxes[current], boxes[index])

            if iou < threshold:
                remaining.append(index)

        order = np.array(remaining)

    return keep


def detect_waste(image_path: str):

    image = Image.open(image_path).convert("RGB")

    original_width, original_height = image.size

    # Resize to the same size used during ONNX export
    image = image.resize((320, 320))

    image_array = np.array(image).astype(np.float32) / 255.0

    # HWC -> CHW
    image_array = np.transpose(image_array, (2, 0, 1))

    # Add batch dimension
    image_array = np.expand_dims(image_array, axis=0)

    # Run ONNX inference
    outputs = session.run(None, {
        input_name: image_array
    })

    predictions = outputs[0]

    # YOLO output is normally:
    # (1, 4 + number_of_classes, number_of_boxes)
    predictions = np.squeeze(predictions)

    if predictions.shape[0] < predictions.shape[1]:
        predictions = predictions.T

    boxes = []
    scores = []
    class_ids = []

    for prediction in predictions:

        x_center, y_center, width, height = prediction[:4]

        class_scores = prediction[4:]

        class_id = int(np.argmax(class_scores))
        confidence = float(class_scores[class_id])

        # Ignore weak detections
        if confidence < 0.25:
            continue

        # Convert center coordinates to corner coordinates
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2

        # Convert from 320x320 to original image size
        x1 *= original_width / 320
        x2 *= original_width / 320
        y1 *= original_height / 320
        y2 *= original_height / 320

        boxes.append([x1, y1, x2, y2])
        scores.append(confidence)
        class_ids.append(class_id)

    detections = []

    if not boxes:
        return detections

    # Remove duplicate boxes
    keep = nms(boxes, scores)

    for index in keep:

        class_id = class_ids[index]

        if class_id >= len(class_names):
            continue

        class_name = class_names[class_id]
        confidence = scores[index]

        waste_result = classify_waste(class_name)

        detections.append({
            "object": class_name,
            "confidence": round(confidence, 2),
            "category": waste_result["category"],
            "recommended_bin": waste_result["recommended_bin"]
        })

    return detections