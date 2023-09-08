from abc import ABC, abstractmethod


class Recommendator(ABC):
    @abstractmethod
    async def predict(self, real_goods:list):
        """

        :param frames:
        :param destination_coords:
        :return:
        """
        raise NotImplementedError("Abstract class call!")
