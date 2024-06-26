import itertools
from abc import abstractmethod, ABC
from typing import Final

from mininet.net import Mininet


class Experiment(ABC):
    def __init__(self, size_x: int, size_y: int, net: Mininet):
        self.net = net
        self.SIZE_Y: Final = size_y
        self.SIZE_X: Final = size_x
        self.torus_nodes = [f'h{x}x{y}' for x, y in itertools.product(range(self.SIZE_X), range(self.SIZE_Y))]

    @abstractmethod
    def run(self, **kwargs) -> dict:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
