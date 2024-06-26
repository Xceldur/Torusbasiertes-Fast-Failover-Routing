import itertools
import json
import statistics
from pathlib import Path

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# insert filenames and name of algorithm as tuple (name, filename)
FILES_NAMES : list[tuple[str,str]] = [
    ('Low Stretch', 'ExpResults_lowStretch.json'),
    #('Low S. Aug.', 'ExpResults_lowStretchAug.json'),
    #('Hamilton', 'ExpResults_hamilton.json'),
    #('Hamilton Low S.', 'ExpResults_hamilton_LowStretch.json'),
    #('Hamilton Low S. Aug.', 'ExpResults_hamiltonLowStretchAug.json')
]
ITERATIONS_TO_PLOT_LATENCY = 11
ITERATIONS_TO_PLOT_FILTRATE = 100

def extractData_Fping(filename: str):
    with open(filename) as json_file:
        json_data = json.load(json_file)

    # first extract useful information
    number_of_iteration = max(map(int, json_data.keys())) + 1
    number_of_exp = max(map(int, json_data['0'].keys())) + 1

    # datastructure of json data: [failurepattern iteration][exp iteration][name of expirment] [edge]

    # first calculate median of ping results
    for it, exp_it in itertools.product(range(number_of_iteration), range(number_of_exp)):

        for edge, ping_probes in json_data[str(it)][str(exp_it)]['FpingTestMultiBatch'].items():
            # filter none for median calculation
            ping_probes = list(filter(lambda item: item is not None, ping_probes))
            # set to none if list of values is empty
            json_data[str(it)][str(exp_it)]['FpingTestMultiBatch'][edge] = \
                None if len(ping_probes) == 0 else statistics.median(ping_probes)

    # following the calculation of failure rates[it][min/max/avg/mean/stdv/pstddev]
    # also the raw data will be safe for diagrams later
    absolute_failure_rates = [dict() for _ in range(number_of_iteration)]
    absolute_failure_rates_raw = list()
    relative_failure_rates_raw = list()
    ping_aggregates = [dict() for _ in range(number_of_iteration)]
    for it in range(number_of_iteration):
        current_it = json_data[str(it)]
        failure_rate_exp = list()
        relative_failure_rate_exp = list()

        for exp in range(number_of_exp):
            current_exp = current_it[str(exp)]['FpingTestMultiBatch']
            failure_rate_exp.insert(
                exp, ([ping_probe_median for _, ping_probe_median in current_exp.items()].count(None)))
            relative_failure_rate_exp.insert(
                exp, ([ping_probe_median for _,
                ping_probe_median in current_exp.items()].count(None)/len(current_exp)))

        absolute_failure_rates_raw.append(failure_rate_exp)
        relative_failure_rates_raw.append(relative_failure_rate_exp)

        absolute_failure_rates[it]['avg'] = statistics.mean(failure_rate_exp)
        absolute_failure_rates[it]['median'] = statistics.median(failure_rate_exp)
        absolute_failure_rates[it]['max'] = max(failure_rate_exp)
        absolute_failure_rates[it]['min'] = min(failure_rate_exp)
        absolute_failure_rates[it]['std'] = statistics.stdev(failure_rate_exp)
        absolute_failure_rates[it]['pstd'] = statistics.pstdev(failure_rate_exp)

    # next the latency again we calculate [it][min/max/avg/median/stdv/pstdv/sum/filterd_None]
    # there are multiple solution for handling packet that did not arrive
    # yet it seems most sensible delete values, beacuse elsewhise a bias would be induced
    """
    for it in range(number_of_iteration):
        current_it = json_data[str(it)]
        all_latencys_exp = [for exp in current_it[str(exp)]['FpingTestMultiBatch']]
    """
    latency_rates = [dict() for _ in range(number_of_iteration)]
    latency_rates_raw = list()
    for it in range(number_of_iteration):
        current_it = json_data[str(it)]
        # chain all ping in one list and filter none
        all_exp_values_with_none = list(itertools.chain(
            *[current_it[str(exp)]['FpingTestMultiBatch'].values() for exp in range(number_of_exp)]))
        all_exp_values_filterd = list(filter(lambda x: x is not None, all_exp_values_with_none))

        latency_rates[it]['avg'] = statistics.mean(all_exp_values_filterd)
        latency_rates[it]['median'] = statistics.median(all_exp_values_filterd)
        latency_rates[it]['max'] = max(all_exp_values_filterd)
        latency_rates[it]['min'] = min(all_exp_values_filterd)
        latency_rates[it]['std'] = statistics.stdev(all_exp_values_filterd)
        latency_rates[it]['pstd'] = statistics.pstdev(all_exp_values_filterd)
        latency_rates[it]['deleted_values'] = (len(all_exp_values_with_none) - len(all_exp_values_filterd))

        latency_rates_raw.append(all_exp_values_filterd)

    return {
        'latency_rates_raw': latency_rates_raw,
        'latency_rates': latency_rates,
        'absolute_failure_rates': absolute_failure_rates,
        'absolute_failure_rates_raw': absolute_failure_rates_raw,
        'relative_failure_rates_raw' : relative_failure_rates_raw,
    }


