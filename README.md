# Arch Linux Hypervisor Lab

Architecture notes, configuration examples and test records for an Arch Linux
KVM/VFIO lab running on two Acer laptops.

```text
Arch Linux host (LUKS2, Btrfs, linux-hardened, systemd-boot)
|
|-- clean     10.10.1.0/24  NAT       trusted accounts and games
|-- dirty     10.10.2.0/24  NAT       mods and untrusted software
|-- dev       10.10.3.0/24  NAT       development and 3D work
|-- lab       10.10.4.0/24  ISOLATED  malware and OT experiments
`-- services  10.10.5.0/24  NAT       private service VMs

NVIDIA dGPU -- VFIO --> one of clean / dirty / dev / lab
```

The dGPU is assigned to one workload VM at a time. It is never part of the
`services` domain. The stage-2 foundation remains headless for recovery, while
the normal laptop target adds Sway and the Looking Glass host transport on the
iGPU in that order.

## Repository set

1. [arch-bootstrap](https://github.com/importriri/arch-bootstrap) installs the
   encrypted base system and optional encrypted VM disk.
2. [privatestack-ansible](https://github.com/importriri/privatestack-ansible)
   configures KVM, networking, isolation, boot profiles, GPU hand-off, the
   local cockpit, Looking Glass host transport and explicit VM/service
   lifecycle transactions.
3. This repository records the design, setup order, failures and compatibility
   results.

The known profiles are an Acer Nitro 5 with an RTX 3060 Mobile and an Acer
Predator Helios 300 with an RTX 3070 Mobile. Individual components have been
exercised on both machines, but a complete compatibility result is recorded
only after a clean install and a second idempotent Ansible run. The Nitro
bootstrap-to-stage-2 host path has been reproduced and the immediate second
stage-2 apply reported `changed=0`; full compatibility remains pending until
the frozen clean-install and guest-cycle evidence is complete. Current status
is in [`hardware/README.md`](hardware/README.md).

## PCIe power-management freeze

The immediate host freeze was first isolated on the Nitro while starting a
passthrough guest. Disabling PCIe port power management with
`pcie_port_pm=off` stopped the freeze. The Predator later reproduced the same
failure without that parameter and confirmed the same fix. `pcie_aspm=off` is
kept in the VFIO profile as the related fallback used by this lab.

Full notes:
[`problems/gpu-freeze-power-management.md`](problems/gpu-freeze-power-management.md).

## Looking Glass without a physical display

On the Nitro, the only output wired to the passed GPU cannot be used. A Windows
virtual display keeps the RTX 3060 active, kvmfr carries the framebuffer and
SPICE remains available only for input and recovery. The Looking Glass client
log and kvmfr state are used to distinguish real shared-memory capture from the
plausible SPICE fallback.

Relevant files:

- [`configs/looking-glass.md`](configs/looking-glass.md)
- [`configs/virtual-display-windows.md`](configs/virtual-display-windows.md)
- [`problems/geforce-passthrough-needs-a-display.md`](problems/geforce-passthrough-needs-a-display.md)
- [`problems/looking-glass-shows-spice-and-calls-it-success.md`](problems/looking-glass-shows-spice-and-calls-it-success.md)
- [`problems/kvmfr-device-permissions.md`](problems/kvmfr-device-permissions.md)
- [`problems/looking-glass-client-ini-comments.md`](problems/looking-glass-client-ini-comments.md)

## Repository map

```text
configs/      boot, network, libvirt and guest configuration examples
hardware/     compatibility matrix, evidence policy and report template
problems/     failure investigations and fixes
scripts/      hardware report collector and repository verifier
```

The end-to-end command order is maintained in [`SETUP.md`](SETUP.md). Network
contracts are in [`configs/network-domains.md`](configs/network-domains.md),
and the four boot modes are indexed in
[`configs/boot/boot-profiles.md`](configs/boot/boot-profiles.md).

Run the repository checks with:

```bash
# Validate relative links, hardware states and checked-in configuration contracts.
python scripts/verify_repo.py

# Parse the hardware collector without executing it or reading host data.
bash -n scripts/collect-hardware-report.sh
```

## Scope

The isolated network is intended for defensive research and controlled tests
on systems you own or are authorized to examine. It has no uplink by default,
and the host rules block forwarding between trust domains. Any deliberate LAN
exposure belongs in the documented allowlist.
