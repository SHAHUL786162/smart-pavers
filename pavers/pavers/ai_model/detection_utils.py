import torch
import requests
import json
from PIL import Image, ExifTags

# --- Load your trained YOLOv5 model ---
model = torch.hub.load('yolov5', 'custom', path='ai_model/best.pt', source='local')
model.conf = 0.5

# --- Get GPS from image EXIF ---
def get_lat_lon_from_image(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        gps_info = {}

        for tag, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag)
            if tag_name == "GPSInfo":
                for key in value:
                    decode = ExifTags.GPSTAGS.get(key)
                    gps_info[decode] = value[key]

        def to_degrees(value):
            d, m, s = value
            return d[0]/d[1] + m[0]/m[1]/60 + s[0]/s[1]/3600

        lat = to_degrees(gps_info["GPSLatitude"])
        if gps_info["GPSLatitudeRef"] != "N":
            lat = -lat

        lon = to_degrees(gps_info["GPSLongitude"])
        if gps_info["GPSLongitudeRef"] != "E":
            lon = -lon

        return lat, lon
    except:
        print("❌ No EXIF GPS data found. Using default coordinates.")
        return 12.9721, 77.5933  # fallback location

# --- Run detection on an image ---
def detect_and_return_json(image_path):
    results = model(image_path)
    detections = []

    for *box, conf, cls in results.xyxy[0]:
        x1, y1, x2, y2 = [float(v) for v in box]
        confidence = float(conf)
        class_id = int(cls)
        class_name = model.names[class_id]

        detections.append({
            "class": class_name,
            "confidence": confidence,
            "bounding_box": {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2
            }
        })

    return detections

# --- Main: Run detection and send to backend ---
if _name_ == "_main_":
    image_path = "ai_model/test_image.jpg"  # replace with your image path
    detections = detect_and_return_json(image_path)

    if not detections:
        print("❌ No potholes detected.")
        exit()

    # Extract GPS from image EXIF
    latitude, longitude = get_lat_lon_from_image(image_path)

    # Send to backend
    backend_url = "http://localhost:5000/report"
    params = {
        "lat": latitude,
        "lon": longitude,
        "traffic_density": "high"  # optional
    }

    response = requests.post(backend_url, json=detections, params=params)

    print("✅ Backend Response:")
    print(response.status_code)
    print(response.json())