
# Torusbasiertes-Fast-Failover-Routing



## Abstract
> ⁤In this thesis, grid and torus-based fast failover methods are explored to enhance the resilience of network infrastructures. ⁤⁤The focus is on software-defined networking (SDN) environments, where rapid recovery is crucial. ⁤⁤Several failover strategies are evaluated, with particular attention to a low-stretch algorithm and a Hamiltonian-based method. ⁤⁤Various failure patterns are employed to simulate multiple failure scenarios. ⁤⁤The implementation is carried out entirely in OpenFlow, utilizing fast failover groups. ⁤⁤The results confirm that the low-stretch algorithm provides superior throughput and latency under failure conditions due to its efficient routing structure. It should be emphasized that the low stretch algorithm works even better than its theoretical resilience guarantees.  

## Setup
#### Manual (Fedora 39; July): 
1) Install packages:
```bash
sudo dnf install git ping fping iperf mininet iproute-tc openvswitch python3 python3-seaborn python3-numpy python3-pandas python3-tqdm python3-matplotlib python-networkx kernel-modules-extra
``` 
2) Start OpenVSwitch:
```bash
sudo systemctl start openvswitch.service
``` 
4) Load NetEm Kernel Module (otherwise, no limits will be applied)
```bash
sudo modprobe sch_netem
```
6) Clone the repo:
```bash
git clone https://github.com/Xceldur/Torusbasiertes-Fast-Failover-Routing.git
``` 

##### Autostart:
1) OpenVSwitch:
```bash
sudo systemctl enable openvswitch.service
```
2) Load NetEm Kernel Module on demand by removing the kernel-module form the “blacklist”\[[2](https://access.redhat.com/articles/3760101)\]. You can also just add a hashtag to _/etc/modprobe.d/sch_netem-blacklist.conf_ before _blacklist sch_netem_:
```bash
sudo sed -i 's/^blacklist sch_netem/#&/' /etc/modprobe.d/sch_netem-blacklist.conf
```


#### Prebuild VM:
You may also use a VM of your choice, yet be aware that there may be issues regarding *tc* limiting abilities due to VM imprecision\[[1](https://stackoverflow.com/questions/72539814/mininet-ping-iperf3-got-unstable-measurement-results)\].
A prebuild VM (OVA File) can be found [here](https://tu-dortmund.sciebo.de/s/sHiuKnXJRgMmDq1/download). It appears to be advisable to allow only the utilization of one CPU Core. However, that may pose different limitations regarding performance. 

**VM:** user: `core`; pw: `core`

## Instructions
t.b.a

## Reproduce the experiments of the thesis
t.b.a

## Make your own **experiment**
t.b.a

## Make your own (fast failover)-routing algorithm
t.b.a
