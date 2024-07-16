import argparse
import json
import sys
import time
import traceback
from typing import Final

import mininet.clean
from mininet.link import Intf
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch

from algoritmen.FailOverAlgorimenManager import FailOverAlgorimenManager
from experimente.ExperimentManager import ExperimentManager
from experimente.FpingTestMultiBatch import FpingTestMultiBatch
from experimente.IperAllToAll import IPerfAllotAll
from experimente.failurePattern.FailurePatternFactory import FailurePatternFactory
from network.CUSTOMCLI import CUSTOMCLI
from network.TopoTorus import TopoTorus

# set LogLevel for Mininet and Logger
setLogLevel('info')

# start parsing terminal arguments
parser = argparse.ArgumentParser(prog='Mininet Fast Failover',
                                 description='Description', )

parser.add_argument('algo', choices=['low_stretch', 'hamilton', 'hamilton_low_stretch', 'clean'],
                    help='a')
parser.add_argument('--size_x', type=int, default=5, choices=range(3, 255),
                    metavar='[3-255]',
                    help='a')
parser.add_argument('--size_y', type=int, default=5, choices=range(3, 255),
                    metavar='[3-255]',
                    help='a')
parser.add_argument('--augmentation', choices=['two_hop'],
                    help='')
parser.add_argument('--topo', choices=['single_dest', 'normal'], default='normal',
                    help='a')
parser.add_argument('--bandwidth', choices=range(10, 1000), default=100, metavar='[10-1000]mbit')
parser.add_argument('--delay', choices=range(0, 1000), default=10, metavar='[10-1000]ms')
# parser.add_argument('--delay', type=int, default=5, )
args = parser.parse_args()
X_SIZE: Final[int] = args.size_x
Y_SIZE: Final[int] = args.size_y
ALGO: Final[str] = args.algo
AUGMENTATION: Final[str] = [] if args.augmentation is None else args.augmentation
TOPO: Final[str] = args.topo
BW: Final[int] = args.bandwidth
DELAY: Final[int] = args.delay
# end parsing terminal arguments

# cleanup mininet residue if desired, that may be necessary if the script did not exit gracefully
if ALGO == 'clean':
    mininet.clean.cleanup()
    sys.exit()

# initialize the requested torus topologie
match TOPO:
    # case 'single_dest': pass #topo = TopoTorusSingelDest(X_SIZE=X_SIZE, Y_SIZE=Y_SIZE, dst=)
    case 'normal':
        topo = TopoTorus(x_size=X_SIZE, y_size=Y_SIZE)
    case _:
        raise AssertionError('Not a known Topology')
# create network without controller and static arp routes and detemitic mac adresses
mininet_network: Mininet
try:
    mininet_network = Mininet(topo=topo,
                              switch=OVSSwitch,
                              controller=None,
                              autoStaticArp=True,
                              autoSetMacs=True,
                              cleanup=True,
                              )
except Exception as e:
    if 'RTNETLINK answers: File exists' in str(e):
        print(str(e))
        print('Did mininet not exit probably? Try calling ALGO \"clean\" or mn -c')
    else:
        print(traceback.format_exc())
    sys.exit(-1)

# start network
mininet_network.start()

# disable IPv6 due to unnecessary icmpv6 router solicitations. Since no static IPv6 IPs will be set nor any ndp entries
for node in mininet_network.values():
    node.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
    node.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
    node.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

# setting link parameter since mininet tcLink does not work link intended. Realworld link characteristic are applied
#  with tc
for link in mininet_network.links:
    # get interfaces from links
    link_interfaces: list[Intf] = [link.intf1, link.intf2]
    # skip hosts due to the fact that it does not contribute to evaluation
    if any(map(lambda x: x.node.name.startswith('h'), link_interfaces)):
        continue
    # apply netem qdisk to both interfaces of link
    for inf in link_interfaces:
        inf.node.cmd(f'tc qdisc add dev {inf.name} root netem delay {DELAY}ms rate {BW}mbit')

# now we have a running network...
# next a mac host relation will be created
macHostRelation: dict[str, str] = {}
for host in mininet_network.hosts:
    macHostRelation[host.name] = host.MAC()

# and a switch (interface) port relation in a adjacent matrix style
port_switch_adj: dict[str, dict[str, int]] = {f's{x}x{y}': {} for x in range(X_SIZE) for y in range(Y_SIZE)}

# iterate over all links and extract port numbers for adj matrix
for link in mininet_network.links:
    edge: (str, list[str]) = (
        str(link.intf1).split('-'), str(link.intf2).split('-'))  # get node and interface number

    # filter hosts in adj matrix since they always reside on port 1
    if edge[0][0][0] == 'h' or edge[1][0][0] == 'h':
        continue

    port_switch_adj[edge[0][0]][edge[1][0]] = int(edge[0][1][3:])
    port_switch_adj[edge[1][0]][edge[0][0]] = int(edge[1][1][3:])

# applying selected fail over routing scheme
fM = FailOverAlgorimenManager(size_x=X_SIZE, size_y=Y_SIZE,
                              portInterfaceRelation=port_switch_adj,
                              macHostRelation=macHostRelation,
                              main_algo_name=ALGO)
# next attach augmentation if desired
for aug in AUGMENTATION:
    fM.attachAugmenationByName(aug)

# now insert openflow rules
fM.insertRules()

eM = ExperimentManager(net=mininet_network, x_size=X_SIZE, y_size=Y_SIZE, save_file=True, filename='/tmp/TempExpResult-22.json')
eM.attach(FpingTestMultiBatch(net=mininet_network, size_x=X_SIZE, size_y=Y_SIZE))
eM.attach(IPerfAllotAll(net=mininet_network, size_x=X_SIZE, size_y=Y_SIZE, number_of_pairs=20, seed=2976067196261))

# Failure Pattern Random Node
start_time = time.time()
failurepattern_list = [
    FailurePatternFactory(size_x=X_SIZE, size_y=Y_SIZE)
    .clusterFailureStep(nodes_d=['s3x3'], p=0.9, interval_q=(0.30, 0.94), step_q=0.04) for _ in range(5)]

eM.aggregatedRun(failure_pattern_list=failurepattern_list, iterations=15)
print("--- %s seconds ---" % (time.time() - start_time))

mininet_network.stop()
