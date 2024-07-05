
# Torusbasiertes-Fast-Failover-Routing



## Abstract
> ⁤In this thesis, grid and torus-based fast failover methods are explored to enhance the resilience of network infrastructures. ⁤⁤The focus is on software-defined networking (SDN) environments, where rapid recovery is crucial. ⁤⁤Several failover strategies are evaluated, with particular attention to a low-stretch algorithm and a Hamiltonian-based method. ⁤⁤Various failure patterns are employed to simulate multiple failure scenarios. ⁤⁤The implementation is carried out entirely in OpenFlow, utilizing fast failover groups. ⁤⁤The results confirm that the low-stretch algorithm provides superior throughput and latency under failure conditions due to its efficient routing structure. It should be emphasized that the low stretch algorithm works even better than its theoretical resilience guarantees.  

## Setup
#### Manual (Fedora 39): 
1) Install packages:
`dnf install git ping fping iperf mininet iproute-tc openvswitch python3 python3-seaborn python3-numpy python3-pandas python3-tqdm python3-matplotlib python-networkx` 
2) Enable and start OpenVSwitch:
`sudo systemctl enable openvswitch.service` </br></br>
`sudo systemctl start openvswitch.service` 
3) Clone the repo:
`git clone https://github.com/Xceldur/Torusbasiertes-Fast-Failover-Routing.git` 
#### Prebuild VM:
You may also use a VM of your choice, yet be aware that there may be issues regarding *tc* limiting abilities due to VM imprecision[\[1\]](https://stackoverflow.com/questions/72539814/mininet-ping-iperf3-got-unstable-measurement-results).
A prebuild VM (OVA File) can be found [here](https://tu-dortmund.sciebo.de/s/sHiuKnXJRgMmDq1/download). It appears to be advisable to allow only the utilization of one CPU Core. However, that may pose different limitations regarding performance. 

## Instructions
t.b.a

## Reproduce the experiments of the thesis
t.b.a

## Make your own **experiment**
t.b.a

## Make your own (fast failover)-routing algorithm
t.b.a
