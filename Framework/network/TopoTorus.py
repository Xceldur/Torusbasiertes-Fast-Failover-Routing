import itertools
from typing import override

from mininet.topo import Topo


class TopoTorus(Topo):

    def __init__(self, x_size: int, y_size: int):
        self.Y_SIZE: int = y_size
        self.X_SIZE: int = x_size
        self.sw = [[None for _ in range(x_size)] for _ in range(y_size)]
        self.ho = [[None for _ in range(x_size)] for _ in range(y_size)]

        super().__init__()

    @override
    def build(self, **_opts):
        i = 1
        # generate switches and host. Moreover, connect them
        for x in range(self.X_SIZE):
            for y in range(self.Y_SIZE):
                dpid = ((x + 1) << 8) + (y + 1)
                self.sw[x][y] = self.addSwitch(f's{x}x{y}', dpid=f'{dpid:x}')
                self.ho[x][y] = self.addHost(f'h{x}x{y}')
                self.addLink(self.sw[x][y], self.ho[x][y])
                i = i + 1

        for x in range(self.X_SIZE):
            for y in range(self.Y_SIZE):
                self.addLink(self.sw[x][y], self.sw[(x + 1) % self.X_SIZE][y])
                self.addLink(self.sw[x][y], self.sw[x][(y + 1) % self.Y_SIZE])


class TopoTorusSingleDest(TopoTorus):

    def __init__(self, x_size: int, y_size: int, dst: str):
        self.dst = dst
        super().__init__(x_size, y_size)

    @override
    def build(self, **_opts):
        super().build(**_opts)
        self.addSwitch('puppetmaster', dpid=f'{hex(70000)}')
        self.addLink(self.dst, 'puppetmaster')

        for x, y in itertools.product(range(self.X_SIZE), range(self.Y_SIZE)):
            self.addLink('puppetmaster', f's{x}x{y}')
