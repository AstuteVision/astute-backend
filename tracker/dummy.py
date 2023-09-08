from random import randint
from time import sleep

from .base import Tracker


class DummyTracker(Tracker):
    def predict(self, frames, destination_coords: tuple[int]):
        return 10, (2, 9)
