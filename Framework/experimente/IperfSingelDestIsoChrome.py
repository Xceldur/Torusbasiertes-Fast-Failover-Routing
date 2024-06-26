import itertools
import re
from random import Random

from mininet.net import Mininet

from experimente.Experiment import Experiment


class IPerfSingelDestIsochrone(Experiment):
    @property
    def name(self) -> str:
        return "IperfSingeltoAll"

    def __init__(self, size_x: int, size_y: int, dst: str, net: Mininet, server_options: dict = None,
                 client_options: dict = None, isochronous : bool =False):
        super().__init__(size_x, size_y, net)
        # initialize optional parameter if they are None
        if server_options is None:
            server_options = {}
        if client_options is None:
            client_options = {}
        self.dst = dst

        # set default options if non a provided
        server_options_default = {
            '-t': '20',
            '--sum-dstip': '',  # that's neeed for the parser to work
            '-f': 'm'  # output in mbits/s
        }
        client_options_default = {
            #'--reverse': '',
            '-t': '10',
            '-f': 'm'  # output in mbits/s
        }
        if isochronous:
            client_options['--isochronous'] = ''

        server_options = server_options_default | server_options
        client_options = client_options_default | client_options

        # next convert option to a string that is
        self.client_options = ' '.join([f'{k} {v}' for k, v in client_options.items()])
        self.server_options = ' '.join([f'{k} {v}' for k, v in server_options.items()])

        # save timeout from client and server
        self.server_timeout = int(server_options['-t'])
        self.client_timeout = int(client_options['-t'])

        # generate nodes and remove dst
        self.client_list = [f'h{x}x{y}' for x, y in itertools.product(range(size_x), range(size_y))]
        self.client_list.remove(self.dst)

    def run(self, **kwargs) -> dict:
        # start server
        self.net[self.dst].sendCmd(f'timeout -k 3 {self.server_timeout + 3} iperf -zs  {self.server_options}')

        # start clients
        for client in self.client_list:
            self.net[client].sendCmd((f'timeout -k 3 {self.client_timeout + 3} '
                                      f'iperf -zc {self.net[self.dst].IP()} {self.client_options}'))

        # restive output form host
        result = dict()
        result[f'server_output'] = self.net[self.dst].waitOutput()
        result |= {f'{client}_output': self.net[client].waitOutput() for client in self.client_list}

        #for k,v in result.items():
        #    print(k + ':')
        #    print(v)

        x = self.parse_results(result)
        print(x)

        return x



    def parse_results(self,results: dict) -> dict:
        parsed_results = {}
        parsed_results['server'] = self.parse_server_sum_data_rate(results['server_output'])

        for key, output in results.items():
            if key == 'server_output':
                continue

            key = key.replace('_output', '')
            parsed_results[key] = self.parse_client_data_rate(output)
        return parsed_results


# Function to parse client data rate
    def parse_client_data_rate(self, output):
        match = re.search(r'\[\s*\d+\] .+?\s+([\d.]+)\s+Mbits/sec', output)
        if match:
            return float(match.group(1))
        return None

# Function to parse server sum data rate
    def parse_server_sum_data_rate(self, output):
        match = re.search(r'\[SUM\] .+?\s+([\d.]+)\s+Mbits/sec', output)
        if match:
            return float(match.group(1))
        return None