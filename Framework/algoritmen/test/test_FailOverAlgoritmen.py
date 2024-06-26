import unittest
from unittest import TestCase

from algoritmen.FailOverAlgoritmen import FailOverAlgorithm


class TestFailOverAlgoritmenImplemenation(FailOverAlgorithm):

    def insertFailOverRules(self) -> int:
        raise NotImplementedError()


class TestFailOverAlgorithm(TestCase):
    @classmethod
    def setUpClass(cls):
        portInterfaceRelation = {'s0x0': {'s0x1': '3', 's1x0': '2', 's0x2': '4', 's2x0': '5'},
                                 's0x1': {'s0x0': '2', 's0x2': '4', 's1x1': '3', 's2x1': '5'},
                                 's0x2': {'s0x1': '2', 's0x0': '4', 's1x2': '3', 's2x2': '5'},
                                 's1x0': {'s0x0': '2', 's1x1': '4', 's2x0': '3', 's1x2': '5'},
                                 's1x1': {'s0x1': '2', 's1x0': '3', 's1x2': '5', 's2x1': '4'},
                                 's1x2': {'s0x2': '2', 's1x1': '3', 's1x0': '5', 's2x2': '4'},
                                 's2x0': {'s1x0': '2', 's0x0': '3', 's2x1': '4', 's2x2': '5'},
                                 's2x1': {'s1x1': '2', 's2x0': '3', 's0x1': '4', 's2x2': '5'},
                                 's2x2': {'s1x2': '2', 's2x1': '3', 's0x2': '4', 's2x0': '5'}}

        cls.f = TestFailOverAlgoritmenImplemenation(10, 10, portInterfaceRelation)

    def test_get_failover_group(self):
        self.f.setUpFailOvertGroups()
        n = self.f.__get_failover_group('s0x0', 's0x1', 's1x0', 's0x2', 's2x0')
        self.assertEqual(6, n)

    def test_switch_to_mac(self):
        specimen_string = self.f.__switchToMAC('s25x37')
        specimen_tuple = self.f.__switchToMAC((25, 37))
        self.assertEqual('00:00:00:00:19:25', specimen_string, specimen_tuple)


if __name__ == '__main__':
    unittest.main()
