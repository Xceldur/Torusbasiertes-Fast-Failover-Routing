from abc import ABC, abstractmethod
from typing import override

from algoritmen.FailOverAlgoritmen import FailOverAlgorithm


class PrioryCounter:
    def __init__(self):
        self.__internalCounter: int = 1000

    @property
    def prio(self) -> int:
        self.__internalCounter += 100
        return self.__internalCounter


class FailOverAugmentation(FailOverAlgorithm, ABC):
    def __init__(self, size_x: int, size_y: int, portInterfaceRelation: dict, macHostRelation: dict,
                 prioCounter: PrioryCounter, failoverLookUp=None):
        super().__init__(size_x, size_y, portInterfaceRelation, macHostRelation)
        self.prioCounter: PrioryCounter = prioCounter
        if failoverLookUp is None:
            failoverLookUp = []

        self._lookupTable = failoverLookUp

    def setFailOverGroupLookUp(self, failoverLookUp: list):
        if len(self._lookupTable) > 0:
            raise ValueError('failoverLookUp is already intilized')
        self._lookupTable = failoverLookUp
        print()

    @abstractmethod
    def insertFailOverRules(self, dst: str) -> int:
        if len(self._lookupTable) < 0:
            raise ValueError('failoverlookup is not initialized')
        return 0

    # Raise errors if setup methode is called from augmentation (this seems like a poor solution but for now it works)
    @override
    def setUpFailOvertGroups(self, size: int = 4):
        raise AttributeError("You may not call this method from augmentation")

    @override
    def setUpHostToSwitch(self):
        raise AttributeError("You may not call this method from augmentation")
