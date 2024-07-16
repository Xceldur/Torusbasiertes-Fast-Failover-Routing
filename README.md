
# Torusbasiertes-Fast-Failover-Routing
## Overview
This project was developed as part of a bachelor's thesis to evaluate several torus-based fast failure methods. For this purpose, a portfolio of algorithms (in particular a low stretch fast failover algorithm) was implemented in OpenFlow and tested against different failure patterns. Thus, this project provides a framework to implement routing procedures and evaluate them within different metrics for different failure patterns. Mininet and OpenVSwitch are used for the simulation.

## Table of Content

1. [Overview](#overview)
2. [Abstract and Thesis](#abstract-and-thesis)
3. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
     - [Manual Setup (Fedora 39)](#manual-setup-fedora-39)
     - [Autostart Configuration](#autostart-configuration)
   - [Prebuilt VM](#prebuilt-vm)
   - [Quick Start](#quick-start)
4. [Folder Structure](#folder-structure)
5. [Usage](#usage)
   - [Torus dimensions and algorithm](#torus-dimensions-and-algorithm)
   - [Experiments](#experiments)
   - [Failure pattern](#failure-pattern)
   - [Plotter and data evaluation](#plotter-and-data-evaluation)
6. [Reproducing the Measurements](#reproducing-the-measurements)
7. [Make your own...](#make-your-own)
   - [Failure Pattern](#failure-pattern-1)
   - [Experiment](#experiment)
   - [(Fast failover) algorithm](#fast-failover-algorithm)
8. [License](#license)

## Abstract and Thesis
> In this thesis, grid and torus-based fast failover methods are
> explored to enhance the resilience of network infrastructures. The
> focus is on software-defined networking (SDN) environments, where
> rapid recovery is crucial. Several failover strategies are evaluated,
> with particular attention to a low-stretch algorithm and a
> Hamiltonian-based method. Various failure patterns are employed to
> simulate multiple failure scenarios. The implementation is carried out
> entirely in OpenFlow, utilizing fast failover groups. The results
> confirm that the low-stretch algorithm provides superior throughput
> and latency under failure conditions due to its efficient routing
> structure. It should be emphasized that the low stretch algorithm
> works even better than its theoretical resilience guarantees.

**Thesis:** t.b.a    <br>
**Defence:** [PDF](Thesis/Defense%20presentation.pdf)

## Getting Started
### Prerequisites
A modern Linux operating system with support for Mininet >2.3..×. and OpenVSwitch >3.2.×. The testing was done on fedora 39. Other distributions should work analogous. 

### Installation
You can find additional information for installing [OpenVSwitch](https://www.openvswitch.org/) and [Mininet](https://mininet.org/) on their respective project pages.
#### Manual Setup (Fedora 39)
1. **Install packages**:
```bash
    sudo dnf install git ping fping iperf mininet iproute-tc openvswitch kernel-modules-extra python3 python3-seaborn python3-numpy python3-pandas python3-tqdm python3-matplotlib python-networkx
```
2. **Start OpenVSwitch**:
```bash
    sudo systemctl start openvswitch.service
```
3. **Load NetEm kernel module**:
```bash
    sudo modprobe sch_netem
```
4. **Clone the repository**:
 ```bash
    git clone https://github.com/Xceldur/Torusbasiertes-Fast-Failover-Routing.git
 ```
##### Autostart Configuration
1. **Enable OpenVSwitch service on startup**:
```bash
    sudo systemctl enable openvswitch.service
```
2. **Load NetEm kernel module on demand by removing module from blacklist** (Note: For older Fedora versions or different Linux distributions, this step is probably unnecessary\[[2](https://access.redhat.com/articles/3760101)\].):
```bash
    sudo sed -i 's/^blacklist sch_netem/#&/' /etc/modprobe.d/sch_netem-blacklist.conf
```
### Prebuilt VM
A prebuilt VM (OVA file) is also available [here](https://tu-dortmund.sciebo.de/s/sHiuKnXJRgMmDq1/download). Note that VM precision issues may affect `tc` limiting abilities, and it is advisable to allow only the use of one CPU core, though that may limit performance\[[1](https://stackoverflow.com/questions/72539814/mininet-ping-iperf3-got-unstable-measurement-results)\].

**VM credentials**:

- **User**: `core`
- **Password**: `core`

**Note:** You can execute `update_or_clone_repo.bash` to clone or update the repo. 

### Quick Start
t.b.a
## Folder Structure
```tree
├── Framework	# source code of the framework
├── Plotter		# plotter for each experiment 
├── Rohdaten	# collected data in evaluation of thesis
├── Thesis		# pdf-files and defence of thesis
├── LICENSE		
└── README.md	
```
## Usage
### Torus dimensions and algorithm
Command line arguments allow you to configure the torus size and the routing algorithm, as well as adjust bandwidth and delay settings. Note: If dimensions or link parameters are not specified, default values will be used (`torus 5x5; bandwidth 100 Mbit; delay 10 ms`).
```
usage: main_cli.py: [-h] [--size_x [3-255]] [--size_y [3-255]] [--augmentation {two_hop}] [--topo {single_dest,normal}] [--bandwidth [10-1000]mbit] [--delay [0-1000]ms] {low_stretch,hamilton,hamilton_low_stretch,clean}

Description

positional argument:
  algoritmen : {low_stretch,hamilton,hamilton_low_stretch,clean}
                        
options:
  -h, --help					show help message and exit
  --size_x [3-255]      		x size of the torus
  --size_y [3-255]      		y size of the torus
  --augmentation {two_hop} 		attach an augmenation to modify behaviour of the algorithm
  --bandwidth [10-1000]mbit	 	specify a bandwidth limit
  --delay [0-1000]ms			specify a delay to apply

```
### Experiments 
After the flow rules are inserted. Initially, the `ExperimentManager` has to be instantiated.  
```python
ExperimentManager(x_size, y_size, net: mininet, filename: str = '', save_file: bool = False)
``` 

The location of the result-JSON can be specified (`filename`), or a pattern of date and time will be used. Afterwards, several experiments can be attached, which are executed sequentially.  For example, some combinations of the experiments below:  

```python  
eM.attach(IPerfSingelDestIsochrone(size_x=X_SIZE, size_y=Y_SIZE,net=mininet_network, dst='h1x1'))
eM.attach(FpingTestMultiBatch(net=mininet_network, size_x=X_SIZE, size_y=Y_SIZE)
eM.attach(IPerfAllotAll(net=mininet_network, size_x=X_SIZE, size_y=Y_SIZE, number_of_pairs=20, seed=20))

```
Finally, a single run can be executed with `run()`. However, please refer to the following [section](Failure-pattern) with other means of execution options (for example, with failures).

The experiments are explained in the table below:

| Experiment               | Description and parameters |
|:---|:---|
| IPerfAllotAll            | Iperf2 is executed in duplex randomly between several drawn pairs of the node set.<br>**Parameters**:<br>- `number_of_pairs`: The number of pairs to be drawn<br>- `seed`: Integer to seed *random*.                                                                                                                            |
| IPerfSingelDestIsochrone | Iperf2 is executed between all vertexes and one destination (client-server model).<br>**Parameters**:<br>- `dst`: vertex to be chosen as destination<br>- `isochronous`: boolean to enable [isochronous mode](https://iperf2.sourceforge.io/iperf-manpage.html). Just make sure your iperf2 is recent and works with the `--isochronous` flag. It is advisable to only select smaller dimensions.  <br>  |
| FpingTestMultiBatch      | Fping is executed between all pairs of the Cartesian product of the vertexes. You can specify a `batch_size` or number of cpu_cores will be used.                                                                                                                                                                               |
### Failure pattern
A failure pattern describes a set of edges to be deactivated that represent an approximation of a real failure. More precisely, an iterator is used that returns a set of edges to be deactivated for each iteration. The following table provides an overview of the available patterns and their parameters:


| Failure Pattern | Description and parameters |
| :--- | :--- |
| Random Edges  | An edge is uniform randomly picked and deactivated.<br>**Parameters**:<br>- `seed`: Integer to seed _random_.  |
| Random Node  | A node is uniform randomly selected, and the surrounding edges are deactivated.<br>**Parameters**:<br>- `seed`: Integer to seed _random_. |
| Clustered Failures  | The failure is propagated from one or more points to several edges. Specifically, one or more points are selected (epicentre) around which the failures propagate to the neighbouring edges with degressive probability per hop, provided that this edge has, in fact, failed (*p* is the initial probability that gets reduced by the product with *q* each hop). As a result, two characteristics are derived. Firstly, it is possible to iterate over the intervals of the probabilities (*ClusterFailureStep*) or to introduce more epicentres in each iteration (*ClusterFailureNode*). <br> **Parameters**  (*ClusterFailureStep*): <br>- `nodes_d`: The epicenter nodes.<br>- `step_p` and `step_q`: the step of each iteration <br>- `interval_q` and `interval_q`: the interval of p and q<br>- `p`and `q`: Floats p and q  <br>Note: Only set an interval and step or a constant value. <br>**Parameters** (*ClusterFailureNode*): <br>- `nodes_d`: a list of nodes where one (cluster failed) is added each iteration  <br>- `p` and `q`: Floats p and q  <br>- `seed`: Integer to seed _random_.|
| Towards Destination | The edges are deactivated while rotating around a chosen destination to induce a high load on the nearby connections to the target node.<br> **Parameters**: <br>- `dst_node`: specify “destination” switch <br>- `keep_a_way`: a boolean if set *true*, the graph will be kept connected |                                                               


To instantiate a failure pattern:
```python
FailurePatternFactory(size_x=X_SIZE, size_y=Y_SIZE).randomEdges(...)
FailurePatternFactory(size_x=X_SIZE, size_y=Y_SIZE).randomNodes(...)
FailurePatternFactory(size_x=X_SIZE, size_y=Y_SIZE).clusterFailureStep(...)
FailurePatternFactory(size_x=X_SIZE, size_y=Y_SIZE).clusterFailureIncreaseNodes(...)
```

The parameters of the *FailurePatternFactory* can be used to influence the behaviour of the iterator:
- `amount_of_edges`: maximum number of edges to be deactivated until termination. Note: This parameter has no influence on the Cluster Pattern
- `exclude_edges`: edges to keep alive.
- `yield_none_first`: let the first iteration be empty to establish a baseline.

Afterwards, there are several means of execution:
```python  
eM = ExperimentManager(net=mininet_network, x_size=X_SIZE, y_size=Y_SIZE, save_file=True)

#aggregated execution e.g multiple patter sequentially each iteration
failurepattern_list = [FailurePatternFactory(size_x=X_SIZE, size_y=Y_SIZE).randomEdge() for _ in range(10)
eM.aggregatedRun(failure_pattern_list=failurepattern_list, iterations=15)

# execution of a single pattern
fail_pattern = FailurePatternFactory(size_x=X_SIZE, size_y=Y_SIZE).randomEdge()
eM.run(failure_pattern=fail_pattern)
```

### Plotter and data evaluation
For each experiment, a Python script is [available](Plotter/) to generate plots between multiple runs and provide basic statistics. The scripts are designed to be self-explanatory. You can adjust their behavior by modifying the constants at the top of the source files. Note: It is also possible to analyse only a single file

## Reproducing the Measurements
The accountability of research results is of fundamental importance in research. To address this, a script was developed to minimize any potential obstacles.
```bash
$ sudo ./repoduce_data.bash --help
This script can be used to reproduce the data form the thesis
Usage: ./repoduce_data.bash [OPTIONS]

Note: Without a flag all failure patters will be run
Options:
  --random_edge       Execute the algorithms on random edge
  --random_node       Execute the algorithms on random node
  --cluster_step      Execute the algorithms on cluster step
  --cluster_node      Execute the algorithms on cluster node
  --towards_dst       Execute the algorithms on towards destination 
  --help              Display this help message
```
You can use that [script](Framework/repoduce_data.bash) to reproduce all or some parts of data. Note that the reproduced data can be found in the folder `reproduced_data`. Afterwards the data can be [plotted](#plotter-and-data-evaluation) accordingly. Just make sure that mininet and python is in your `$PATH`.
<br> **Caution**: Running this script may result in data loss especially regarding the content of `reproduced_data`.

## Make your own…
Of course, it is also possible to implement and test new ideas within new failure patterns or algorithms. In the following sections, you will find short description of the corresponding topics, sorted by difficulty. For additional information, please consult the source code.

### Failure Pattern
That one is quite straightforward. You only need to create an [*Iterator*](https://docs.python.org/3/c-api/iterator.html) that returns a list of `frozenset` as edges to deactivate for each iteration. It may be helpful to “extend” the `FailurePatternFactory` and utilize `nodes()` or `edges()` if you just want to implement simple patterns.  

### Experiment
To implement an experiment, the abstract class `Experiment` must first be implemented. It is important to overwrite the `name` attribute with a unique value (that name will also be used in the result JSON). Subsequently, the `run()` and *init* method can be overwritten for realisation. Be aware that a result must be returned as *dict* for each call of run(). <br>
You probably only want to interact with the hosts, as the switches fall within the scope of the routing algorithm. Each host is named after `h{pos_x}x{pos_y}` and can be addressed with `self.net[%host%]`. There are multiple Mininet methods [available](https://mininet.org/api/classmininet_1_1node_1_1Node.html) for executing terminal commands on a host. It should be noted that each host works on the same storage, but the processes and the network interface are isolated. 

### (Fast failover) algorithm
t.b.a
## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

