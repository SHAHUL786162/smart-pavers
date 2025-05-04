from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import datetime
import smtplib
from email.mime.text import MIMEText
import torch
import cv2
import numpy as np
import os

# --- App and DB Setup ---
app = Flask(__name__)  # ✅ FIXED HERE
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Load YOLOv5 Model ---
model = torch.hub.load(
    os.path.abspath("yolov5"), 'custom',
    path=os.path.abspath("ai_model/best.pt"),
    source='local', force_reload=True
)
model.conf = 0.5

# --- Email Config ---
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'your-email@gmail.com'
EMAIL_PASSWORD = 'your-app-password'  # Use app password, NOT your actual password

# --- Database Model ---
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100))
    severity = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    timestamp = db.Column(db.String(100))
    traffic_density = db.Column(db.String(50))
    priority = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "severity": self.severity,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp,
            "traffic_density": self.traffic_density,
            "priority": self.priority
        }

# --- Traffic Zones (Hardcoded)
high_traffic_zones = [
    {"min_lat": 12.9700, "max_lat": 12.9800, "min_lon": 77.5900, "max_lon": 77.6000},
    {"min_lat": 12.9900, "max_lat": 13.0000, "min_lon": 77.5800, "max_lon": 77.5900},
]

# --- Utilities ---
def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = 'authority-email@example.com'
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent.")
    except Exception as e:
        print("❌ Email error:", e)

def get_exif_data(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            tagname = TAGS.get(tag, tag)
            if tagname == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_tag = GPSTAGS.get(t, t)
                    gps_data[sub_tag] = value[t]
                exif_data["GPSInfo"] = gps_data
    return exif_data

def get_lat_lon(exif_data):
    if "GPSInfo" not in exif_data:
        return None, None
    gps_info = exif_data["GPSInfo"]

    def convert_to_degrees(value):
        d, m, s = value
        return d[0]/d[1] + m[0]/m[1]/60 + s[0]/s[1]/3600

    lat = convert_to_degrees(gps_info["GPSLatitude"])
    lon = convert_to_degrees(gps_info["GPSLongitude"])
    if gps_info.get("GPSLatitudeRef") != "N":
        lat = -lat
    if gps_info.get("GPSLongitudeRef") != "E":
        lon = -lon
    return lat, lon

def calculate_priority(severity, traffic_density):
    severity_score = {"minor": 1, "moderate": 2, "severe": 3}
    traffic_score = {"low": 1, "medium": 2, "high": 3}
    return severity_score.get(severity.lower(), 1) + traffic_score.get(traffic_density.lower(), 1)

def estimate_traffic_density(lat, lon):
    for zone in high_traffic_zones:
        if zone['min_lat'] <= lat <= zone['max_lat'] and zone['min_lon'] <= lon <= zone['max_lon']:
            return "high"
    return "low"

def analyze_detections(detections):
    total_area = 0
    total_conf = 0
    count = len(detections)
    if count == 0:
        return {"average_confidence": 0, "average_area": 0, "severity": "none"}
    for det in detections:
        box = det["bounding_box"]
        width = box["x2"] - box["x1"]
        height = box["y2"] - box["y1"]
        area = width * height
        total_area += area
        total_conf += det["confidence"]
    avg_area = total_area / count
    avg_conf = total_conf / count
    if avg_area > 50000:
        severity = "severe"
    elif avg_area > 20000:
        severity = "moderate"
    else:
        severity = "minor"
    return {
        "average_confidence": round(avg_conf, 3),
        "average_area": round(avg_area, 2),
        "severity": severity
    }

# --- API Routes ---
@app.route('/')
def home():
    return "🚀 Smart Pavers Backend Running!"

@app.route('/report', methods=['POST'])
def receive_report():
    try:
        if request.is_json:
            detections = request.get_json()
            latitude = float(request.args.get("lat", 0))
            longitude = float(request.args.get("lon", 0))
            traffic_density = request.args.get("traffic_density", estimate_traffic_density(latitude, longitude))
            timestamp = datetime.datetime.now().isoformat()
            summary = analyze_detections(detections)
            severity = summary["severity"]
            priority = calculate_priority(severity, traffic_density)

            new_report = Report(
                type="pothole",
                severity=severity,
                latitude=latitude,
                longitude=longitude,
                timestamp=timestamp,
                traffic_density=traffic_density,
                priority=priority
            )
            db.session.add(new_report)
            db.session.commit()

            if priority >= 5:
                send_email(
                    "🚨 Urgent Road Defect Detected",
                    f"Pothole(s) Detected\nSeverity: {severity}\nPriority: {priority}\nLocation: ({latitude}, {longitude})\nTimestamp: {timestamp}"
                )
            return jsonify({"message": "✅ Report saved", "severity": severity, "priority": priority}), 201

        elif 'image' in request.files:
            image_file = request.files['image']
            image_pil = Image.open(image_file.stream)
            exif_data = get_exif_data(image_pil)
            latitude, longitude = get_lat_lon(exif_data)
            if latitude is None or longitude is None:
                return jsonify({"error": "No GPS data in image"}), 400

            image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
            results = model(image_cv)
            detections = results.pandas().xyxy[0]

            if detections.empty:
                return jsonify({"error": "No defects detected"}), 400

            det_list = []
            for _, row in detections.iterrows():
                det_list.append({
                    "class": row["name"],
                    "confidence": float(row["confidence"]),
                    "bounding_box": {
                        "x1": float(row["xmin"]),
                        "y1": float(row["ymin"]),
                        "x2": float(row["xmax"]),
                        "y2": float(row["ymax"]),
                    }
                })

            summary = analyze_detections(det_list)
            severity = summary["severity"]
            traffic_density = request.form.get("traffic_density", estimate_traffic_density(latitude, longitude))
            priority = calculate_priority(severity, traffic_density)
            timestamp = datetime.datetime.now().isoformat()

            new_report = Report(
                type="pothole",
                severity=severity,
                latitude=latitude,
                longitude=longitude,
                timestamp=timestamp,
                traffic_density=traffic_density,
                priority=priority
            )
            db.session.add(new_report)
            db.session.commit()

            if priority >= 5:
                send_email(
                    "🚨 Urgent Road Defect Detected",
                    f"Pothole(s) Detected\nSeverity: {severity}\nPriority: {priority}\nLocation: ({latitude}, {longitude})\nTimestamp: {timestamp}"
                )

            return jsonify({"message": "✅ Image processed", "severity": severity, "priority": priority}), 201

        else:
            return jsonify({"error": "Send either JSON or image"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/reports', methods=['GET'])
def get_reports():
    reports = Report.query.order_by(Report.priority.desc()).all()
    return jsonify([r.to_dict() for r in reports]), 200

@app.route('/clear_reports', methods=['POST'])
def clear_reports():
    try:
        num_rows_deleted = db.session.query(Report).delete()
        db.session.commit()
        return jsonify({"message": f"✅ Cleared {num_rows_deleted} reports"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run the Server ---
if __name__ == '__main__':  # ✅ FIXED HERE
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)