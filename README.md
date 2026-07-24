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
Every phase is written — partitioning through Secure Boot signing, plus an
optional second encrypted disk dedicated to VM storage — and is being
published milestone by milestone. Three test layers back it: unit (real
functions, stubbed tools), a real LUKS2 header check, and a full
partition→mount pipeline on loop devices. What's left is real-hardware validation.
The live roadmap is in that repo's README.

**2. Configuration → Ansible roles** — 🚧 *in progress*
Everything after the base install: network domains (nftables), libvirt VMs,
VFIO/GPU passthrough, the GPU handoff hooks, host hardening, the malware lab.
Written as reusable roles, so the whole machine can be rebuilt with one command.
Lives in its own repo:
[privatestack-ansible](https://github.com/importriri/privatestack-ansible) —
the brick catalog in its README tracks what has landed.

**3. The lab → this repo**
Configs and writeups land here as each piece goes live and gets verified
on real hardware.

Right now the work is happening in **stages 1 and 2**.

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

On desktops the same power-management family usually announces itself in
`dmesg` (`Unable to change power state from D3cold to D0`) before failing;
on this laptop the freeze lands before any log is written. The laptop/Optimus
case is still missing from the guides.

→ Full writeup: [`problems/gpu-freeze-power-management.md`](problems/gpu-freeze-power-management.md)

---

## Looking Glass without a dummy plug

The GPU belongs to the VM, so the host needs a window into it. Looking Glass
moves raw frames through shared memory — no encode, no network.

It has one requirement that is easy to miss: **the passed GPU must have a
display attached**, physical or dummy, or Windows disables its output and the
capture finds nothing. On this laptop the only port wired to the dGPU is a
broken HDMI, so a dummy plug is not an option. The way through is an indirect
display driver — a monitor that exists in software.

Three writeups came out of getting there, and each one is a different class of
mistake:

- **[The host application exits in 66 ms](problems/geforce-passthrough-needs-a-display.md)** —
  no display on the card. Includes three plausible dead ends: Looking Glass's own
  IDD is not shipped yet, EDID-from-file in the NVIDIA panel is Quadro-only, and
  a `winget` install that reports success while installing no driver.
- **[Looking Glass shows a desktop while the host is not running](problems/looking-glass-shows-spice-and-calls-it-success.md)** —
  the SPICE fallback is indistinguishable from success by eye. Two days were
  spent tuning a path that was carrying nothing.
- **[/dev/kvmfr0 permission denied, twice](problems/kvmfr-device-permissions.md)** —
  two processes need the same node, and udev does not apply rules to devices
  that already exist.

Setup and verification protocol: [`configs/looking-glass.md`](configs/looking-glass.md).
The host side is automated as an ansible brick; the guest half stays manual and
is written down in [`configs/virtual-display-windows.md`](configs/virtual-display-windows.md).

---

## Repo structure

```
arch-hypervisor-lab/
├── README.md
├── SETUP.md                   # how to reproduce the lab, stage by stage
├── problems/                  # bugs encountered and solved — written as they happen
├── configs/
│   ├── network-domains.md     # the four network segments, nftables design
│   ├── looking-glass.md       # the window onto the GPU VM, host side
│   ├── virtual-display-windows.md  # the guest half, done by hand once
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
