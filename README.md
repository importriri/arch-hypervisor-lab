# Arch Linux Hypervisor Lab

A practical companion to building a GPU passthrough hypervisor on a laptop,
from a clean Arch Linux install to a fully isolated four-domain lab.

A step-by-step guide to building a GPU passthrough hypervisor on a laptop — from a clean Arch Linux install to a fully isolated four-domain lab. Config files, boot profiles and documented bug fixes added progressively."

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

## Prerequisites

- A laptop with a dedicated NVIDIA GPU (Optimus/hybrid mode)
- Intel CPU with VT-d (IOMMU) enabled in BIOS
- Willingness to install Arch Linux from scratch

---

## Course structure — what each chapter builds

| Chapter | Topic | Config files added to this repo |
|---|---|---|
| 01 | Linux fundamentals, bash, Git | *(repo initialized)* |
| 02 | Networking, virtual bridges, nftables | `configs/network-domains.md` |
| 03 | Btrfs/LUKS2, systemd, Arch install from scratch | `configs/boot/` |
| 04 | KVM, IOMMU, VFIO, GPU passthrough, CPU pinning, Looking Glass | `configs/libvirt/` |
| 05 | Four isolated domains, GPU hooks, host hardening | `configs/hooks/` |
| 06 | Malware lab — REMnux, INetSim, static & dynamic analysis | `configs/malware-lab/` |

---

## Laptop-specific bug — not covered by the course

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
│   ├── boot/                  # systemd-boot profiles        (chapter 03)
│   ├── libvirt/               # VM XML definitions           (chapters 04-05)
│   ├── hooks/                 # GPU switch scripts           (chapter 05)
│   └── malware-lab/           # REMnux/INetSim configuration (chapter 06)
└── screenshots/               # proof it works
```

---

## Keywords

`KVM laptop` `VFIO laptop` `GPU passthrough laptop` `NVIDIA Optimus passthrough`
`pcie_port_pm laptop fix` `KVM freeze laptop` `four domains hypervisor`
`Windows VM KVM` `gaming VM Linux` `systemd-boot VFIO` `Arch Linux hypervisor`
`Looking Glass KVM` `malware lab KVM` `TTY hypervisor`
