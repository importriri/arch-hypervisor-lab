# Arch Linux Hypervisor Lab

Two target laptops, five security domains, and one NVIDIA dGPU passed to one
workload VM at a time. This repository is the public architecture record for a
three-repository pipeline: configs, validation evidence, compatibility status,
and every failure that changed the design.

## Architecture

```text
Arch Linux host (LUKS2 · Btrfs · linux-hardened · systemd-boot)
│
├── clean     10.10.1.0/24  NAT       verified gaming/accounts
├── dirty     10.10.2.0/24  NAT       mods and untrusted gaming software
├── dev       10.10.3.0/24  NAT       development and 3D work
├── lab       10.10.4.0/24  ISOLATED  malware/OT experiments
└── services  10.10.5.0/24  NAT       service VMs; explicit exposure only

NVIDIA dGPU ── VFIO ──> one of clean / dirty / dev / lab
                         (never services; trust-ranked handoff)
```

A network domain is not the same thing as a VM. Multiple service VMs can live
in `services`; the GPU-owning Windows templates live in the four workload
domains. The host remains headless by default. Sway and Looking Glass are
optional cockpit components, not a requirement of the secure base host.

## The published pipeline

1. **[arch-bootstrap](https://github.com/importriri/arch-bootstrap)** installs
   the encrypted Arch foundation and optional encrypted VM disk.
2. **[privatestack-ansible](https://github.com/importriri/privatestack-ansible)**
   detects a reviewed laptop profile and assembles KVM, VFIO, five networks,
   isolation and GPU handoff.
3. **This repository** records the intended architecture and the evidence that
   each exact commit worked on exact hardware.

The current known profiles are the Acer Nitro 5 with RTX 3060 Mobile and Acer
Predator Helios 300 with RTX 3070 Mobile. Both have component-level evidence;
neither is labelled a complete public-pipeline pass until a clean install and
second idempotent Ansible run are recorded. See
[`hardware/README.md`](hardware/README.md).

## Laptop-specific VFIO freeze

On the Predator, starting the RTX 3070 passthrough guest caused an immediate
host freeze before useful logs. The working boot profile disables PCIe port
power management with `pcie_port_pm=off` and keeps `pcie_aspm=off` as the
safety net.

Full writeup:
[`problems/gpu-freeze-power-management.md`](problems/gpu-freeze-power-management.md).

## Looking Glass without a dummy plug

The Nitro evidence covers the harder no-physical-display path: a Windows
virtual display keeps the passed RTX 3060 active, kvmfr carries the frames, and
SPICE is retained only for input/recovery. The client log, not the visible
window, is the success criterion.

Start here:

- [`configs/looking-glass.md`](configs/looking-glass.md)
- [`configs/virtual-display-windows.md`](configs/virtual-display-windows.md)
- [`problems/geforce-passthrough-needs-a-display.md`](problems/geforce-passthrough-needs-a-display.md)
- [`problems/looking-glass-shows-spice-and-calls-it-success.md`](problems/looking-glass-shows-spice-and-calls-it-success.md)
- [`problems/kvmfr-device-permissions.md`](problems/kvmfr-device-permissions.md)
- [`problems/looking-glass-client-ini-comments.md`](problems/looking-glass-client-ini-comments.md)

## Repository map

```text
configs/      reference boot, network, libvirt and guest configuration
hardware/     compatibility matrix, evidence policy and report template
problems/     root-cause writeups, indexed by symptom
scripts/      sanitized hardware report and repository verifier
SETUP.md      end-to-end execution and validation order
```

Run the repository checks with:

```bash
python scripts/verify_repo.py
bash -n scripts/collect-hardware-report.sh
```

## Scope and safety

The isolated lab is for defensive research, malware analysis and controlled
experiments on hardware and systems you own or are authorized to test. The
network model denies cross-domain forwarding and gives the lab no uplink by
default. Any deliberate exposure belongs in a reviewed allowlist, never in an
ad-hoc host rule.

## Keywords

`KVM laptop` `VFIO laptop` `GPU passthrough laptop` `NVIDIA Optimus passthrough`
`pcie_port_pm laptop fix` `five domain hypervisor` `Looking Glass kvmfr`
`Arch Linux hypervisor` `isolated malware lab` `hardware compatibility matrix`
