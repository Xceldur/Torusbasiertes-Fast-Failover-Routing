# interface for rule inserter for different algorithm
import itertools
import os
import subprocess
from abc import ABC, abstractmethod
from collections import Counter
from typing import Tuple, Final
from tqdm import tqdm


class FailOverAlgorithm(ABC):
    def __init__(self, size_x: int, size_y: int, portInterfaceRelation: dict, macHostRelation: dict):
        self.__failOverInzilaized : bool = False
        if len(portInterfaceRelation) == 0 or len(macHostRelation) == 0:
            raise ValueError("ports and macs cannot be empty")

        self.macHostRelation = macHostRelation
        self._lookupTable: list[list[int]] = list()
        self.portInterfaceRelation = portInterfaceRelation
        if size_x < 3 or size_x > 255 or size_y < 3 or size_y > 255:
            raise ValueError('You have respect the limitations of the mininet implementation')
        self.X_SIZE: Final = size_x
        self.Y_SIZE: Final = size_y
        self.ovsComands: list[str] = []
        self.priorityCounter = {f's{x}x{y}': 0 for x in range(self.X_SIZE) for y in range(self.Y_SIZE)}

    # helper function to convert switch sting to tuple
    @staticmethod
    def _switchToTuple(switchAsString: str) -> (int, int):
        return tuple(map(int, switchAsString[1:].split('x')))

    # helper function to convert switch to mac
    def _switchHostToMAC(self, switch) -> str:
        if isinstance(switch, str):
            switch = self._switchToTuple(switch)
        host = f'h{switch[0]}x{switch[1]}'
        mac_address = self.macHostRelation[host]
        return mac_address

    # exicute ovs comands
    def exicuteOVS(self):
        if len(self.ovsComands) == 0:
            raise ValueError("There are no commands to run")
        print('Inserting Openflow Rules')
        for line in tqdm(self.ovsComands, unit='inserts'):
            # print(line)

            if line[0] == '#':
                continue
            else:
                # comand = ['ovs-ofctl', *line.split()]
                # subprocess.run(comand)
                os.system("ovs-ofctl " + line)

        self.ovsComands = []

    @abstractmethod
    def insertFailOverRules(self, dst: str) -> int:
        if not self.__failOverInzilaized:
            raise ValueError('You have to initialize the failover groups before running generate')
        pass

    def setUpFailOvertGroups(self, size: int = 4):
        self.__failOverInzilaized = True

        # buckets with respective output and erase for in_port since in_port=outport may be dropped
        # (not advised when it's not needed)
        buckets = ['bucket=watch_port:2,load:0->NXM_OF_IN_PORT[],output:2',
                   'bucket=watch_port:3,load:0->NXM_OF_IN_PORT[],output:3',
                   'bucket=watch_port:4,load:0->NXM_OF_IN_PORT[],output:4',
                   'bucket=watch_port:5,load:0->NXM_OF_IN_PORT[],output:5']

        if size != 4:
            raise NotImplementedError()

        # generate permutations
        permList = list(itertools.permutations([0, 1, 2, 3], size))
        # lookup table for failover groups
        for perm in permList:
            self._lookupTable.append(list(map(lambda x: x + 2, perm)))

        for x in range(self.X_SIZE):
            for y in range(self.Y_SIZE):
                for id in range(len(permList)):
                    currentOrder = permList[id]
                    self.ovsComands.append(f'-O OpenFlow15 add-group s{x}x{y} group_id={id},\"type=ff,'
                                           f'{buckets[currentOrder[0]]},'
                                           f'{buckets[currentOrder[1]]},'
                                           f'{buckets[currentOrder[2]]},'
                                           f'{buckets[currentOrder[3]]}\"')

    def setUpHostToSwitch(self):
        for x in range(self.X_SIZE):
            for y in range(self.Y_SIZE):
                self.ovsComands.append(f'-O OpenFlow15 add-flow s{x}x{y} '
                                       f'priority=65535,'
                                       f'dl_dst={self._switchHostToMAC((x, y))}'
                                       f',actions=output:1')
                self.priorityCounter[f's{x}x{y}'] += 1

    # get number of failovergroup
    def _get_failover_group(self, src: str, *fdst: str) -> int:
        if not 1 <= len(fdst) <= 4:
            raise ValueError("Invalid number of failover destinations")
        if len(self._lookupTable) == 0:
            raise ValueError("Failovergroups have not be inalazied or a lookup tabel have not been provided")

        searchEntry: list[int] = []
        missingNumber = {2, 3, 4, 5}

        for i in range(4):
            port: int
            if len(fdst) - 1 > i:
                port = int(self.portInterfaceRelation[src][fdst[i]])
                missingNumber.remove(port)
            else:
                port = missingNumber.pop()
            searchEntry.append(port)

        return self._lookupTable.index(searchEntry)
