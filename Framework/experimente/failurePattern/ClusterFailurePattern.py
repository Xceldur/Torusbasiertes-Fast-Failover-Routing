import random
from typing import Set

import networkx as nx


def simulate_failures(graph: nx.Graph, d: str, p: float, f: float, seed=None):
    assert graph.has_node(d), 'D has to be a node of the graph'
    assert 0 <= p <= 1, 'p has to be between 0 and 1'

    # seed random generator
    random.seed(seed)

    # Initialize a dictionary to store failure probabilities
    failure_probabilities = {frozenset(edge): 0 for edge in graph.edges()}

    # Start with the edges directly connected to node d
    for neighbor in graph.neighbors(d):
        failure_probabilities[frozenset((d, neighbor))] = p

    # Maintain a set of failed edges
    failed_edges: Set[frozenset[str]] = set()

    # BFS to propagate failure probabilities
    queue = [(neighbor, p, 1) for neighbor in graph.neighbors(d)]

    while queue:
        current_node, current_prob, hops = queue.pop(0)

        for neighbor in graph.neighbors(current_node):
            if neighbor != d:  # Avoid going back to the starting node
                edge = frozenset((current_node, neighbor))
                propagated_prob = current_prob * (f ** hops)

                # Check if the neighbor edge is already failed
                if edge in failed_edges:
                    propagated_prob = max(propagated_prob, failure_probabilities[edge])

                if propagated_prob > failure_probabilities[edge]:
                    failure_probabilities[edge] = propagated_prob
                    queue.append((neighbor, propagated_prob, hops + 1))

                    # Add edge to failed set if failure occurs
                    if random.random() < propagated_prob:
                        failed_edges.add(edge)

    return list(failed_edges)
