import itertools
import json
import statistics

import seaborn as sns
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

BANDWITH_LIMIT_ON_LINK = 100
MAKE_PLOT: bool = True
SHOW_DATA: bool = False
FILES_NAMES: list[tuple[str, str]] = [
    ('Low Stretch', 'test1.json'),
    ('Hamilton', 'test2.json'),
    ('Hamilton Low S.', 'test3.json')
]
SAVE_FIG: bool = True
OUTPUT_NAME: str = 'SingelDestTowardDest'
X_TXT: str = 'Iteration (Ausgefallene Kanten)'
Y_TXT: str = 'Datenrate Ausnutzung'


def extractData_IperfSingel(filename: str):
    with open(filename) as json_file:
        json_data = json.load(json_file)

    # first extract useful information
    number_of_iteration = max(map(int, json_data.keys())) + 1
    number_of_exp = max(map(int, json_data['0'].keys())) + 1
    number_of_hosts_running = len(json_data['0']['0']['IperfSingleToAll'])

    datapoints = [None for i in range(number_of_iteration)]

    for it in range(number_of_iteration):
        current_it = json_data[str(it)]
        server_rates = list(map(lambda x: x / (BANDWITH_LIMIT_ON_LINK * 4),
                                filter(lambda x: x != None,
                                       [current_it[str(exp)]['IperfSingleToAll']['server']
                                        for exp in range(number_of_exp)])))
        client_sums = [0 for _ in range(number_of_exp)]

        for exp in range(number_of_exp):
            for k, v in current_it[str(exp)]['IperfSingleToAll'].items():
                if k == 'server' or v == None:
                    continue
                client_sums[exp] += v
            client_sums[exp] /= BANDWITH_LIMIT_ON_LINK*4

        datapoints[it] = server_rates + client_sums

    return datapoints


if __name__ == '__main__':
    # create plot folder
    Path("plots").mkdir(exist_ok=True)

    results_evaluation = []

    for algo_name, filename in FILES_NAMES:
        results_evaluation.append((algo_name, extractData_IperfSingel(filename)))

    data_set_to_plot = list()
    for result in results_evaluation:
        data_iperf = result[1]
        algo_name = result[0]

        for index, it_samples in enumerate(data_iperf):
            for failre_v in it_samples:
                data_set_to_plot.append((index + 1, algo_name, failre_v))

        if SHOW_DATA:
            print(f'Algo: {algo_name}')
            for i, e in enumerate(result[1]):
                print(i, ':', e)

    if not MAKE_PLOT:
        exit()

    data_pd = pd.DataFrame(columns=['it', 'algo', 'failure_rate'], data=data_set_to_plot)
    sns.set(rc={'figure.figsize': (12, 6)})
    sns.set_style("whitegrid")
    sns.boxplot(x='it', y='failure_rate', hue='algo',
                data=data_pd, showfliers=False)
    plt.ylabel(Y_TXT)
    plt.xlabel(X_TXT)
    plt.legend(title='Failover Algorithm')
    if SAVE_FIG:
        plt.savefig(f"plots/plots{OUTPUT_NAME}.pdf", bbox_inches='tight', dpi=300)
    plt.show()
