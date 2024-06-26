import itertools
import multiprocessing
import re
import time

from mininet.net import Mininet
from experimente.Experiment import Experiment


class FpingTestMultiBatch(Experiment):
    def __init__(self, size_x: int, size_y: int, net: Mininet, batch_size: int = None):
        super().__init__(size_x, size_y, net)
        self.ip_relation_host_relation = {h.IP(): h.name for h in net.hosts}

        if batch_size is None or batch_size < 1:
            batch_size = multiprocessing.cpu_count()
        self.batch_size = batch_size

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
            else:
                raise ValueError(f"\nUnexpected fping output line: {line}\n"
                                 f"Contents of fping output:\n {fping_output}")

        return parsed_data

    def run(self, **kwargs) -> dict:
        assert self.batch_size >= 1, 'batch size must be greater than or equal to 1'

        result_dict: dict = {}
        fping_commands = {}

        # Generate all commands to be executed
        for x_src, y_src in itertools.product(range(self.SIZE_X), range(self.SIZE_Y)):
            target_hosts_iter = filter(lambda t_dst: (x_src, y_src) < t_dst,
                                       itertools.product(range(self.SIZE_X), range(self.SIZE_Y)))
            target_hosts = [f'h{x_dst}x{y_dst}' for x_dst, y_dst in target_hosts_iter]
            target_host_ips = list(map(lambda host_as_str: self.net[host_as_str].IP(), target_hosts))

            if len(target_host_ips) == 0:
                continue

            cmd = self._generateExecutionString(target_host_ips, count=3)
            fping_commands[f'h{x_src}x{y_src}'] = cmd

        # print(fping_commands)

        # Execute commands in batches
        command_items = list(fping_commands.items())
        for i in range(0, len(command_items), self.batch_size):
            batch = command_items[i:i + self.batch_size]

            # Send all commands from  batch to hosts
            for host, cmd in batch:
                self.net[host].sendCmd(cmd)

            # Wait for hosts from batch to complete and retrieve output
            fping_outputs = {}
            for host, _ in batch:
                fping_outputs[host] = self.net[host].waitOutput()

            # Optional sleep to give the system some rest
            time.sleep(0.5)

            # Parse the output of each command
            for src_host, fping_output in fping_outputs.items():

                result = self._parse_fping_output(fping_output)

                for k, v in result.items():
                    address = tuple(sorted([src_host, k]))
                    assert str(address) not in result_dict
                    result_dict[str(address)] = v

        # print(result_dict)

        return result_dict

    @property
    def name(self) -> str:
        return "FpingTestMultiBatch"
