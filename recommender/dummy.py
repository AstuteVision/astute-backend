from .base import Recommender


class DummyRecommender(Recommender):
    def predict(self, real_goods: list) -> list:
        return [5, 11]
