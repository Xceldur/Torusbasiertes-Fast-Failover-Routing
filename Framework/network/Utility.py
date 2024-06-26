import random


class Utility(object):
    @staticmethod
    def switchToTuple(switchAsString: str) -> (int, int):
        return tuple(map(int, switchAsString[1:].split('x')))

    @staticmethod
    def shuffled_neighbors(neighbors):
        neighbors = list(neighbors)  # Convert to list if not already
        random.shuffle(neighbors)  # Shuffle the list in place
        return neighbors

