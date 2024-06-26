import itertools
import random
import statistics
from typing import Final, Iterable, Iterator, List, FrozenSet

import networkx as nx
import numpy as np

from experimente.failurePattern import ClusterFailurePattern
from network.Utility import Utility


class FailurePatternFactory:
    def __init__(self, size_x, size_y, amount_of_edges: int = 0, exclude_edges: list[frozenset[str]] = None,
                 yield_none_first: bool = True):
        self.NUMBER_OF_EDGES: Final[int] = (2 * size_x * size_y)
        self.yield_none_first = yield_none_first
        if exclude_edges is None:
            exclude_edges = set()
        if size_x < 3 or size_y < 3:
            raise ValueError("The size of the torus is invalid")
        if amount_of_edges >= self.NUMBER_OF_EDGES:
            raise ValueError("There can not be more edges than the total amount")
        if amount_of_edges <= 0:
            amount_of_edges = self.NUMBER_OF_EDGES

        self.amount = amount_of_edges
        self.SIZE_Y: Final[int] = size_y
        self.SIZE_X: Final[int] = size_x

        # generate all edges in the torus
        self._torusEdges: list[frozenset[str]] = list()
        for x, y in itertools.product(range(size_x), range(size_y)):
            self._torusEdges.append(frozenset(
                [f's{x}x{y}', f's{(x + 1) % size_x}x{y}']
            ))
            self._torusEdges.append(frozenset(
                [f's{x}x{y}', f's{x}x{(y + 1) % size_y}']
            ))
        self._torusEdges_complete = self._torusEdges.copy()

        # remove edges to exclude if not none
        if exclude_edges is not None:
            for e in exclude_edges:
                self._torusEdges.remove(e)

    def edges(self, links_to_deactivate: list[frozenset[str]], block_size: int = 1) -> Iterator[list[frozenset[str]]]:
        """
            Returns a block of edges according to the requested size and provided edges.
            Note: This pattern does not honor the requested exclusions
        """
        if self.yield_none_first:
            self.yield_none_first = False
            yield []

        if block_size < 1:
            raise ValueError("The block size cannot be less than 1")

        while len(links_to_deactivate) > 0 or self.amount > 0:
            block = [links_to_deactivate.pop(0) for _ in range(min(block_size, len(links_to_deactivate)))]
            self.amount = - 1
            yield block

    def nodes(self, switches_to_deactivate: list[str]) -> Iterator[list[frozenset[str]]]:
        edges_to_deactivate: list[frozenset[str]] = list()

        # generate all edges around each node that should be "deactivated"
        for node in switches_to_deactivate:
            switch_x, switch_y = Utility.switchToTuple(node)
            edges_to_deactivate += [
                frozenset({node, f's{(switch_x + 1) % self.SIZE_X}x{switch_y}'}),
                frozenset({node, f's{(switch_x - 1) % self.SIZE_X}x{switch_y}'}),
                frozenset({node, f's{switch_x}x{(switch_y + 1) % self.SIZE_Y}'}),
                frozenset({node, f's{switch_x}x{(switch_y - 1) % self.SIZE_Y}'})
            ]

        # eliminate duplicates (source: https://www.geeksforgeeks.org/python-ways-to-remove-duplicates-from-list/)
        edges_to_deactivate = [i for n, i in enumerate(edges_to_deactivate) if i not in edges_to_deactivate[:n]]

        return self.edges(links_to_deactivate=list(edges_to_deactivate), block_size=4)

    def randomEdges(self, seed=None) -> Iterator[list[frozenset[str]]]:
        random.seed(seed)
        edges = random.sample(self._torusEdges, len(self._torusEdges))
        print(edges)
        return self.edges(edges, block_size=1)

    def randomNodes(self, seed=None) -> Iterator[list[frozenset[str]]]:
        random.seed(seed)
        all_switches = [f's{x}x{y}' for x, y in itertools.product(range(self.SIZE_X), range(self.SIZE_Y))]
        random.shuffle(all_switches)
        return self.nodes(all_switches)

    # failure pattern where p and/or q from cluster failure is stepped each iteration.

    def clusterFailureStep(self, nodes_d: list[str],
                           step_p: float = None, interval_p: tuple[float, float] = None, p=None,
                           step_q: float = None, interval_q: tuple[float, float] = None, q=None,
                           seed=None) -> Iterator[list[frozenset[str]]]:

        assert (step_p is not None and interval_p is not None) or p is not None, 'interval q or p constant'
        assert (step_q is not None and interval_q is not None) or q is not None, 'interval q or q constant'

        if self.yield_none_first:
            self.yield_none_first = False
            yield []

        # set step so only one value will be generated
        product_it_p = [p] if p is not None else np.arange(*interval_p, step=step_p)
        product_it_q = [q] if q is not None else np.arange(*interval_q, step=step_q)

        G = nx.Graph()
        G.add_edges_from(self._torusEdges)

        for p_it, f_it in itertools.product(product_it_p, product_it_q):
            edges_to_fail = (
                set(*[ClusterFailurePattern.simulate_failures(graph=G, d=node, p=p_it, f=f_it) for node in nodes_d]))
            yield list(edges_to_fail)

    # failure pattern where p and q for cluster failure where p,q is fixed,
    # but the number of nodes increases each interation
    def clusterFailureIncreaseNodes(self, nodes_d: list[str] = None, p: float = 0.9, q: float = 0.34, seed=None) \
            -> Iterator[list[frozenset[str]]]:

        if self.yield_none_first:
            self.yield_none_first = False
            yield []

        # if no nodes are set generate them randomly after seed
        if nodes_d is None:
            all_switches = [f's{x}x{y}' for x, y in itertools.product(range(self.SIZE_X), range(self.SIZE_Y))]
            random.seed(seed)
            random.shuffle(all_switches)
            nodes_d = all_switches

        G = nx.Graph()
        G.add_edges_from(self._torusEdges)

        edges_to_fail = set()
        for node in nodes_d:
            edges_to_fail.update(ClusterFailurePattern.simulate_failures(G, node, p, q, seed))
            yield list(edges_to_fail)

    def towardsNodeBFS(self, dst_node: str, keep_a_way=True, seed=None) -> Iterator[list[frozenset[str]]]:
        # edges_to_deactivate = list(self._torusEdges)
        # edges_to_deactivate.sort()

        if self.yield_none_first:
            self.yield_none_first = False
            yield []

        torus_graph: nx.Graph = nx.from_edgelist(list(self._torusEdges))
        torus_graph_bfs = list(nx.bfs_edges(G=torus_graph, source=dst_node, sort_neighbors=Utility.shuffled_neighbors))
        edges_to_deactivate = []

        # remove edge, then test weather graph is still connected.
        # if that's not the case reverse removal of edge and do not deactivate edge
        while len(torus_graph_bfs) > 0:
            edge = torus_graph_bfs.pop(0)
            torus_graph.remove_edge(*edge)

            if keep_a_way and not nx.is_connected(torus_graph):
                torus_graph.add_edge(*edge)
                continue

            edges_to_deactivate.append(frozenset(edge))

        return self.edges(edges_to_deactivate, block_size=1)

    def getByName(self, failure_pattern_name: str, **kwargs):
        method = getattr(self, failure_pattern_name, None)
        if method:
            method(*kwargs)
        else:
            print(f"Failure Pattern '{failure_pattern_name}' not found!")
