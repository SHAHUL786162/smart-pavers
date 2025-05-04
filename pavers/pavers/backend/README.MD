# Backend - Smart Pavers

This is the Flask Backend API for the Smart Pavers project.

## Features
- Accepts defect reports as JSON or Images
- Runs AI detection (YOLOv5) automatically on uploaded images
- Calculates severity, priority
- Sends email alerts to authorities if priority >= 5
- Stores all reports in SQLite database
- Provides `/reports` API for dashboard

## How to Run

1. Install packages:
    ```
    pip install -r requirements.txt
    ```

2. Start server:
    ```
    python app.py
    ```

Server will run at: `http://localhost:5000/`
