import time
import numpy as np
import cv2
SCALING_FACTOR = 3.4

def scale_coordinates(coords, original_width=3840, original_height=2160, target_width=1280, target_height=720):
    """Scale coordinates from original image dimensions to target dimensions"""
    scale_x = target_width / original_width
    scale_y = target_height / original_height
    return np.array([[int(x * scale_x), int(y * scale_y)] for x, y in coords])




class ViewTransformer:
    def __init__(self, SOURCE_0: np.ndarray, target: np.ndarray) -> None:
        SOURCE_0 = SOURCE_0.astype(np.float32)
        target = target.astype(np.float32)
        self.m = cv2.getPerspectiveTransform(SOURCE_0, target)

    def transform_points(self, points: np.ndarray) -> np.ndarray:
        if points.size == 0:
            return points

        reshaped_points = points.reshape(-1, 1, 2).astype(np.float32)
        transformed_points = cv2.perspectiveTransform(reshaped_points, self.m)
        return transformed_points.reshape(-1, 2)


class vehicle_class():
    def __init__(self, tracker_id: int, region_points: list, INTERVAL_BETWEEN_SPEED_CALCULATION: int):
        self.tracker_id = tracker_id
        self.region_points = region_points
        self.tracked_is_inside = []
        self.times_detected = []
        self.tracked_conf = []
        self.tracked_boxes = []
        self.actual_coordinates = []
        self.actual_coordinates_and_time = []
        self.interval_for_speed_calculation = 0
        self.speed = 0
        self.INTERVAL_BETWEEN_SPEED_CALCULATION = INTERVAL_BETWEEN_SPEED_CALCULATION

    def detected(self, conf: float, box: list, is_inside: bool, actual_coordinates: tuple, time_stamp: float):
        box_center = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        self.times_detected.append((box_center, time_stamp))
        self.tracked_conf.append(conf)
        self.tracked_boxes.append(box)
        self.tracked_is_inside.append(is_inside)
        self.interval_for_speed_calculation += 1
        update = False
        if self.interval_for_speed_calculation >= self.INTERVAL_BETWEEN_SPEED_CALCULATION:
            self.actual_coordinates_and_time.append((time_stamp, actual_coordinates))
            self.calculate_speed()
            self.interval_for_speed_calculation = 0
            update = True
        return self.speed, update

    def calculate_speed(self):
        if len(self.actual_coordinates_and_time) < 2:
            return
        most_recent_entry = self.actual_coordinates_and_time[-1]
        most_recent_coordinate = most_recent_entry[1]
        most_recent_time = most_recent_entry[0]
        x1, y1 = most_recent_coordinate[0]
        x2, y2 = most_recent_coordinate[1]
        x_m1 = (x1 + x2) / 2
        y_m1 = (y1 + y2) / 2

        second_most_recent_entry = self.actual_coordinates_and_time[-2]
        second_most_recent_coordinate = second_most_recent_entry[1]
        second_most_recent_time = second_most_recent_entry[0]
        x3, y3 = second_most_recent_coordinate[0]
        x4, y4 = second_most_recent_coordinate[1]
        x_m2 = (x3 + x4) / 2
        y_m2 = (y3 + y4) / 2

        hyptenuse = np.linalg.norm(np.array([x_m1, y_m1]) - np.array([x_m2, y_m2]))
        time_difference = most_recent_time - second_most_recent_time
        speed = (hyptenuse / time_difference) * SCALING_FACTOR
        self.speed = speed


