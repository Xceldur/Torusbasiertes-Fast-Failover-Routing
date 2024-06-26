import logging
from typing import override

from algoritmen.FailOverAlgoritmen import FailOverAlgorithm


class LowStretchFailover(FailOverAlgorithm):

    def _project_to_suitable_coordinates(self, x1, x2):
        # calculate distance to center
        distance_to_center_x = self.X_SIZE // 2
        distance_to_center_y = self.Y_SIZE // 2

        # offset coordinates by center and take module to account for warp around
        # afterward push coordinates back centered
        new_x = ((x1 + distance_to_center_x) % self.X_SIZE) - distance_to_center_x
        new_y = ((-x2 + distance_to_center_y) % self.Y_SIZE) - distance_to_center_y
        return new_x, new_y

    # generate T_k for every node to source
    def _generateT_shortesPath(self, target: str):
        T_k: dict[str, str] = {}
        target_x, target_y = self._switchToTuple(target)

        # generate projection and inverse
        projection: dict = {}
        reverse_projection: dict
        for x in range(self.X_SIZE):
            for y in range(self.Y_SIZE):
                p_x, p_y = self._project_to_suitable_coordinates(x - target_x, y - target_y)
                projection[f's{x}x{y}'] = (p_x, p_y)
        reverse_projection = dict((v, k) for k, v in projection.items())

        # calculate for every node v the next node in the shortest path according to paper
        # note: the target has to be centered to (0,0) first
        for v_x in range(self.X_SIZE):
            for v_y in range(self.Y_SIZE):
                # get project of coordinates
                p_x, p_y = projection[f's{v_x}x{v_y}']
                # now calculate according to paper take action TODO: Take action
                if p_x > 0:  # decrease x1 to 0 when x1 > 0
                    T_k[f's{v_x}x{v_y}'] = reverse_projection[(p_x - 1, p_y)]
                elif p_y > 0:  # decrease x2 to 0 when x2 > 0
                    T_k[f's{v_x}x{v_y}'] = reverse_projection[(p_x, p_y - 1)]
                elif p_x < 0:  # increase x1 to 0 when x1 < 0
                    T_k[f's{v_x}x{v_y}'] = reverse_projection[(p_x + 1, p_y)]
                elif p_y < 0:  # increase x2 to 0 when x2 < 0
                    T_k[f's{v_x}x{v_y}'] = reverse_projection[(p_x, p_y + 1)]
                else:
                    # assert that v is in fact the target
                    assert p_x == 0 and p_y == 0
                    assert v_x == target_x and v_y == target_y
        return T_k

    # generate dict with e_t, e_l, e_b, e_r for every node respectively from T_k TODO: Orientirung überpüfen
    def __generate_auxiliary(self, T_k, target: str):
        e: dict[str, dict[str, str | bool]] = {}
        for v_x in range(self.X_SIZE):
            for v_y in range(self.Y_SIZE):
                if self._switchToTuple(target) == (v_x, v_y):  # skip dst
                    continue
                et: str = self._switchToTuple(T_k[f's{v_x}x{v_y}'])
                # calculate cardinal directions for v
                cardinals_direction: list[str] = [
                    (v_x, (v_y + 1) % self.Y_SIZE),  # north
                    ((v_x + 1) % self.X_SIZE, v_y),  # east
                    (v_x, (v_y - 1) % self.Y_SIZE),  # south
                    ((v_x - 1) % self.X_SIZE, v_y)  # west
                ]
                # match e_t with one of the car cardinalsDirection to get rotation to offset list
                rotation_index: int = cardinals_direction.index(et)
                cardinals_direction: list[str] = list(
                    map(lambda x: f's{x[0]}x{x[1]}', cardinals_direction))  # map to switch marking
                e[f's{v_x}x{v_y}'] = {'t': cardinals_direction[(rotation_index + 0) % 4],
                                      'l': cardinals_direction[(rotation_index + 1) % 4],
                                      'b': cardinals_direction[(rotation_index + 2) % 4],
                                      'r': cardinals_direction[(rotation_index + 3) % 4],
                                      'mark': False}
        return e

    def __generateRules(self, e_kv: dict, target):
        ex_rules: list[str] = []
        # *1 mark every node v when some node w exist where e_l(w)=v and x1(w) or x2(w)=1
        for i in range(self.Y_SIZE):  # some node w with x1 = 0 TODO: mark überpüfen
            # skip target
            if f's0x{i}' == target:  # or e_kv[f's0x{i}']['l'] == target:
                continue
            e_kv[e_kv[f's0x{i}']['l']]['mark'] = True
        for i in range(self.X_SIZE):  # some node w with x2 = 0
            # skip target
            if f's{i}x0' == target:  # or e_kv[f's{i}x0']['l'] == target:
                continue
            e_kv[e_kv[f's{i}x0']['l']]['mark'] = True

        for y in range(self.Y_SIZE):
            for x in range(self.X_SIZE):
                switch_src = f's{x}x{y}'

                if switch_src == target:
                    continue

                ex_rules.append(f'# Node: s{x}x{y}')
                # for every node where condition *1 is valid, rule where inport=e_l(v) output:e_t,e_b
                if e_kv[switch_src]['mark']:
                    ex_rules.append('# Rule 1 while mark set:')
                    ex_rules.append(f'-O OpenFlow15 add-flow {switch_src} '
                                   f'priority=5,'
                                   f'dl_dst={self._switchHostToMAC(target)},'
                                   f'in_port={self.portInterfaceRelation[switch_src][e_kv[switch_src]['l']]},'
                                   f'actions=group:'
                                   f'{self._get_failover_group(switch_src,
                                                               e_kv[switch_src]['t'],
                                                               e_kv[switch_src]['b'])}')

                # rule if in_port=e_t, output: e_l, e_b, e_r
                ex_rules.append(f'-O OpenFlow15 add-flow {switch_src} '
                               f'priority=4,'
                               f'dl_dst={self._switchHostToMAC(target)},'
                               f'in_port={self.portInterfaceRelation[switch_src][e_kv[switch_src]['t']]},'
                               f'actions=group:'
                               f'{self._get_failover_group(switch_src,
                                                           e_kv[switch_src]['l'],
                                                           e_kv[switch_src]['b'],
                                                           e_kv[switch_src]['r'])}')

                # if not output: e_l, e_b, e_r
                ex_rules.append(f'-O OpenFlow15 add-flow {switch_src} '
                               f'priority=3,'
                               f'dl_dst={self._switchHostToMAC(target)},'
                               f'actions=group:'
                               f'{self._get_failover_group(switch_src,
                                                           e_kv[switch_src]['t'],
                                                           e_kv[switch_src]['l'],
                                                           e_kv[switch_src]['b'],
                                                           e_kv[switch_src]['r'])}')

        return ex_rules

    @override
    def insertFailOverRules(self, dst: str) -> int:
        super().insertFailOverRules(dst)
        # generate e_kv for target
        T_k = self._generateT_shortesPath(target=dst)
        e_kv = self.__generate_auxiliary(T_k, dst)
        # generate failover rules from e_kv
        ex_rules = self.__generateRules(e_kv, target=dst)
        self.ovsComands = self.ovsComands + ex_rules

        if logging.DEBUG >= logging.root.level:
            logging.debug(f'\n Low Stretch Results for target: {dst}:')
            logging.debug("{:<5}| {:<5}{:<5}{:<5}{:<5}{:<5}".format('Node', 'mark', 'e_t', 'e_l', 'e_r', 'e_b'))
            for k, v in e_kv.items():
                logging.debug("{:<5}| {:<5}{:<5}{:<5}{:<5}{:<5}".
                              format(k, v['mark'], v['t'], v['l'], v['r'], v['b']))
        return 0
