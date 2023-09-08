from tracker.base import Tracker
from tracker.dummy import DummyTracker
from tracker.yolo import YoloTracker


def get_tracker() -> Tracker:
    return YoloTracker()


def get_dummy_tracker() -> Tracker:
    return DummyTracker()
