import itertools
from typing import override

import networkx as nx

from algoritmen.FailOverAlgoritmen import FailOverAlgorithm


class HamiltonCircutFailover(FailOverAlgorithm):

    def __init__(self, size_x: int, size_y: int, portInterfaceRelation: dict, macHostRelation):
        super().__init__(size_x, size_y, portInterfaceRelation, macHostRelation)

        if size_x % 2 == 0 or size_y % 2 == 0:
            raise ValueError('Only odd dimensions are supported')
        self.numberOfNodes = size_x * size_y

        # generate the two hamilton path and a lookup tabel for each node
        h1, h2 = self._generateHamilton()
        assert h1, h2 == self.numberOfNodes
        self.h_LookUp: dict[str, dict[str, str]] = self.__generateHamiltonLookUp(h1, h2)
        self.rules_already_inserted: bool = False
        self.h1 = h1
        self.h2 = h2

    def _generateHamilton(self):  # TODO: Revise bigger than 3 torus
        torusGraph = nx.Graph()
        h1_graph: nx.Graph = nx.Graph()
        h2_graph: nx.Graph
        # initialize 2d torus
        for x in range(self.X_SIZE):
            for y in range(self.Y_SIZE):
                torusGraph.add_edge(f's{x}x{y}', f's{(x + 1) % self.X_SIZE}x{y}')
                torusGraph.add_edge(f's{x}x{y}', f's{x}x{(y + 1) % self.Y_SIZE}')

        # calculate the first hamilton path according to the construction from the paper
        # flurtstück 1
        h1_graph.add_edge('s0x0', 's1x0')
        for i in range((self.Y_SIZE - 1) // 2):
            offset = i * 2
            plot = [(f's0x{offset + 0}', f's0x{offset + 1}'),
                    (f's0x{offset + 1}', f's1x{offset + 1}'),
                    (f's1x{offset + 1}', f's1x{offset + 2}'),
                    (f's1x{offset + 2}', f's0x{offset + 2}')]
            h1_graph.add_edges_from(plot)
        # flurstürck 2
        h1_graph.add_edge(f's0x{self.Y_SIZE - 1}', f's{self.X_SIZE - 1}x{self.Y_SIZE - 1}')
        for j in range(self.Y_SIZE - 1, 0, -1):
            h1_graph.add_edge(f's{self.X_SIZE - 1}x{j}', f's{self.X_SIZE - 1}x{j - 1}')
        h1_graph.add_edge(f's{self.X_SIZE - 1}x0', f's{self.X_SIZE - 2}x0')
        # flurstück 3
        for i in range((self.X_SIZE - 3) // 2):
            offset = i * 2
            for j in range(self.Y_SIZE - 1):
                h1_graph.add_edge(f's{self.X_SIZE - 2 - offset}x{j}',
                                  f's{self.X_SIZE - 2 - offset}x{j + 1}')
            h1_graph.add_edge(f's{self.X_SIZE - 2 - offset}x{self.Y_SIZE - 1}',
                              f's{self.X_SIZE - 3 - offset}x{self.Y_SIZE - 1}')

            for j in range(self.Y_SIZE - 1, 0, -1):
                h1_graph.add_edge(f's{self.X_SIZE - 3 - offset}x{j}',
                                  f's{self.X_SIZE - 3 - offset}x{j - 1}')
            h1_graph.add_edge(f's{self.X_SIZE - 3 - offset}x0',
                              f's{self.X_SIZE - 4 - offset}x0')
        #  the second Hamilton path consists of all edges that are not in h1
        h2_graph = nx.difference(torusGraph, h1_graph)

        # assert h1 and h2 contains the same nodes as the torus and have as many edges
        assert set(h1_graph.nodes) == set(torusGraph.nodes), 'h1 does not contain all nodes'
        assert set(h1_graph.nodes) == set(torusGraph.nodes), 'h2 does not contain all nodes'
        assert len(h1_graph.edges) == len(h2_graph.edges) == len(torusGraph.edges) / 2, ('h1 edges and h2 edge len is '
                                                                                         'wrong')
        # assert that h1 and h2 are in fact disjoint and in union a torus
        assert nx.symmetric_difference(h1_graph, h2_graph).edges == torusGraph.edges, 'h1 and h2 are not disjoint'
        # assert that h1 and h2 are connected
        assert nx.is_connected(h1_graph) and nx.is_connected(h2_graph), 'h1 or h2 is not connected'

        # transverse hamilton path graphs and return lists
        return (list(nx.dfs_preorder_nodes(G=h1_graph, source='s0x0')),
                list(nx.dfs_preorder_nodes(G=h2_graph, source='s0x0')))

    def __generateHamiltonLookUp(self, h1: list[str], h2: list[str]):
        # Initialize an empty dictionary to store the Hamiltonian look-up table
        h_LookUp: dict[str, dict[str, str]] = {}
        # Iterate over every node in the torus with coordinates (x, y)
        for x in range(self.X_SIZE):
            for y in range(self.Y_SIZE):
                # Calculate the index of the current node in both Hamiltonian cycle
                nodeIndex_h1 = h1.index(f's{x}x{y}')
                nodeIndex_h2 = h2.index(f's{x}x{y}')
                # Create a sub-dictionary for the current node and its neighbors in both cycle
                h_LookUp[f's{x}x{y}'] = {'h1_f': h1[(nodeIndex_h1 + 1) % self.numberOfNodes],
                                         'h1_b': h1[(nodeIndex_h1 - 1) % self.numberOfNodes],
                                         'h2_f': h2[(nodeIndex_h2 + 1) % self.numberOfNodes],
                                         'h2_b': h2[(nodeIndex_h2 - 1) % self.numberOfNodes]}

        return h_LookUp

    def _generateStartRule(self, switch_src):
        # rule 1: inport=1 (host), output: h1_f, h1_b, h2_f, h2_b [start first cycle form host]
        self.ovsComands.append(f'-O OpenFlow15 add-flow {switch_src} '
                               f'priority=6,'
                               f'in_port=1,'
                               f'actions=group:'
                               f'{self._get_failover_group(switch_src,
                                                           self.h_LookUp[switch_src]['h1_f'],
                                                           self.h_LookUp[switch_src]['h1_b'],
                                                           self.h_LookUp[switch_src]['h2_f'],
                                                           self.h_LookUp[switch_src]['h2_b']
                                                           )}')

    def _generateFailOverRules(self, switch_src):
        # rule 2: inport=h1_b, output: h1_f, h2_f, h2_b [first hamilton cycle]
        self.ovsComands.append(f'-O OpenFlow15 add-flow {switch_src} '
                               f'priority=5,'
                               f'in_port={self.portInterfaceRelation[switch_src][
                                   self.h_LookUp[switch_src]['h1_b']]},'
                               f'actions=group:'
                               f'{self._get_failover_group(switch_src,
                                                           self.h_LookUp[switch_src]['h1_f'],
                                                           self.h_LookUp[switch_src]['h1_b'],
                                                           self.h_LookUp[switch_src]['h2_f'],
                                                           self.h_LookUp[switch_src]['h2_b']
                                                           )}'
                               )
        # rule 3: inport=h1_f, output: h1_b ,h2_f, h2_b [first hamilton cycle backwards]
        self.ovsComands.append(f'-O OpenFlow15 add-flow {switch_src} '
                               f'priority=4,'
                               f'in_port={self.portInterfaceRelation[switch_src]
                               [self.h_LookUp[switch_src]['h1_f']]},'
                               f'actions=group:'
                               f'{self._get_failover_group(switch_src,
                                                           self.h_LookUp[switch_src]['h1_b'],
                                                           self.h_LookUp[switch_src]['h2_f'],
                                                           self.h_LookUp[switch_src]['h2_b'],
                                                           self.h_LookUp[switch_src]['h1_f']
                                                           )}'
                               )

        # rule 4: inport:h2_b, output: h2_f [second hamilton cycle forwards]
        self.ovsComands.append(f'-O OpenFlow15 add-flow {switch_src} '
                               f'priority=3,'
                               f'in_port={self.portInterfaceRelation[switch_src]
                               [self.h_LookUp[switch_src]['h2_b']]},'
                               f'actions=group:'
                               f'{self._get_failover_group(switch_src,
                                                           self.h_LookUp[switch_src]['h2_f'],
                                                           self.h_LookUp[switch_src]['h2_b'],
                                                           self.h_LookUp[switch_src]['h1_f'],
                                                           self.h_LookUp[switch_src]['h1_b']
                                                           )}'
                               )

        # rule 5: in_port:h2_f, output: h2_b [second hamitlon cycle backwards]
        self.ovsComands.append(f'-O OpenFlow15 add-flow {switch_src} '
                               f'priority=2,'
                               f'in_port={self.portInterfaceRelation[switch_src]
                               [self.h_LookUp[switch_src]['h2_f']]},'
                               f'actions=group:'
                               f'{self._get_failover_group(switch_src,
                                                           self.h_LookUp[switch_src]['h2_b'],
                                                           self.h_LookUp[switch_src]['h1_f'],
                                                           self.h_LookUp[switch_src]['h1_b'],
                                                           self.h_LookUp[switch_src]['h2_f']
                                                           )}'
                               )

    @override
    def insertFailOverRules(self, dst: str) -> int:
        super().insertFailOverRules(dst)
        # since no dst is needed for the algo, the rules are only need to be inserted once
        if self.rules_already_inserted:
            return 0

        self.rules_already_inserted = True

        for y in range(self.Y_SIZE):
            for x in range(self.X_SIZE):
                switch_src = f's{x}x{y}'
                # generate rules [first start rule form switch, then subsequent failoverrules]
                self._generateStartRule(switch_src)
                self._generateFailOverRules(switch_src)

        return 0


