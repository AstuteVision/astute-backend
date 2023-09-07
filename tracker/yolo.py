import numpy as np
from ultralytics import YOLO

from .base import Tracker


class YoloTracker(Tracker):
    def __init__(self):
        self.model = YOLO("yolov8n.pt")
        self.track_history = []
        # fixme need to be annotated
        self.zones = {}

    async def predict(self, frames, destination_coords: tuple[int]) -> tuple[float, tuple[int, int]]:
        # fixme get only first video stream
        frame = frames[0]
        results = self.model.track(frame, persist=True, classes=[0])
        boxes = results[0].boxes.xywh.cpu()
        track_ids: list[int] = results[0].boxes.id.int().cpu().tolist()
        # fixme predict without registration - track only the first one
        index_to_track = track_ids.index(1)
        box = boxes[index_to_track]
        degrees = await self.__estimate_direction(box)
        await self.__estimate_current_position(box)
        return degrees, (2, 3)

    async def __estimate_direction(self, box):
        x, y, w, h = box
        self.track_history.append((float(x), float(y)))
        if len(self.track_history) > 2:
            dx = self.track_history[-1][0] - self.track_history[-2][0]
            dy = self.track_history[-1][1] - self.track_history[-2][1]
            direction = np.arctan2(dy, dx)
            degrees_direction = np.rad2deg(direction)
            return degrees_direction
        return 0

    async def __estimate_current_position(self, box):
        # fixme calculate position by annotated zones
        print(self.zones)
        return 2, 3
