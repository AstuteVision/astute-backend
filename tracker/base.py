from abc import ABC, abstractmethod


class Tracker(ABC):
    @abstractmethod
    async def predict(self, frames, destination_coords: tuple[int]):
        """

        :param frames:
        :param destination_coords:
        :return:
        """
        raise NotImplementedError("Abstract class call!")
