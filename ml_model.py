from random import randint
from time import sleep


class DummyTracker:
    async def predict(self, data):
        sleep(0.1)
        return bool(randint(0, 3))
