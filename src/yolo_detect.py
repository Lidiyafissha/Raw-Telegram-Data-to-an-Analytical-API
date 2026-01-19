# src/yolo_detect.py

import os
from pathlib import Path
import cv2
from ultralytics import YOLO
import pandas as pd
from datetime import datetime

# ---------------------------
# CONFIGURATION
# ---------------------------

# Project root (to handle relative paths safely)
BASE_DIR = Path(__file__).resolve().parent.parent

# Folder containing scraped images
IMAGE_ROOT = BASE_DIR / "src" / "images"

# Folder to save YOLO results
OUTPUT_CSV = BASE_DIR / "data" / "processed" / "yolo_detections.csv"

# YOLO model and confidence threshold
MODEL_NAME = "yolov8n.pt"
CONF_THRESHOLD = 0.3

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def classify_image(detected_classes):
    """
    Rule-based classification based on detected objects
    """
    has_person = "person" in detected_classes
    has_product = any(obj in detected_classes for obj in ["bottle", "cup", "container"])

    if has_person and has_product:
        return "promotional"
    if has_product and not has_person:
        return "product_display"
    if has_person and not has_product:
        return "lifestyle"
    return "other"

def valid_image(path):
    """
    Safely check if image can be read
    """
    img = cv2.imread(str(path))
    return img is not None

# ---------------------------
# MAIN DETECTION LOGIC
# ---------------------------

def run_detection():
    # Check input folder
    if not IMAGE_ROOT.exists():
        raise FileNotFoundError(f"❌ Image folder not found: {IMAGE_ROOT}")
    print(f"📂 Looking for images in: {IMAGE_ROOT}")

    # Create output folder if missing
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # Find all JPG and PNG images recursively
    image_paths = list(IMAGE_ROOT.rglob("*.jpg")) + list(IMAGE_ROOT.rglob("*.png"))
    print(f"🔍 Found {len(image_paths)} images")

    if len(image_paths) == 0:
        print("⚠️ No images to process. Exiting.")
        return

    # Load YOLO model
    model = YOLO(MODEL_NAME)
    print("✅ YOLO model loaded")

    # Initialize records list
    records = []

    # Process each image
    for idx, img_path in enumerate(image_paths, start=1):
        if not valid_image(img_path):
            print(f"⚠️ Skipping unreadable image: {img_path}")
            continue

        try:
            results = model(str(img_path), conf=CONF_THRESHOLD, verbose=False)[0]

            detected_classes = []
            confidences = []

            if results.boxes is not None:
                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    cls_name = model.names[cls_id]

                    detected_classes.append(cls_name)
                    confidences.append(conf)

            image_category = classify_image(detected_classes)

            records.append({
                "image_name": img_path.name,
                "image_path": str(img_path),
                "detected_objects": ",".join(detected_classes),
                "avg_confidence": round(sum(confidences)/len(confidences), 3) if confidences else None,
                "image_category": image_category,
                "processed_at": datetime.utcnow().isoformat()
            })

            # Show progress
            print(f"[{idx}/{len(image_paths)}] ✅ Processed: {img_path.name} → {image_category}")

        except Exception as e:
            print(f"❌ Error processing {img_path}: {e}")

    # ---------------------------
    # SAVE TO CSV
    # ---------------------------
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n🌱 Detection complete. Results saved to {OUTPUT_CSV}")
    print(f"Total images processed: {len(records)}")

# ---------------------------
# ENTRY POINT
# ---------------------------

if __name__ == "__main__":
    run_detection()
