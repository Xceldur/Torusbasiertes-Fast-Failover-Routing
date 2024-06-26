import itertools
import re

from mininet.net import Mininet

from experimente.Experiment import Experiment


class FpingTest(Experiment):
    def __init__(self, size_x: int, size_y: int, net: Mininet):
        super().__init__(size_x, size_y, net)
        self.ip_relation_host_relation = {h.IP(): h.name for h in net.hosts}

    def _generateExecutionString(self, hosts: list[str], count=3):
        assert len(hosts) > 0, 'the host list cannot be empty'
        cmd = (['fping', '-q', '-C', str(count)] + hosts)
        return ' '.join(cmd)

    def _parse_fping_output(self, fping_output: str):
        pattern = re.compile(r'(\S+)\s+:\s+(.+)')
        parsed_data = {}

        # Process each line in the output
        for line in fping_output.strip().split('\n'):
            match = pattern.match(line)
            if match:
                host_ip = match.group(1)
                responses = match.group(2).split()
                parsed_data[self.ip_relation_host_relation[host_ip]] = \
                    [None if resp == '-' else float(resp) for resp in responses]

        return parsed_data

    def run(self, **kwargs) -> dict:
        result_dict: dict = {}

        for x_src, y_src in itertools.product(range(self.SIZE_X), range(self.SIZE_Y)):
            # filter all obsolete ping targets due to reflexivity and symmetry
            target_hosts_iter = filter(lambda t_dst: (x_src, y_src) < t_dst,
                                       itertools.product(range(self.SIZE_X), range(self.SIZE_Y)))
            target_hosts = [f'h{x_dst}x{y_dst}' for x_dst, y_dst in target_hosts_iter]
            target_host_ips = list(map(lambda host_as_str: self.net[host_as_str].IP(), target_hosts))

            # skip if there are not target more to ping,
            if len(target_host_ips) == 0:
                break

            # next generate f ping string to execute
            cmd = self._generateExecutionString(target_host_ips, count=3)
            fping_output = self.net[f'h{x_src}x{y_src}'].cmd(cmd)
            result = self._parse_fping_output(fping_output)

            print(result)

            # update result dictionary
            for k, v in result.items():
                address = tuple(sorted([f'h{x_src}x{y_src}', k]))
                assert str(address) not in result_dict
                result_dict[str(address)] = v

        print(result_dict)

        return result_dict

    @property
    def name(self) -> str:
        return "FpingTest"
