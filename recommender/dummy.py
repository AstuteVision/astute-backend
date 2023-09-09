from .base import Recommender


class DummyRecommender(Recommender):
    def predict(self, real_goods: list) -> list:
        return [2, 4]
