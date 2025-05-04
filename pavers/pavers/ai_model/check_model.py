import torch

path = 'ai_model/best.pt'  # or change if named differently

try:
    model_data = torch.load(path, map_location='cpu')
    print("=== Keys in model file ===")
    print(model_data.keys())

    if 'model' in model_data and 'optimizer' in model_data:
        print("\n✅ This is likely a YOLOv5-trained model.")
    elif 'cfg' in model_data or 'yaml' in model_data:
        print("\n✅ This is likely a YOLOv8-trained model.")
    else:
        print("\n❓ Unknown format. Could be custom export or unsupported.")
except Exception as e:
    print("❌ Could not read model:", e)