class HamiltonCircuitFailoverLowStretch(HamiltonCircutFailover):

    def calculateOpptunStartCycle(self, switch_src, switch_dst):
        # assert src is not dst
        assert switch_dst != switch_src
        # get iciest of dst on the hamilton path and offset by source dst
        h1_idc_dst = self.h1.index(switch_dst)
        h2_idc_dst = self.h2.index(switch_dst)
        h1_idc_source = self.h1.index(switch_src)
        h2_idc_source = self.h2.index(switch_src)

        # generate distances from indices and sort it
        distances_hamilton_paths: list = [
            ('h1_f',  (h1_idc_dst - h1_idc_source) % self.numberOfNodes),
            ('h2_f',  (h2_idc_dst - h2_idc_source) % self.numberOfNodes),
            ('h1_b', -(h1_idc_dst - h1_idc_source) % self.numberOfNodes),
            ('h2_b', -(h2_idc_dst - h2_idc_source) % self.numberOfNodes),
        ]

        min_path, min_dist = min(distances_hamilton_paths, key=lambda x: x[1])
        return min_path

    def _generateStartRuleWithOpptunChoice(self, switch_src, switch_dst):
        cycleSequence = ['h1_f', 'h1_b', 'h2_f', 'h2_b']
        shiftindex = cycleSequence.index(self.calculateOpptunStartCycle(switch_src=switch_src, switch_dst=switch_dst))

        print(f'src:{switch_src}, dst:{switch_dst}, cycle:{cycleSequence[shiftindex]}')

        self.ovsComands.append(f'-O OpenFlow15 add-flow {switch_src} '
                               f'priority=6,'
                               f'dl_dst={self._switchHostToMAC(switch_dst)},'
                               f'in_port=1,'
                               f'actions=group:'
                               f'{self._get_failover_group(switch_src,
                                                           self.h_LookUp[switch_src][cycleSequence[(shiftindex + 0) % 4]],
                                                           self.h_LookUp[switch_src][cycleSequence[(shiftindex + 1) % 4]],
                                                           self.h_LookUp[switch_src][cycleSequence[(shiftindex + 2) % 4]],
                                                           self.h_LookUp[switch_src][cycleSequence[(shiftindex + 3) % 4]]
                                                           )}')

    @override
    def insertFailOverRules(self, dst: str) -> int:
        for x, y in itertools.product(range(self.X_SIZE), range(self.Y_SIZE)):
            switch_src = f's{x}x{y}'

            if dst == switch_src:
                continue

            self._generateStartRuleWithOpptunChoice(switch_src=switch_src, switch_dst=dst)

        # insert failover rules that only depend on in_port only once
        if self.rules_already_inserted:
            return 0
        self.rules_already_inserted = True
        for x, y in itertools.product(range(self.X_SIZE), range(self.Y_SIZE)):
            self._generateFailOverRules(switch_src=f's{x}x{y}')
