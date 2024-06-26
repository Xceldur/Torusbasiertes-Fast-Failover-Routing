from unittest import TestCase

from algoritmen.LowStretchFailover import LowStretchFailover


class TestLowStretchFailover(TestCase):

    def setUp(self):
        portInterfaceRelation = {'s0x0': {'s0x1': '3', 's1x0': '2', 's0x2': '4', 's2x0': '5'},
                                 's0x1': {'s0x0': '2', 's0x2': '4', 's1x1': '3', 's2x1': '5'},
                                 's0x2': {'s0x1': '2', 's0x0': '4', 's1x2': '3', 's2x2': '5'},
                                 's1x0': {'s0x0': '2', 's1x1': '4', 's2x0': '3', 's1x2': '5'},
                                 's1x1': {'s0x1': '2', 's1x0': '3', 's1x2': '5', 's2x1': '4'},
                                 's1x2': {'s0x2': '2', 's1x1': '3', 's1x0': '5', 's2x2': '4'},
                                 's2x0': {'s1x0': '2', 's0x0': '3', 's2x1': '4', 's2x2': '5'},
                                 's2x1': {'s1x1': '2', 's2x0': '3', 's0x1': '4', 's2x2': '5'},
                                 's2x2': {'s1x2': '2', 's2x1': '3', 's0x2': '4', 's2x0': '5'}}
        macHostRelation = {
            'h0x0': '00:00:00:00:00:01', 'h0x1': '00:00:00:00:00:02', 'h0x2': '00:00:00:00:00:03',
            'h1x0': '00:00:00:00:00:04', 'h1x1': '00:00:00:00:00:05', 'h1x2': '00:00:00:00:00:06',
            'h2x0': '00:00:00:00:00:07', 'h2x1': '00:00:00:00:00:08', 'h2x2': '00:00:00:00:00:09'}

        self.lowStretchAlgo = LowStretchFailover(size_x=3, size_y=3,
                                                 portInterfaceRelation=portInterfaceRelation,
                                                 macHostRelation=macHostRelation)

    def test_generate_t_shortes_path(self):
        d = self.lowStretchAlgo._generateT_shortesPath('s0x0')
        print(d)

    def test_generate_auxillary(self):
        self.fail()

    def test_generate_rules(self):
        self.fail()

    def test_insert_fail_over_rules(self):
        self.fail()

    def test__project_to_suitable_coordinates_Y(self):
        def gY(n):
            l = {}
            for i in range(3):
                new_x, new_y = self.lowStretchAlgo._project_to_suitable_coordinates(0, i-n)
                l[i] = new_y
            return l

        # test Y_i projection, i describes to value that had to be centered
        Y_0 = {
            0: 0,
            1: -1,
            2: 1,
        }
        self.assertEqual(Y_0, gY(0))
        Y_1 = {
            0: 1,
            1: 0,
            2: -1,
        }
        self.assertEqual(Y_1, gY(1))
        Y_2 = {
            0: -1,
            1: 1,
            2: 0,
        }
        self.assertEqual(Y_2, gY(2))

    def test__project_to_suitable_coordinates_X(self):
        def gX(n):
            l = {}
            for i in range(3):
                    new_x, new_y = self.lowStretchAlgo._project_to_suitable_coordinates(0, i-n)
                    l[i] = new_x
            return l

        # test Y projection Y_i where i decribes to value that had to be centered
        X_0 = {
                0: 0,
                1: -1,
                2: 1,
            }
        self.assertEqual(X_0, gX(0))
        X_1 = {
                0: -1,
                1: -0,
                2: 1,
            }
        self.assertEqual(X_1, gX(1))
        X_2 = {
                0: -1,
                1: 1,
                2: 0,
            }
        self.assertEqual(X_2, gX(2))
