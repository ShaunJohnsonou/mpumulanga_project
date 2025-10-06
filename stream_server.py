from flask import Flask, Response
from ultralytics import YOLO
import cv2
from draw_regions import region_class
from vehicle_class import vehicle_class, speed_cop
import json
from mask import mask
import threading
import time

app = Flask(__name__)

# Video processing variables
PATH_TO_VIDEO = r"demo_videos\video_1.mp4"
MODEL_NAME = "yolov8n.pt"
TRACKING_MODEL = "bytetrack.yaml"
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720
vehicle_tracker = {}
SPEED_LIMIT = 100
speed_cop = speed_cop(SPEED_LIMIT)

# Initialize the YOLO model
model = YOLO(MODEL_NAME)

# Global variables for streaming
current_frame = None
frame_lock = threading.Lock()

def load_region_points():
    """Load or create region points for masking"""
    try:
        with open("region_points.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return a default region if no region_points.json exists
        return [[(100, 100), (1100, 100), (1100, 600), (100, 600)]]

def generate_frames():
    """Generator function that yields video frames for streaming"""
    global current_frame

    # Initialize video capture
    cap = cv2.VideoCapture(PATH_TO_VIDEO)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Load region points
    region_points = load_region_points()

    # Build binary mask
    image_w, image_h = IMAGE_WIDTH, IMAGE_HEIGHT
    region_mask = mask(image_w, image_h, region_points)

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            # Loop the video
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))

        # Run YOLO tracking
        result = model.track(frame, persist=True, tracker=TRACKING_MODEL, verbose=False)
        if result and len(result) > 0:
            boxes = result[0].boxes

            for box in boxes:
                # Skip boxes without a tracker id yet
                if box.id is None:
                    continue

                conf = box.conf[0]
                tracker_id = int(box.id[0].item()) if hasattr(box.id[0], 'item') else int(box.id[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Compute a representative point (bbox center) and test against mask
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                is_inside = region_mask.point_is_inside(center_x, center_y)

                # Ensure vehicle object exists in tracker dict
                if tracker_id not in vehicle_tracker:
                    vehicle_tracker[tracker_id] = vehicle_class(tracker_id, region_points)
                vehicle_object = vehicle_tracker[tracker_id]
                vehicle_object.detected(float(conf), [x1, y1, x2, y2], bool(is_inside))

                if is_inside:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Convert frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        # Update the current frame for other endpoints
        with frame_lock:
            current_frame = frame_bytes

        # Yield the frame for MJPEG streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        frame_count += 1
        # Small delay to control frame rate
        time.sleep(0.033)  # ~30 FPS

    cap.release()

@app.route('/')
def index():
    """Main page"""
    return '''
    <html>
    <head>
        <title>Video Stream</title>
    </head>
    <body>
        <h1>Video Stream Server</h1>
        <p>Processed video stream with object detection</p>
        <img src="/video_feed" width="1280" height="720" />
    </body>
    </html>
    '''

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/current_frame.jpg')
def current_frame_endpoint():
    """Get current frame as JPEG"""
    with frame_lock:
        if current_frame is not None:
            return Response(current_frame, mimetype='image/jpeg')
        else:
            return "No frame available", 404

if __name__ == '__main__':
    print("Starting video stream server...")
    print("Access the stream at: http://localhost:5000/video_feed")
    print("Or view in browser at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
