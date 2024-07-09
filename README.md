# Torusbasiertes-Fast-Failover-Routing

## Overview
t.b.a

## Table of Contents
- [Abstract and thesis](#abstract-and-thesis)
- [Setup](#setup)
  - [Manual setup (Fedora 39)](#manual-setup-fedora-39)
  - [Autostart configuration](#autostart-configuration)
  - [Prebuilt VM](#prebuilt-vm)
- [Usage instructions](#usage-instructions)
- [Create Your own experiment](#create-your-own-experiment)
- [Develop Your own (fast failover) routing Algorithm](#develop-your-own-fast-failover-routing-algorithm)
- [Reproduce the measurements](#reproduce-the-measurements)
- [License](#license)

## Abstract and thesis

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
**Defense:** [PDF](Thesis/Defense%20presentation.pdf)
## Setup

### Manual Setup (Fedora 39)
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

### Autostart configuration
1. **Enable OpenVSwitch service on startup**:
    ```bash
    sudo systemctl enable openvswitch.service
    ```
2. **Load NetEm kernel module on demand by removing module from blacklist** (Note: For older Fedora versions or diffrent Linux distributions, this step is probably unnecessary\[[2](https://access.redhat.com/articles/3760101)\].):
    ```bash
    sudo sed -i 's/^blacklist sch_netem/#&/' /etc/modprobe.d/sch_netem-blacklist.conf
    ```

### Prebuilt VM
A prebuilt VM (OVA file) is also available [here](https://tu-dortmund.sciebo.de/s/sHiuKnXJRgMmDq1/download). Note that VM precision issues may affect `tc` limiting abilities, and it is advisable to allow only the use of one CPU core, though this may limit performance\[[1](https://stackoverflow.com/questions/72539814/mininet-ping-iperf3-got-unstable-measurement-results)\].

**VM credentials**:
- **User**: `core`
- **Password**: `core`

## Usage instructions
t.b.a

## Create Your own experiment
t.b.a

## Develop Your own (fast failover) routing algorithm
t.b.a

## Reproduce the measurements
t.b.a

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

