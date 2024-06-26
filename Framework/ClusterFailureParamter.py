import itertools

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt

from experimente.failurePattern import ClusterFailurePattern

# self explaining Parameters for parameter tester
OUTPUT_STDOUT = True
SIZE_X: int = 7
SIZE_Y: int = 7
NUMBER_SIM: int = 15
POINT_D: str = 's3x3'
RANGE_P: tuple[float, float] = (0.3, 1)
RANGE_F: tuple[float, float] = (0.3, 1)
STEP_P: float = 0.005
STEP_F: float = 0.005

# plotting options
DRAW_PLOT: bool = True
NORM_PLOT: bool = True

# Create a torus graph in dimensions to test on
torusEdges: set[frozenset[str]] = set()
for x, y in itertools.product(range(SIZE_X), range(SIZE_Y)):
    torusEdges = torusEdges.union({frozenset(
        [f's{x}x{y}', f's{(x + 1) % SIZE_X}x{y}']
    )})
    torusEdges = torusEdges.union({frozenset(
        [f's{x}x{y}', f's{x}x{(y + 1) % SIZE_Y}']
    )})

G = nx.Graph()
G.add_edges_from(torusEdges)

if OUTPUT_STDOUT:
    print(f'Dimensions of G: {SIZE_X} * {SIZE_Y}')
    print('Number of Edges in G:', len(G.edges), '\n')
    # Table Header
    print("  p     |     f     | Max | Average | Median | Mode |  Min  ")
    print("-" * 59)

datapoints = list()

for p, f in itertools.product(np.arange(*RANGE_P, step=STEP_P), np.arange(*RANGE_F, step=STEP_F)):
    p: float = round(p, 3)
    f: float = round(f, 3)

    results = np.zeros(NUMBER_SIM, dtype=int)
    result_duplicate = np.zeros(NUMBER_SIM, dtype=int)

    for i in range(NUMBER_SIM):
        failedEdges = ClusterFailurePattern.simulate_failures(graph=G, d=POINT_D, p=p, f=f)
        results[i] = len(failedEdges)
        assert len(failedEdges) == len(set(failedEdges)), 'there can not be any duplicate edges'

    max_v = np.max(results)
    avg_v = np.mean(results)
    median_v = round(np.median(results))
    mode_v = np.bincount(results).argmax().round()
    min_v = np.min(results)

    datapoints.append((p, f, max_v, avg_v, median_v, mode_v, min_v))

    if OUTPUT_STDOUT:
        # Print results in a table format
        print(f"{p:^8.3f} | {f:^8.3f} | {max_v:^4} | {avg_v:^7.2f} | {median_v:^6} | {mode_v:^4} | {min_v:^5}")

# exit if no plot is requested
if not DRAW_PLOT:
    exit()
# Data
p_values = [t[0] for t in datapoints]
f_values = [t[1] for t in datapoints]
average_values = [t[4] for t in datapoints]

if NORM_PLOT:
    average_values = [t for t in average_values]

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(p_values, f_values, c=average_values, cmap='magma', s=100, alpha=0.7)

# Customize plot
plt.title('Scatter Plot of p and f in a 7x7 Torus')
plt.xlabel('p')
plt.ylabel('f')
plt.xlim(RANGE_P)
plt.ylim(RANGE_F)
plt.colorbar(label='median of deactivated Edges')

# Show plot
plt.grid(True)
plt.tight_layout()
plt.savefig('clusterfuck.pdf', bbox_inches='tight')
plt.show()
