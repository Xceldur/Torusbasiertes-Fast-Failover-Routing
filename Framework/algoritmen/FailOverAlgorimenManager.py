import itertools

from algoritmen.Augmentations import FailOverAugmentation
from algoritmen.Augmentations.FailOverAlgoritmenTwoHop import FailOverAlgorithmTwoHop
from algoritmen.Augmentations.FailOverAugmentation import PrioryCounter
from algoritmen.FailOverAlgoritmen import FailOverAlgorithm
from algoritmen.HamiltonCircutFailover import HamiltonCircutFailover, HamiltonCircuitFailoverLowStretch
from algoritmen.LowStretchFailover import LowStretchFailover


class FailOverAlgorimenManager:
    def __init__(self, size_x: int, size_y: int, portInterfaceRelation: dict, macHostRelation: dict,
                 main_algo_name: str):
        self.main_algo: FailOverAlgorithm
        self.macHostRelation = macHostRelation
        self.portInterfaceRelation = portInterfaceRelation
        self.size_y = size_y
        self.size_x = size_x
        self._attatched_augmenations: dict[str, FailOverAugmentation] = dict()

        # prepare parameter dict for creation of algorithms
        self.parm_dict: dict = {
            'size_x': self.size_x,
            'size_y': self.size_y,
            'portInterfaceRelation': self.portInterfaceRelation,
            'macHostRelation': self.macHostRelation}

        self.prioCounter = PrioryCounter()
        print(type(self.prioCounter))

        self._loadRoutingAlgorithm(main_algo_name)

    def _loadRoutingAlgorithm(self, main_algo_name):
        # load main algorithm
        match main_algo_name.lower():
            case 'low_stretch':
                self.main_algo = LowStretchFailover(**self.parm_dict)
            case 'hamilton':
                self.main_algo = HamiltonCircutFailover(**self.parm_dict)
            case 'hamilton_low_stretch':
                self.main_algo = HamiltonCircuitFailoverLowStretch(**self.parm_dict)
            case _:
                raise ValueError(f"That Algorithm is not known: {main_algo_name}")

    def attachAugmenationByName(self, name_augmenation: str):
        match name_augmenation:
            case 'twoHop':
                self._attatched_augmenations[name_augmenation] = FailOverAlgorithmTwoHop(**self.parm_dict,
                                                                                         prioCounter=self.prioCounter)
            case _:
                raise ValueError(f"That Augmentation is not known: {name_augmenation}")

    def insertRules(self, dst: str = ''):
        self.main_algo.setUpFailOvertGroups()
        self.main_algo.setUpHostToSwitch()

        # pass lookup table for augmenatiaon
        for aug in self._attatched_augmenations.values():
            aug.setFailOverGroupLookUp(self.main_algo._lookupTable)


        # if no dest is specified insert rules for all dst
        if dst == '':
            for x, y in itertools.product(range(self.size_x), range(self.size_y)):
                # run main algoritmen
                self.main_algo.insertFailOverRules(dst=f's{x}x{y}')
                # attach augmenations
                for aug in self._attatched_augmenations.values():
                    aug.insertFailOverRules(dst=f's{x}x{y}')
        else:
            self.main_algo.insertFailOverRules(dst=dst)
            for aug in self._attatched_augmenations.values():
                aug.insertFailOverRules(dst=dst)

        #logging.info(f"Time taken in Calculation of routing rules: {time.process_time() - start_time}")

        self.main_algo.exicuteOVS()
        for aug in self._attatched_augmenations.values():
            aug.exicuteOVS()

        # attach augmentations
