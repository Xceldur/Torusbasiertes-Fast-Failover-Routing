import itertools
from typing import override

import pingparsing
from mininet import node
from mininet.net import Mininet

from experimente.Experiment import Experiment


class PingTest(Experiment):

    def _pingSrcDst(self, host_src: node, host_dst: node):
        parser = pingparsing.PingParsing()

        # ping host five times and parse output
        ping_command_result = host_src.cmd(f'LC_ALL=C ping -i 0.3 -c 3 {host_dst.IP()}')
        # print(ping_command_result)
        stats = parser.parse(ping_command_result).as_dict()

        return {'src': host_src.name,
                'dst': host_dst.name,
                'rtt': stats['rtt_min'],
                'ploss': True if stats['packet_loss_rate'] > 0 else False}

    def __init__(self, size_x: int, size_y: int, net: Mininet):
        super().__init__(size_x, size_y, net)
        self._name = 'PingTest'

    @property
    def name(self) -> str:
        return self._name

    @override
    def run(self, **kwargs) -> dict:
        result = dict()
        i = 0
        # ping each host
        for x_src, y_src, x_dst, y_dst in itertools.product(range(self.SIZE_X), range(self.SIZE_Y), repeat=2):
            if (x_src, y_src) >= (x_dst, y_dst):
                continue

            r = self._pingSrcDst(host_src=self.net[f'h{x_src}x{y_src}'], host_dst=self.net[f'h{x_dst}x{y_dst}'])
            # print(r)
            result[i] = r
            i = i + 1

        return result