from random import Random

from mininet.net import Mininet

from experimente.Experiment import Experiment


class IPerfAllotAll(Experiment):
    @property
    def name(self) -> str:
        return "IperfAlltoAll"

    def __init__(self, size_x: int, size_y: int, net: Mininet, server_options: dict = None,
                 client_options: dict = None, number_of_pairs: int = 5, seed=None):
        super().__init__(size_x, size_y, net)
        assert number_of_pairs * 2 <= size_x * size_y, "You can not use more pairs than client server pairs available"
        assert number_of_pairs >= 0, "This can not work with less than zero"
        random = Random(seed)
        # initialize optional parameter if they are None
        if server_options is None:
            server_options = {}
        if client_options is None:
            client_options = {}

        # set default options if non a provided
        server_options_default = {
            '-t': '18',
            '--sum-dstip': '',  # that's neeed for the parser to work
            '-f': 'm'  # output in mbits/s
        }
        client_options_default = {
            '--full-duplex': '',
            '-t': '10',
            '-w': '50kb',
            '-f': 'm'  # output in mbits/s
        }
        server_options = server_options_default | server_options
        client_options = client_options_default | client_options

        # next convert option to a string that is
        self.client_options = ' '.join([f'{k} {v}' for k, v in client_options.items()])
        self.server_options = ' '.join([f'{k} {v}' for k, v in server_options.items()])

        # save timeout from client and server
        self.server_timeout = int(server_options['-t'])
        self.client_timeout = int(client_options['-t'])

        # generate pairs randomly, but without putting them back, due to problem with duplicate servers on one client
        shuffled_node_list = random.sample(self.torus_nodes, number_of_pairs * 2)
        self.communication_pairs = list(zip(shuffled_node_list[::2], shuffled_node_list[1::2]))

    def run(self, **kwargs) -> dict:
        # start servers
        for _, s_node in self.communication_pairs:
            self.net[s_node].sendCmd(f'timeout -k 3 {self.server_timeout + 3} iperf -zs  {self.server_options}')
        # start clients
        for c_node, s_node in self.communication_pairs:
            self.net[c_node].sendCmd(f'timeout -k 3 {self.client_timeout + 3} '
                                     f'iperf -zc {self.net[s_node].IP()} {self.client_options}')

        # Wait for clients to finish and collect results
        results = {}
        for c_node, s_node in self.communication_pairs:
            client_output = self.net[c_node].waitOutput()
            server_output = self.net[s_node].waitOutput()
            results[(c_node, s_node)] = {
                'client_output': client_output,
                'server_output': server_output
            }
            # print(f'{client_output}, {server_output}')

        evaluated_results = self._evaluate(results)
        print(evaluated_results)
        return evaluated_results

    def _evaluate(self, results: dict) -> dict:
        evaluated_results = {}
        for pair, outputs in results.items():
            # get output of server and client
            client_output = outputs['client_output']
            server_output = outputs['server_output']

            # parse throughput
            client_throughput = self._parse_throughput(client_output)
            server_throughput = self._parse_throughput(server_output)

            # add throughput to result
            evaluated_results[str(pair)] = {
                'client_throughput': client_throughput,
                'server_throughput': server_throughput,
            }

        return evaluated_results

    # ugly thing to parse messy output from iperf. There is support for full duplex mode...
    def _parse_throughput(self, output: str):
        if "Connection refused" in output or "failed" in output:
            return None

        throughput = None
        full_duplex = False

        for line in output.split('\n'):
            if 'full-duplex' in line:
                full_duplex = True
            if '[SUM]' in line and full_duplex:
                parts = line.split()
                if parts[-1] == 'Mbits/sec':
                    throughput = float(parts[-2])
                    break
            elif 'Mbits/sec' in line and not full_duplex:
                parts = line.split()
                if parts[-1] == 'Mbits/sec':
                    throughput = float(parts[-2])
                    break
        return throughput
