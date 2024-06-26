import argparse

from mininet.cli import CLI

from experimente.ExperimentManager import ExperimentManager


# extend CLI Interface for running custom experiments
class CUSTOMCLI(CLI):
    prompt = 'mininetFailOver> '

    def __init__(self, mininet, *args, **kwargs):
        self.SIZE_X = kwargs.pop('size_x')
        self.SIZE_Y = kwargs.pop('size_y')
        super().__init__(mininet, *args, **kwargs)
        self.eM = ExperimentManager(net=mininet, x_size=self.SIZE_X, y_size=self.SIZE_Y)

    # print hello world to greet everyone out there
    def do_hello(self, line: str):
        print(f'Hello World! {line}')

    # TODO: Interface for expirement mangar
    def do_expirment(self, line):
        # parse arguments for experiment manager
        parser = argparse.ArgumentParser()

    # TODO. Some day swithch the ALGO on runtime?
    # 1) flush rules
    # 2) Load algo over fA? Nedd some investigating still.
    def do_switch_route_algo(self, line):
        print('Not Implementet, yet')