if __name__ == '__main__':
    # create plot folder
    Path("plots").mkdir(exist_ok=True)

    results_evaluation = []
    for algo_name, filename in FILES_NAMES:
        results_evaluation.append((algo_name, extractData_Fping(filename)))

    # print statistics
    for algo_name, result in results_evaluation:
        print(algo_name, ':')
        print('--- Erreichbarkeit ---')
        for e in result['absolute_failure_rates_raw']:
            print(e)
        #print('--- Latencys ---')
        #for e in result['latency_rates']:
         #   print(e)

    data_set_to_plot_failurerate = list()

    # no edge failure since that case was not tested after data collection with failure pattern
    data_set_to_plot_latency = list()
    # make plot for failure rate
    for result in results_evaluation:
        data_failurerate = result[1]['relative_failure_rates_raw']
        data_latency = result[1]['latency_rates_raw']
        algo_name = result[0]

        for index, it_samples in enumerate(data_failurerate):
            for failre_v in it_samples:
                data_set_to_plot_failurerate.append((index + 1, algo_name, failre_v))
        #data_set_to_plot_failurerate.append((0, algo_name, 0))

        for index, it_samples in enumerate(data_latency):
            if index >= 13:
                continue
            for lat_v in it_samples:
                data_set_to_plot_latency.append((index + 1, algo_name, lat_v))


    # make plot for not delivered pings
    data_pd = pd.DataFrame(columns=['it', 'algo', 'failure_rate'], data=data_set_to_plot_failurerate)
    sns.set(rc={'figure.figsize': (12, 6)})
    sns.set_style("whitegrid")
    sns.boxplot(x='it', y='failure_rate', hue='algo',
                data=data_pd, showfliers=False, medianprops={"linewidth": 2})
    plt.ylabel('unzustellbare Pings in %')
    plt.xlabel('Iteration (Ausgefallene Kanten)')
    plt.legend(title='Failover Algorithm')
    plt.savefig("plots/junck.pdf", bbox_inches='tight', dpi=300)
    plt.show()

    # make plot for latenc rates
    sns.set(rc={'figure.figsize': (12, 6)})
    sns.set_style("whitegrid")
    data_pd = pd.DataFrame(columns=['it', 'algo', 'latency_rate'], data=data_set_to_plot_latency)
    sns.boxplot(x='it', y='latency_rate', hue='algo', data=data_pd,
                showfliers=False, whis=3, log_scale=2, medianprops={"color": "m", "linewidth": 2})
    plt.ylabel('Latenzraten in ms')
    plt.xlabel('Iteration (Ausgefallene Kanten)')
    plt.legend(title='Failover Algorithm')
    plt.savefig("plots/junck.pdf", bbox_inches='tight', dpi=300)
    plt.show()
