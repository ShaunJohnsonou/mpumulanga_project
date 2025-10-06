from ultralytics import YOLO
import cv2
from scripts.draw_regions import region_class
from vehicle_class import vehicle_class
import json
from vehicle_class import ViewTransformer, scale_coordinates
from mask import mask
import numpy as np
import os


#Initiate the variables
PATH_TO_VIDEO = r"demo_videos\video_0.mp4"
MODEL_NAME = "yolov8x.pt"
TRACKING_MODEL = "bytetrack.yaml"
IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720
vehicle_tracker = {}
SPEED_LIMIT = 120
PLAY_ROOM = 10
FINE_SPEED_LIMIT = SPEED_LIMIT + PLAY_ROOM
TIME_NOT_DETECTED_THRESHOLD = 2
INTERVAL_BETWEEN_SPEED_CALCULATION = 25
CIRCULAR_ARRAY_SIZE = 100
CIRCULAR_ARRAY = []
image_number = 0
FPS = 25 #(frames per second)


SOURCE_0 = np.array([[1252, 787], [2298, 803], [5039, 2159], [-550, 2159]])
SOURCE_0 = scale_coordinates(coords=SOURCE_0, original_width=3840, original_height=2160, target_width=IMAGE_WIDTH, target_height=IMAGE_HEIGHT)

TARGET_WIDTH = 25
TARGET_HEIGHT = 250
TARGET = np.array(
    [
        [0, 0],
        [TARGET_WIDTH - 1, 0],
        [TARGET_WIDTH - 1, TARGET_HEIGHT - 1],
        [0, TARGET_HEIGHT - 1],
    ]
)
#Initialize the YOLO model
model = YOLO(MODEL_NAME).to("cuda:0")

#Initialize the videoCapture
cap = cv2.VideoCapture(PATH_TO_VIDEO)
ret, frame = cap.read()
transformer = ViewTransformer(SOURCE_0, TARGET)
if not ret:
    print("Error: Could not open video.")
    exit()

# Initialize video writer for processed video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'XVID' for .avi
output_video = cv2.VideoWriter('processed_video.mp4', fourcc, FPS, (IMAGE_WIDTH, IMAGE_HEIGHT))

# reuse_previous_regions = input("Do you want to reuse previous regions? (y/n): ")
reuse_previous_regions = 'y'
while reuse_previous_regions not in ["y", "n"]:
    reuse_previous_regions = input("Do you want to reuse previous regions? (y/n): ")
if reuse_previous_regions == "n":
    region_drawer = region_class(cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT)))
    region_points = region_drawer.draw_region()
    with open("region_points.json", "w") as f:
        json.dump(region_points, f)
else:
    with open("region_points.json", "r") as f:
        region_points = json.load(f)

# Build binary mask (1 inside polygon, 0 outside)
image_w, image_h = IMAGE_WIDTH, IMAGE_HEIGHT
region_mask = mask(image_w, image_h, region_points)

def apply_region_overlay(frame, region_mask_obj, region_points):
    """
    Apply a semi-transparent overlay showing the region area and polygon outline
    """
    # Create overlay with semi-transparent fill
    overlay = frame.copy()
    # Create colored mask for the region area (light green with transparency)
    region_color = np.array([144, 238, 144], dtype=np.uint8)  # Light green
    alpha = 0.25  # Transparency level (0.0 to 1.0)

    # Apply color to the region area
    mask_array = region_mask_obj.populated_mask
    for i in range(3):  # Apply to all color channels
        overlay[:, :, i] = np.where(mask_array == 1,
                                   overlay[:, :, i] * (1 - alpha) + region_color[i] * alpha,
                                   overlay[:, :, i])

    # Draw polygon outline (more visible)
    if len(region_points) > 0:
        points_array = np.array(region_points, dtype=np.int32)
        # Draw the polygon outline in red
        cv2.polylines(overlay, [points_array], isClosed=True, color=(144, 238, 144), thickness=3)
        # Draw individual points as small circles
        for point in region_points:
            cv2.circle(overlay, point, 5, (144, 238, 144), -1)  # Red dots

    return overlay

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

if cap.isOpened():
    while ret:
        if not ret:
            cap = cv2.VideoCapture(PATH_TO_VIDEO)
            ret, frame = cap.read()
        image_number += 1
        time_stamp = image_number / FPS
        ret, frame = cap.read()
        frame = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))


        if len(CIRCULAR_ARRAY) >= CIRCULAR_ARRAY_SIZE:
            CIRCULAR_ARRAY.pop(0)


        result = model.track(frame, persist=True, tracker=TRACKING_MODEL, verbose=False, device="cuda:0")[0]
        boxes = result.boxes
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
            center_y = y2

            is_inside = region_mask.point_is_inside(center_x, center_y)

            # Ensure vehicle object exists in tracker dict
            if tracker_id not in vehicle_tracker:
                vehicle_tracker[tracker_id] = vehicle_class(tracker_id, region_points, INTERVAL_BETWEEN_SPEED_CALCULATION)

            vehicle_object = vehicle_tracker[tracker_id]
            transformed_points = transformer.transform_points(np.array([x1, y1, x2, y2])).astype(int)
            x_actual = transformed_points[0]
            y_actual = transformed_points[1]
            speed, update = vehicle_object.detected(float(conf), [x1, y1, x2, y2], bool(is_inside), (x_actual, y_actual), time_stamp)


            if region_mask.point_is_inside(center_x, center_y):
                if speed > FINE_SPEED_LIMIT:
                    color = (0, 0, 255)
                elif speed > SPEED_LIMIT:
                    color = (0, 255, 255)
                else:
                    color = (0, 255, 0)
                label = f"id: {tracker_id}, speed: {speed} km/h"
                cv2.putText(frame, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                if speed > FINE_SPEED_LIMIT:
                    PATH_TO_IMAGE_FOLDER = "evidence"
                    if update:
                        for img_number, img in enumerate(CIRCULAR_ARRAY):
                            if not os.path.exists(f"{PATH_TO_IMAGE_FOLDER}/{tracker_id}"):
                                os.makedirs(f"{PATH_TO_IMAGE_FOLDER}/{tracker_id}")
                            cv2.imwrite(f"{PATH_TO_IMAGE_FOLDER}/{tracker_id}/{img_number+image_number}_{speed:.2f}.jpg", img)

            # Apply region overlay to the frame
            frame_with_overlay = apply_region_overlay(frame.copy(), region_mask, region_points)

            CIRCULAR_ARRAY.append(frame_with_overlay)

        # Write the processed frame to output video
        output_video.write(frame_with_overlay)

        cv2.imshow("Frame", frame_with_overlay)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
output_video.release()
cv2.destroyAllWindows()






