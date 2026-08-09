# Arch Linux Hypervisor Lab

Architecture, hardware evidence and failure writeups for a laptop KVM/VFIO lab
on Arch Linux.

The project is split so installation, configuration and evidence do not certify
one another:

```text
arch-bootstrap  ->  hyperlab-ansible  ->  arch-hypervisor-lab
base system         host + workloads      evidence + writeups
```

Start with [`SETUP.md`](SETUP.md) for the Nitro path.

## Lab shape

```text
Arch Linux host
|
|-- clean     10.10.1.0/24  NAT       trusted accounts and games
|-- dirty     10.10.2.0/24  NAT       untrusted software and mods
|-- dev       10.10.3.0/24  NAT       development and 3D work
|-- lab       10.10.4.0/24  ISOLATED  controlled research
`-- services  10.10.5.0/24  NAT       private service VMs

NVIDIA dGPU -- VFIO --> one workload VM at a time
```

The host uses the iGPU for Sway and Looking Glass. The dGPU is not shared by the
host desktop. `services` never participates in GPU rotation.

## Repository set

1. [`arch-bootstrap`](https://github.com/importriri/arch-bootstrap) installs the
   encrypted Arch base and writes the storage hand-off contract.
2. [`hyperlab-ansible`](https://github.com/importriri/hyperlab-ansible) configures
   KVM, VFIO, networking, isolation, the Sway cockpit and Looking Glass, then
   owns explicit image/VM/service transactions.
3. This repository records what the architecture is and what has actually been
   proven on hardware.

A green CI run is not a compatibility claim. Hardware status changes only after
the named machine runs the matching frozen commits and evidence gate.

## Hardware status

The Nitro
bootstrap-to-stage-2 host path has been reproduced on the Acer Nitro 5 with an
RTX 3060 Mobile. Within that path,
the normal laptop target adds Sway and the Looking Glass host transport in that
order. Host VFIO and the accelerated Linux video path have real evidence. Final
Linux guest session persistence and Looking Glass input checks are still open.

The Acer Predator Helios 300 with RTX 3070 Mobile has a reviewed profile and
individual component history, but the complete pipeline remains pending until it
replays the same frozen repository commits used for the Nitro release.

See [`hardware/README.md`](hardware/README.md) and
[`hardware/compatibility.yml`](hardware/compatibility.yml).

## Why the problem notes matter

The useful parts of a hardware lab are usually the assumptions that turned out
to be wrong. `problems/` keeps those failures with their symptom, cause, fix and
verification so a future refactor does not have to rediscover them.

Notable examples include PCIe power-management freezes, kvmfr permissions,
Looking Glass display requirements and configuration parsing failures.

## Repository map

- `configs/`: boot, network, libvirt and display contracts;
- `hardware/`: compatibility policy, reports and evidence templates;
- `problems/`: failure investigations;
- `scripts/`: sanitized hardware collection and repository checks;
- `SETUP.md`: operator path from a clean machine to the lab.

Run the repository checks before publishing evidence:

```bash
python scripts/verify_repo.py
bash -n scripts/collect-hardware-report.sh
```

## Scope

The isolated network is for controlled work on systems you own or are authorized
to examine. It has no uplink by default and the host blocks forwarding between
trust domains unless an exposure is explicitly declared.

## Author

[importriri](https://github.com/importriri) is the author and maintainer.
