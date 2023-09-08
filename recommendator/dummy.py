from random import randint
from time import sleep

from .base import Recommendator


class DummyRecommendator(Recommendator):
    def predict(self, real_goods: list) -> list:
        return [5, 11]
