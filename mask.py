import numpy as np
import cv2

class mask:
    def __init__(self, image_width: int, image_height: int, region_points: list):
        self.image_width = image_width
        self.image_height = image_height
        self.mask = np.zeros((self.image_height, self.image_width), dtype=np.uint8)
        self.populated_mask = self._populate_mask(region_points)

    def _populate_mask(self, region_points: list):
        if region_points is None or len(region_points) == 0:
            return self.mask
        polygon = np.array(region_points, dtype=np.int32).reshape((-1, 1, 2))
        filled = self.mask.copy()
        cv2.fillPoly(filled, [polygon], color=1)
        return filled

    def point_is_inside(self, x: int, y: int) -> bool:
        try:
            return bool(self.populated_mask[y, x] == 1)
        except:
            return False
