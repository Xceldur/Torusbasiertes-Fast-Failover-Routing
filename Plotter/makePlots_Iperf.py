import itertools
import json
import statistics

import seaborn as sns
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

BANDWITH_LIMIT_ON_LINK = 100
MAKE_PLOT : bool= True
SHOW_DATA : bool = False
FILES_NAMES : list[tuple[str,str]] = [
    ('Low Stretch', 'test1.json'),
    ('Hamilton', 'test2.json'),
    ('Hamilton Low S.', 'test3.json')
]
SAVE_FIG : bool= False
OUTPUT_NAME : str = ''
X_TXT : str = 'Iteration (Ausgefallene Kanten)'
Y_TXT : str = 'Ausnutzung der Bandbreite'

def extractData_Iperf(filename: str):
    with open(filename) as json_file:
        json_data = json.load(json_file)

    # first extract useful information
    number_of_iteration = max(map(int, json_data.keys())) + 1
    number_of_exp = max(map(int, json_data['0'].keys())) + 1
    number_of_hosts_running = len(json_data['0']['0']['IperfAlltoAll']) * 2

    datarate_values_raw = [list() for _ in range(number_of_iteration)]
    datarate_values = [dict() for _ in range(number_of_iteration)]
    # datastructure of json data: [failurepattern iteration][exp iteration][name of expirment] [edge]
    for it in range(number_of_iteration):
        current_it = json_data[str(it)]
        zero_count = 0
        all_values_iterator = itertools.chain(
            *[current_it[str(exp)]['IperfAlltoAll'].values() for exp in range(number_of_exp)])

        all_values = list()
        for value in all_values_iterator:
            zero_count += 2
            if value['client_throughput'] is not None:
                all_values.append(value['client_throughput'])
                zero_count -= 1
            if value['server_throughput'] is not None:
                all_values.append(value['server_throughput'])
                zero_count -= 1


        datarate_values_raw[it] += all_values
        datarate_values[it]['avg'] = statistics.mean(all_values)
        datarate_values[it]['median'] = statistics.median(all_values)
        datarate_values[it]['max'] = max(all_values)
        datarate_values[it]['min'] = min(all_values)
        datarate_values[it]['std'] = statistics.stdev(all_values)
        datarate_values[it]['pstd'] = statistics.pstdev(all_values)
        datarate_values[it]['sum'] = sum(all_values)
        datarate_values[it]['zero_count'] = zero_count

    # next build sum for each exp
    datarate_sum = list()
    datarate_sum_relative = list()
    for it in range(number_of_iteration):
        sum_list = list()
        sum_list_relative = list()
        current_it = json_data[str(it)]

        for exp in range(number_of_exp):
            current_exp = current_it[str(exp)]['IperfAlltoAll']
            current_exp_thoughpus = [v for k, v in current_exp.items()]
            current_exp_thoughpus = ([v['client_throughput'] for v in current_exp_thoughpus]+
                                     [v['server_throughput'] for v in current_exp_thoughpus])
            sum_list.append(sum(filter(lambda x: x is not None, current_exp_thoughpus)))
            sum_list_relative.append(sum(filter(lambda x: x is not None, current_exp_thoughpus)) /
                                     (2*BANDWITH_LIMIT_ON_LINK*number_of_hosts_running))

        datarate_sum.append(sum_list)
        datarate_sum_relative.append(sum_list_relative)

    return {'datarate_sum': datarate_sum,
            'datarate_sum_relative': datarate_sum_relative,
            'datarate_values_raw': datarate_values_raw,
            'datarate_values': datarate_values}



if __name__ == '__main__':
    # create plot folder
    Path("plots").mkdir(exist_ok=True)

    results_evaluation = []

    for algo_name, filename in FILES_NAMES:
        results_evaluation.append((algo_name, extractData_Iperf(filename)))

    data_set_to_plot = list()
    for result in results_evaluation:
        data_iperf = result[1]['datarate_sum']
        algo_name = result[0]

        for index, it_samples in enumerate(data_iperf):
            for failre_v in it_samples:
                data_set_to_plot.append((index, algo_name, failre_v))

        if SHOW_DATA:
            print(f'Algo: {algo_name}')
            for i,e in enumerate(result[1]['datarate_values']):
                print(i, ':', e)

    if not MAKE_PLOT:
        exit()

    data_pd = pd.DataFrame(columns=['it', 'algo', 'failure_rate'], data=data_set_to_plot)
    sns.set(rc={'figure.figsize': (12, 6)})
    sns.set_style("whitegrid")
    sns.boxplot(x='it', y='failure_rate', hue='algo',
                data=data_pd, showfliers=True, showmeans=True)
    plt.ylabel(Y_TXT)
    plt.xlabel(X_TXT)
    plt.legend(title='Failover Algorithm')
    if SAVE_FIG:
        plt.savefig(f"plots/plots{OUTPUT_NAME}.pdf", bbox_inches='tight', dpi=300)
    plt.show()
