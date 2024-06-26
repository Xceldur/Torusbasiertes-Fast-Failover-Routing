from unittest import TestCase

import networkx as nx

from algoritmen.HamiltonCircutFailover import HamiltonCircutFailover


class TestHamiltonCircutFailover(TestCase):

    def test_hamitlon_with_ivalid_values(self):
        with self.assertRaises(ValueError):
            HamiltonCircutFailover(4, 6, {"a": 4}, {"c": 4})
            HamiltonCircutFailover(3, 3, {}, {})

    def test_generate_hamilton_3x3(self):
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

        self.algo = HamiltonCircutFailover(3, 3, portInterfaceRelation=portInterfaceRelation,
                                           macHostRelation=macHostRelation)
        h1_compare = nx.path_graph(['s0x0', 's1x0', 's2x0', 's2x1', 's2x2', 's0x2', 's1x2', 's1x1', 's0x1'])
        h1_compare.add_edge('s0x0', 's0x1')

        h1_spec, h2_spec = self.algo._generateHamilton()

        self.assertEqual(h1_spec, list(nx.dfs_preorder_nodes(h1_compare, 's0x0')))

    def test_generate_hamilton_5x5(self):
        portInterfaceRelation = {'s0x0': {'s0x1': 3, 's1x0': 2, 's0x4': 4, 's4x0': 5},
                                 's0x1': {'s0x0': 2, 's0x2': 4, 's1x1': 3, 's4x1': 5},
                                 's0x2': {'s0x1': 2, 's0x3': 4, 's1x2': 3, 's4x2': 5},
                                 's0x3': {'s0x2': 2, 's0x4': 4, 's1x3': 3, 's4x3': 5},
                                 's0x4': {'s0x3': 2, 's0x0': 4, 's1x4': 3, 's4x4': 5},
                                 's1x0': {'s0x0': 2, 's1x1': 4, 's2x0': 3, 's1x4': 5},
                                 's1x1': {'s0x1': 2, 's1x0': 3, 's1x2': 5, 's2x1': 4},
                                 's1x2': {'s0x2': 2, 's1x1': 3, 's1x3': 5, 's2x2': 4},
                                 's1x3': {'s0x3': 2, 's1x2': 3, 's1x4': 5, 's2x3': 4},
                                 's1x4': {'s0x4': 2, 's1x3': 3, 's1x0': 5, 's2x4': 4},
                                 's2x0': {'s1x0': 2, 's2x1': 4, 's3x0': 3, 's2x4': 5},
                                 's2x1': {'s1x1': 2, 's2x0': 3, 's2x2': 5, 's3x1': 4},
                                 's2x2': {'s1x2': 2, 's2x1': 3, 's2x3': 5, 's3x2': 4},
                                 's2x3': {'s1x3': 2, 's2x2': 3, 's2x4': 5, 's3x3': 4},
                                 's2x4': {'s1x4': 2, 's2x3': 3, 's2x0': 5, 's3x4': 4},
                                 's3x0': {'s2x0': 2, 's3x1': 4, 's4x0': 3, 's3x4': 5},
                                 's3x1': {'s2x1': 2, 's3x0': 3, 's3x2': 5, 's4x1': 4},
                                 's3x2': {'s2x2': 2, 's3x1': 3, 's3x3': 5, 's4x2': 4},
                                 's3x3': {'s2x3': 2, 's3x2': 3, 's3x4': 5, 's4x3': 4},
                                 's3x4': {'s2x4': 2, 's3x3': 3, 's3x0': 5, 's4x4': 4},
                                 's4x0': {'s3x0': 2, 's0x0': 3, 's4x1': 4, 's4x4': 5},
                                 's4x1': {'s3x1': 2, 's4x0': 3, 's0x1': 4, 's4x2': 5},
                                 's4x2': {'s3x2': 2, 's4x1': 3, 's0x2': 4, 's4x3': 5},
                                 's4x3': {'s3x3': 2, 's4x2': 3, 's0x3': 4, 's4x4': 5},
                                 's4x4': {'s3x4': 2, 's4x3': 3, 's0x4': 4, 's4x0': 5}}

        macHostRelation = {'h0x0': '00:00:00:00:00:01', 'h0x1': '00:00:00:00:00:02', 'h0x2': '00:00:00:00:00:03',
                           'h0x3': '00:00:00:00:00:04', 'h0x4': '00:00:00:00:00:05', 'h1x0': '00:00:00:00:00:06',
                           'h1x1': '00:00:00:00:00:07', 'h1x2': '00:00:00:00:00:08', 'h1x3': '00:00:00:00:00:09',
                           'h1x4': '00:00:00:00:00:0a', 'h2x0': '00:00:00:00:00:0b', 'h2x1': '00:00:00:00:00:0c',
                           'h2x2': '00:00:00:00:00:0d', 'h2x3': '00:00:00:00:00:0e', 'h2x4': '00:00:00:00:00:0f',
                           'h3x0': '00:00:00:00:00:10', 'h3x1': '00:00:00:00:00:11', 'h3x2': '00:00:00:00:00:12',
                           'h3x3': '00:00:00:00:00:13', 'h3x4': '00:00:00:00:00:14', 'h4x0': '00:00:00:00:00:15',
                           'h4x1': '00:00:00:00:00:16', 'h4x2': '00:00:00:00:00:17', 'h4x3': '00:00:00:00:00:18',
                           'h4x4': '00:00:00:00:00:19'}

        h1_compare = nx.Graph()
        h1_compare.add_edges_from(
            [('s0x0', 's1x0'), ('s0x0', 's0x1'), ('s1x0', 's2x0'), ('s0x1', 's1x1'), ('s1x1', 's1x2'), ('s1x2', 's0x2'),
             ('s0x2', 's0x3'), ('s0x3', 's1x3'), ('s1x3', 's1x4'), ('s1x4', 's0x4'), ('s0x4', 's4x4'), ('s4x4', 's4x3'),
             ('s4x3', 's4x2'), ('s4x2', 's4x1'), ('s4x1', 's4x0'), ('s4x0', 's3x0'), ('s3x0', 's3x1'), ('s3x1', 's3x2'),
             ('s3x2', 's3x3'), ('s3x3', 's3x4'), ('s3x4', 's2x4'), ('s2x4', 's2x3'), ('s2x3', 's2x2'), ('s2x2', 's2x1'),
             ('s2x1', 's2x0')])

        self.algo = HamiltonCircutFailover(5, 5, portInterfaceRelation=portInterfaceRelation,
                                           macHostRelation=macHostRelation)

        h1_spec, h2_spec=self.algo._generateHamilton()

        self.assertEqual(list(nx.dfs_preorder_nodes(h1_compare)), h1_spec)

