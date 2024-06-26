from typing import override

from algoritmen.Augmentations.FailOverAugmentation import FailOverAugmentation, PrioryCounter


class FailOverAlgorithmTwoHop(FailOverAugmentation):
    def __init__(self, size_x: int, size_y: int, portInterfaceRelation: dict, macHostRelation: dict,
                 prioCounter: PrioryCounter, failoverLookUp=None):
        # if size_x and size_y < 5:
        #    raise ValueError('Pls use dimensional greater than 5')

        super().__init__(size_x, size_y, portInterfaceRelation, macHostRelation, prioCounter, failoverLookUp)

    @override
    def insertFailOverRules(self, dst: str) -> int:
        super().insertFailOverRules(dst)
        # get assigned priority
        prio: int = self.prioCounter.prio

        # insert two hop rules for dst with higher priory than the other routing rules
        dst_x, dst_y = self._switchToTuple(dst)

        # every node with multiple path within a distance of two hops
        snowflake_intermediateR = {
            f's{(dst_x - 1) % self.X_SIZE}x{(dst_y + 1) % self.Y_SIZE}':  # upper left corner
                [f's{dst_x}x{(dst_y + 1) % self.Y_SIZE}', f's{(dst_x - 1) % self.X_SIZE}x{dst_y}'],

            f's{(dst_x + 1) % self.X_SIZE}x{(dst_y + 1) % self.Y_SIZE}':  # upper right corner
                [f's{dst_x}x{(dst_y + 1) % self.Y_SIZE}', f's{(dst_x + 1) % self.X_SIZE}x{dst_y}'],

            f's{(dst_x + 1) % self.X_SIZE}x{(dst_y - 1) % self.Y_SIZE}':  # bottom right corner
                [f's{dst_x}x{(dst_y - 1) % self.Y_SIZE}', f's{(dst_x + 1) % self.X_SIZE}x{dst_y}'],

            f's{(dst_x - 1) % self.X_SIZE}x{(dst_y - 1) % self.Y_SIZE}':  # bottom left corner
                [f's{dst_x}x{(dst_y - 1) % self.Y_SIZE}', f's{(dst_x - 1) % self.X_SIZE}x{dst_y}'],
        }

        # snowflake rule (all nodes within two distance of dst with viable alternative paths at most. 2)
        for snowflake_node in snowflake_intermediateR.keys():
            intermediates_nodes = snowflake_intermediateR[snowflake_node]
            # snowflake node rules:
            # 1. send to fist intermediate node that is up
            self.ovsComands.append(f'-O OpenFlow15 add-flow {snowflake_node} '
                                   f'priority={prio},'
                                   f'dl_dst={self._switchHostToMAC(dst)},'
                                   f'actions=group:'
                                   f'{self._get_failover_group(
                                       snowflake_node, *intermediates_nodes)}')

            # 2. when package has bounced from intermediate node take different intermediate node (source probing)
            self.ovsComands.append(f'-O OpenFlow15 add-flow {snowflake_node} '
                                   f'priority={prio + 1},'
                                   f'in_port={self.portInterfaceRelation[snowflake_node][intermediates_nodes[0]]},'
                                   f'dl_dst={self._switchHostToMAC(dst)},'
                                   f'actions=output:'
                                   f'{self.portInterfaceRelation[snowflake_node][intermediates_nodes[1]]}'
                                   )
            self.ovsComands.append(f'-O OpenFlow15 add-flow {snowflake_node} '
                                   f'priority={prio + 1},'
                                   f'in_port={self.portInterfaceRelation[snowflake_node][intermediates_nodes[1]]},'
                                   f'dl_dst={self._switchHostToMAC(dst)},'
                                   f'actions=output:'
                                   f'{self.portInterfaceRelation[snowflake_node][intermediates_nodes[0]]}'
                                   )

            # intermediate node rules
            # bounce package back if path direct path to dst is blocked
            self.ovsComands.append(f'-O OpenFlow15 add-flow {intermediates_nodes[0]} '
                                   f'priority={prio},'
                                   f'in_port={self.portInterfaceRelation[intermediates_nodes[0]][snowflake_node]},'
                                   f'dl_dst={self._switchHostToMAC(dst)},'
                                   f'actions=group:'
                                   f'{self._get_failover_group(
                                       intermediates_nodes[0], dst, snowflake_node)}')

            self.ovsComands.append(f'-O OpenFlow15 add-flow {intermediates_nodes[1]} '
                                   f'priority={prio},'
                                   f'in_port={self.portInterfaceRelation[intermediates_nodes[1]][snowflake_node]},'
                                   f'dl_dst={self._switchHostToMAC(dst)},'
                                   f'actions=group:'
                                   f'{self._get_failover_group(
                                       intermediates_nodes[1], dst, snowflake_node)}')

        return 0
