# Arch Linux Hypervisor Lab

One laptop, four isolated virtual machines, one GPU passed between them.
This repo documents the build: configs, boot profiles, and every bug I hit on the way.

---

## What you will build

```
┌──────────────────────────────────────────────────────────────────┐
│              HOST — Arch Linux (hypervisor-01)                   │
│         TTY only · systemd-boot · Btrfs+LUKS2 · nftables        │
│         iGPU → TTY display · Sway (minimal, for Looking Glass)   │
├──────────────┬──────────────┬──────────────┬─────────────────────┤
│  🟢 CLEAN    │  🟠 DIRTY    │  🔴 DEV/3D   │  🟡 MALWARE LAB    │
│  Gaming      │  Gaming      │  Work        │  Static & dynamic   │
│  verified    │  mods        │  software    │  malware analysis   │
│  10.10.1.0   │  10.10.2.0   │  10.10.3.0   │  10.10.4.0 ISOLATED │
├──────────────┴──────────────┴──────────────┴─────────────────────┤
│       dGPU — one VM at a time via VFIO · Looking Glass           │
│               GPU handoff protocol between domains               │
└──────────────────────────────────────────────────────────────────┘
```

The host has no desktop environment.
Sway is installed only as a minimal Wayland compositor to run the Looking Glass client.

---

## How I am building it

Three stages. Each one reproducible on its own.

**1. Base install → [arch-bootstrap](https://github.com/importriri/arch-bootstrap)** — 🚧 *in progress*
A bash installer written and tested from scratch: LUKS2, Btrfs subvolumes,
systemd-boot, Secure Boot with custom keys, `linux-hardened`, zram.
Partitioning is done and covered by a loop-device test suite; encryption is next.
The live roadmap is in that repo's README.

**2. Configuration → Ansible roles** — 📋 *planned*
Everything after the base install: network domains (nftables), libvirt VMs,
VFIO/GPU passthrough, the GPU handoff hooks, host hardening, the malware lab.
Written as reusable roles, so the whole machine can be rebuilt with one command.

**3. The lab → this repo**
Configs and writeups land here as each piece goes live and gets verified
on real hardware.

Right now the work is happening in **stage 1**.

---

## Prerequisites

- A laptop with a dedicated NVIDIA GPU (Optimus/hybrid mode)
- Intel CPU with VT-d (IOMMU) enabled in BIOS
- Willingness to install Arch Linux from scratch

---

## Laptop-specific bug — not covered by most guides

**Symptom:** immediate total system freeze on VM startup with GPU passthrough.
**Cause:** aggressive PCIe port power management enforced by laptop firmware.
**Fix:** `pcie_port_pm=off` (and optionally `pcie_aspm=off`) in the systemd-boot VFIO kernel parameters.
**Time to find it:** ~2 months. No AI tools were available at the time.

This bug does not appear on desktop hardware and is not documented in most VFIO guides.

→ Full writeup: [`problems/gpu-freeze-power-management.md`](problems/gpu-freeze-power-management.md)

---

## Repo structure

```
arch-hypervisor-lab/
├── README.md
├── problems/                  # bugs encountered and solved — written as they happen
├── configs/
│   ├── network-domains.md     # the four network segments, nftables design
│   ├── boot/                  # systemd-boot profiles (VFIO entry included)
│   ├── libvirt/               # VM XML definitions
│   ├── hooks/                 # GPU switch scripts
│   └── malware-lab/           # REMnux/INetSim configuration
└── screenshots/               # proof it works
```

---

## Keywords

`KVM laptop` `VFIO laptop` `GPU passthrough laptop` `NVIDIA Optimus passthrough`
`pcie_port_pm laptop fix` `KVM freeze laptop` `four domains hypervisor`
`Windows VM KVM` `gaming VM Linux` `systemd-boot VFIO` `Arch Linux hypervisor`
`Looking Glass KVM` `malware lab KVM` `TTY hypervisor`
