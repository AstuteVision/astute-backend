from random import randint
from time import sleep

from .base import Tracker


class DummyTracker(Tracker):
    async def predict(self, frames, destination_coords: tuple[int]):
        sleep(0.1)
        return 10, (2, 3)
