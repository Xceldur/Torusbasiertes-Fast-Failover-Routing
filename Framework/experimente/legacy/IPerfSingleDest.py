import itertools
import re
from typing import override

from mininet.net import Mininet
from mininet.node import Node

from experimente.Experiment import Experiment


class IPerfSingleDest(Experiment):
    @property
    def name(self) -> str:
        return self._name

    def __init__(self, size_x: int, size_y: int, net: Mininet, dst_node: str,
                 server_options: dict = None, client_options: dict = None) -> None:
        self._name = "IPerfSingleDest"
        # initialize optional parameter if they are None
        if server_options is None:
            server_options = {}
        if client_options is None:
            client_options = {}

        # set default parameter if not set already. Note you may crash the experiment if you modify those
        # be warned. Note: Also shorthand notation is used if possible...
        server_options_default = {
            '-t': '40',
            '--sum-dstip': '',  # that's neeed for the parser to work
            '-f': 'm'  # output in mbits/s
        }
        client_options_default = {
            '-t': '10',
            '-w': '50kb',
        }
        server_options = server_options_default | server_options
        client_options = client_options_default | client_options

        # next convert option to a string that is
        self.client_options = ' '.join([f'{k} {v}' for k, v in client_options.items()])
        self.server_options = ' '.join([f'{k} {v}' for k, v in server_options.items()])
        self.dst = dst_node

        super().__init__(size_x, size_y, net)

    def _extractSum(self, output_iperf):
        sum_line = None
        search = re.search(r'\[SUM].*\s', output_iperf)
        if search is None:
            return 0, 0
        sum_line = search.group()
        mbytes_transferred = float(re.search(r'(\d+(\.\d+)?) MBytes', sum_line).group(1))
        mbit_sec = float(re.search(r'(\d+(\.\d+)?) Mbits/sec', sum_line).group(1))

        return mbytes_transferred, mbit_sec

    @override
    def run(self, **kwargs) -> dict:
        # start server on dst
        dst_host: Node = self.net[self.dst]  # -t 40 --sum-dstip
        dst_host.sendCmd(f'iperf -zs  {self.server_options}')

        output_iperf_server_start = dst_host.monitor(timeoutms=1000)
        if 'Server listening on' not in output_iperf_server_start:  # dst_host.monitor(timeoutms=1000):
            raise RuntimeError('Somehow Iperf was not stared within the timeout, maybe your computer is to slow,'
                               'yet it seems more likely that something went wrong here:'
                               f'{output_iperf_server_start}')

        # start iperf as client on all nodes
        for x, y in itertools.product(range(self.SIZE_X), range(self.SIZE_Y)):
            current_host = f'h{x}x{y}'
            if self.dst == current_host:
                continue  # -t 10 -w 50kb
            # print(f'iperf -zc {dst_host.IP()} {self.client_options} &')
            self.net[current_host].sendCmd(f'iperf -zc {dst_host.IP()} {self.client_options} &')

        # get benchmark output from server
        output = dst_host.waitOutput()
        mbytes_transferred, mbit_sec = self._extractSum(output)

        # stop iperf if it is still running or rather kill running command with SIGKILL
        for host in self.net.hosts:  # type: Node
            host.waitOutput(verbose=False)

        return {'speed': mbit_sec,
                'mbits': mbytes_transferred}


class IPerfSingleDestUPD(IPerfSingleDest): # TODO: Debug Code
    def __init__(self, size_x: int, size_y: int, net: Mininet, dst_node: str,
                 server_options: dict = None, client_options: dict = None):
        server_options = {
                             '-u': ''
                         } | server_options if server_options is not None else dict()
        client_options = {
                             '-u': ''
                         } | client_options if client_options is not None else dict()
        super().__init__(size_x, size_y, net, dst_node, server_options, client_options)
