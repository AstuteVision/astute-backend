from tracker.base import Tracker
from tracker.yolo import YoloTracker


def get_tracker() -> Tracker:
    return YoloTracker()
