import torch
import os

try:
    model = torch.hub.load(
        os.path.abspath("yolov5"),
        'custom',
        path=os.path.abspath("ai_model/best.pt"),
        source='local',
        force_reload=True
    )
    print("✅ This is a YOLOv5 model.")
except Exception as e:
    print("❌ Not YOLOv5:", e)