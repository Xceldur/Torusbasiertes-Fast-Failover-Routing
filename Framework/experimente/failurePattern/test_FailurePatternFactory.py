from unittest import TestCase

from experimente.failurePattern.FailurePatternFactory import FailurePatternFactory


class TestFailurePatternFactory(TestCase):
    def test_around_node(self):
        for i in range(5):
            list(FailurePatternFactory(7,7).randomNodes(1))
