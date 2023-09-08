from tracker.base import Tracker
from tracker.yolo import YoloTracker
from tracker.dummy import DummyTracker


def get_tracker() -> Tracker:
    return YoloTracker()

def get_dummy_tracker() -> Tracker:
    return DummyTracker()
