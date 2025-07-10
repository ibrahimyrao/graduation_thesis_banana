from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
from datetime import datetime, timedelta
import cv2
import csv

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
LOG_PATH = 'hsv_log.csv'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

latest_filename = None
latest_status = None
estimated_ripeness_time = "Hesaplanıyor..."

def check_ripeness(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Fotoğraf okunamadı", img, (0, 0, 0)

    height, width, _ = img.shape
    box_size = 100
    x_start = width // 2 - box_size // 2
    y_start = height // 2 - box_size // 2
    roi = img[y_start:y_start + box_size, x_start:x_start + box_size]

    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    avg_hsv = cv2.mean(hsv_roi)[:3]
    h, s, v = avg_hsv

    if 15 <= h <= 45 and s >= 50 and v >= 50:
        status = "Olgunlaştı"
        color = (0, 255, 0)
    else:
        status = "Olgunlaşmadı"
        color = (0, 0, 255)

    cv2.rectangle(img, (x_start, y_start), (x_start + box_size, y_start + box_size), color, 3)
    cv2.putText(img, status, (x_start, y_start - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

    return status, img, (h, s, v)

def log_hsv(timestamp, h, s, v, status):
    with open(LOG_PATH, 'a') as f:
        f.write(f"{timestamp.isoformat()},{h:.2f},{s:.2f},{v:.2f},{status}\n")

def read_log_entries():
    entries = []
    if not os.path.exists(LOG_PATH):
        return entries

    with open(LOG_PATH, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                timestamp = datetime.fromisoformat(row[0])
                h = float(row[1])
                entries.append((timestamp, h))
            except:
                continue
    return sorted(entries, key=lambda x: x[0])

def estimate_ripening():
    entries = read_log_entries()
    if len(entries) < 2:
        return "Yeterli veri yok"

    now_time, h_now = entries[-1]
    one_day_ago = now_time - timedelta(hours=24)

    closest = None
    for ts, h in reversed(entries):
        if ts <= one_day_ago:
            closest = (ts, h)
            break

    if not closest:
        return "24 saat öncesine ait kayıt yok"

    ts_then, h_then = closest
    delta_h = h_then - h_now

    if delta_h <= 0:
        return "Renk değişimi tespit edilemedi"

    h_target = 45
    h_gap = h_now - h_target
    if h_gap <= 0:
        return "Zaten olgunlaştı"

    estimated_hours = (24 * h_gap) / delta_h
    estimated_time = now_time + timedelta(hours=estimated_hours)

    return estimated_time.strftime("%Y-%m-%d %H:%M:%S")

@app.route('/upload_image', methods=['POST'])
def upload_image():
    global latest_filename, latest_status, estimated_ripeness_time

    image_data = request.data
    if not image_data:
        return jsonify({'message': 'No image data received'}), 400

    timestamp = datetime.now()
    filename = timestamp.strftime('%Y%m%d_%H%M%S') + '.jpg'
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(filepath, 'wb') as f:
            f.write(image_data)

        status, marked_img, (h, s, v) = check_ripeness(filepath)
        cv2.imwrite(filepath, marked_img)

        latest_filename = filename
        latest_status = status

        log_hsv(timestamp, h, s, v, status)
        estimated_ripeness_time = estimate_ripening()

        print(f"Image saved and marked: {filepath}")
        print(f"Ripeness status: {status}")

        return jsonify({'message': 'Image received successfully', 'status': status}), 200

    except Exception as e:
        print(f"Error saving image: {e}")
        return jsonify({'message': 'Failed to save image'}), 500

@app.route('/')
def index():
    if latest_filename and latest_status:
        image_url = f'/uploads/{latest_filename}'
        status = latest_status
        est_time = estimated_ripeness_time
    else:
        image_url = None
        status = "Henüz fotoğraf yok."
        est_time = "---"

    html = '''
    <!doctype html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Muz Olgunluk Takibi</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f9f9f9;
                color: #333;
                text-align: center;
                margin: 0;
                padding: 0;
            }
            header {
                background-color: #4CAF50;
                color: white;
                padding: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                margin: 0;
            }
            .container {
                margin-top: 30px;
                padding: 20px;
            }
            img {
                max-width: 80vw;
                border: 5px solid #eee;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border-radius: 8px;
            }
            h2 {
                font-size: 2em;
                margin-top: 20px;
            }
            .status {
                color: {% if status == 'Olgunlaştı' %}green{% else %}red{% endif %};
                font-weight: bold;
            }
            .estimate {
                font-size: 1.2em;
                margin-top: 20px;
                color: #555;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Muz Olgunluk Takip Sistemi</h1>
        </header>
        <div class="container">
            {% if image_url %}
                <img src="{{ image_url }}" alt="Son gönderilen fotoğraf" />
                <h2 class="status">{{ status }}</h2>
                <div class="estimate">
                    <strong>Tahmini Olgunlaşma Zamanı:</strong><br> {{ est_time }}
                </div>
            {% else %}
                <p>{{ status }}</p>
            {% endif %}
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, image_url=image_url, status=status, est_time=est_time)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
