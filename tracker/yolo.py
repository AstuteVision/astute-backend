import json
from logging import getLogger

import cv2
import numpy as np
from ultralytics import YOLO

from .base import Tracker

logger = getLogger(__name__)


class YoloTracker(Tracker):
    def __init__(self, path_to_zone_annotations: str = r"D:\pythonProjects\AstuteBackend\tracker\zones.json"):
        self.model = YOLO("yolov8n.pt")
        self.track_history = []
        # fixme need to be annotated
        with open(path_to_zone_annotations) as file:
            zones_json = json.load(file)
            self.zones = {shape["label"]: np.array(shape["points"], dtype=np.int32) for shape in zones_json["shapes"]}

    def predict(self, frame, destination_coords: tuple[int]) -> tuple[float, tuple[int, int]]:
        # fixme get only first video stream
        results = self.model.predict(frame, classes=[0], verbose=False)
        if not results:
            return 0, (-1, -1)
        boxes = results[0].boxes.xywh.cpu().tolist()
        # fixme predict without registration - track only the first one
        if not boxes:
            return 0, (-1, -1)
        box = boxes[0]
        direction = self.__estimate_non_warped_direction(box)
        current_zone_name, next_zone_name = self.__estimate_neigborhood_zones(box, direction=direction)
        if current_zone_name is None:
            return 0, (-2, -2)
        x_current, y_current = map(int, current_zone_name.split(","))
        if next_zone_name is None:
            return 0, (x_current, y_current)
        x_next, y_next = map(int, next_zone_name.split(","))
        dx = x_next - x_current
        dy = y_next - y_current

        x = destination_coords[0] - x_next
        y = destination_coords[1] - y_next

        x_sum = dx+x
        y_sum = dy+y

        angle_to_rotate = np.rad2deg(np.arctan2(y_sum, x_sum))
        print("YOLO", x_current, y_current, "Next", x_next, y_next, "Angle", angle_to_rotate)
        return int(angle_to_rotate), (x_current, y_current)

    def __estimate_non_warped_direction(self, box):
        x, y, w, h = box
        x_up_left = x
        y_up_left = y - h / 2
        self.track_history.append((float(x_up_left), float(y_up_left)))
        if len(self.track_history) > 30:  # retain 90 tracks for 90 frames
            self.track_history.pop(0)
        if len(self.track_history) > 2:
            dx = self.track_history[-1][0] - self.track_history[-2][0]
            dy = self.track_history[-1][1] - self.track_history[-2][1]
            velocity = np.sqrt(dx**2 + dy**2)
            std_velocity_error = 1.3
            if velocity < std_velocity_error:
                return 0
            direction = np.arctan2(dy, dx)
            return direction
        return 0

    def __estimate_neigborhood_zones(self, box, direction):
        x, y, w, h = box
        current_zone = None
        next_zone = None
        for zone_name, zone_points in self.zones.items():
            if cv2.pointPolygonTest(zone_points, (int(x), int(y)), False) >= 0:
                current_zone = zone_name
                logger.debug(f"Track is in zone {zone_name}")
            next_point = (int(x + 2 * 60 * np.cos(direction)), int(y + 2 * 60 * np.sin(direction)))
            if cv2.pointPolygonTest(zone_points, next_point, False) >= 0:
                next_zone = zone_name
                logger.debug(f"Track will be in zone {zone_name}")
        return current_zone, next_zone
