import json
from datetime import datetime
from typing import Final, Iterator

import mininet

from experimente import Experiment


class ExperimentManager:  # TODO: Write json
    def __init__(self, x_size, y_size, net: mininet, filename: str = '', save_file: bool = False) -> None:
        self.net = net
        self.save_file = save_file
        self.filename = filename
        self._switchLinks: list[set[str]] = []
        self.Y_SIZE: Final[int] = y_size
        self.X_SIZE: Final[int] = x_size
        self._experiments: list[Experiment] = []

        if filename == '':
            self.filename = datetime.now().strftime("ExpResults_%m-%d-%Y-%H:%M:%S") + '.json'

        # create a set of all edges in the torus
        for x in range(self.X_SIZE):
            for y in range(self.Y_SIZE):
                self._switchLinks.append({f's{x}x{y}', f's{(x + 1) % self.X_SIZE}x{y}'})
                self._switchLinks.append({f's{x}x{y}', f's{x}x{(y + 1) % self.Y_SIZE}'})

    def attach(self, *experiment: Experiment) -> None:
        if len(experiment) == 0:
            raise ValueError("You can not add empty experiment.")

        self._experiments += list(experiment)

    def detach(self, experiment: Experiment) -> None:
        self._experiments.remove(experiment)

    def detach_all(self) -> None:
        self._experiments = []

    def clear(self) -> None:
        self._experiments = []

    def config(self):
        pass

    def run(self, failure_pattern=None):
        if failure_pattern is None:
            failure_pattern = iter(())

        results: list = list()
        all_deactivated_link = []

        for edges in failure_pattern:  # type: list[frozenset[str]]
            assert all(map(lambda x: type(x) is frozenset and len(x) == 2, edges)), ('the failure pattern does not'
                                                                                     'return an edge')

            self._deactivateLinks(edges)
            all_deactivated_link += edges
            edges_serializable = list(map(lambda x: list(x), all_deactivated_link))

            result_dict = dict()
            try:
                result_dict = {
                                  'deactivated': edges_serializable,
                              } | self.singleRun(all_deactivate_links=all_deactivated_link)
            except Exception as e:
                print(e)
                print(f'Error occurred: {edges_serializable} | {e}')
                break
            print(result_dict)
            results.append(result_dict)

        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4, )

        # afterward restore connectivity between all links
        self._restore()

    def aggregatedRun(self, failure_pattern_list: list[Iterator[list[frozenset[str]]]], iterations) -> dict:
        assert len(failure_pattern_list) > 0, 'You need add at least one failure pattern.'

        # Initialize the result storage
        results = {iteration: {} for iteration in range(iterations)}

        # keep track of all edges to fail for each failure pattern
        trackList = [list() for _ in range(len(failure_pattern_list))]

        for fail_iteration in range(iterations):
            print(f'Iteration {fail_iteration}')
            for failure_pattern_index in range(len(failure_pattern_list)):
                # append new edges to fail to track list and fail them
                trackList[failure_pattern_index] += next(failure_pattern_list[failure_pattern_index])
                # print current failure pattern and deactivated edges
                print(f'\tFailure pattern: {failure_pattern_index}')
                print(f'\tDeactivated Edges: {trackList[failure_pattern_index]}')
                # deactivate edges according to pattern
                self._deactivateLinks(trackList[failure_pattern_index])
                # run attached experiments
                res = self.singleRun(trackList[failure_pattern_index])
                # print(res)
                # restore edges
                self._restore()

                # Store the result
                results[fail_iteration][failure_pattern_index] = res

                # dump results to json
                if self.save_file:
                    with open(self.filename, 'w') as f:
                        json.dump(results, f, indent=4)

        return results

    def singleRun(self, all_deactivate_links=None) -> dict:
        """
         Runs all attached experiment once without modifying the state of any edges
         :return:
        """
        if all_deactivate_links is None:
            all_deactivate_links = list()

        experiment_results = dict()
        # convert from frozenset to tuple to save in json (somewhat ugly)
        experiment_results['deactivated_edges'] = [(a, b) for a, b in all_deactivate_links]

        for experiment in self._experiments:
            experiment_results |= {
                experiment.name: experiment.run(decativated_links=all_deactivate_links)
            }
        return experiment_results

    def _deactivateLinks(self, edges: list[frozenset[str]]):
        for link in edges:
            self.net.configLinkStatus(*link, 'down')

    def _restore(self):
        for link in self._switchLinks:
            self.net.configLinkStatus(*link, 'up')
