# Boot Profiles — Arch Linux

This system has 4 selectable boot profiles in systemd-boot.
Each profile loads a different set of kernel parameters depending on intended use.

**Vfio and Hardened are the base of the lab. Integrated and Nvidia are optional conveniences** (battery saving and native gaming) — the lab works without them.

```
┌──────────────────────────────────────────────────────────────┐
│                        BOOT MENU                             │
├──────────────────────────┬───────────────────────────────────┤
│ Arch Linux (Integrated)  │ Intel iGPU only — light use       │
│ Arch Linux (Nvidia)      │ NVIDIA dGPU — native host gaming  │
│ Arch Linux (Vfio)      ▶ │ dGPU → VFIO — VM passthrough      │
│ Arch Linux (Hardened)    │ hardened kernel — max security    │
└──────────────────────────┴───────────────────────────────────┘
```

## Arch Linux (Integrated)
Uses only the Intel integrated GPU (i915 driver). NVIDIA completely disabled.
Use: light work, battery saving.

## Arch Linux (Nvidia)
Loads proprietary NVIDIA drivers on the host.
Use: native Linux gaming, rendering, Blender.

## Arch Linux (Vfio) ← main profile for this repo
Blocks the open-source nouveau driver so vfio-pci can claim the card at boot.
The GPU is NOT usable on the host — reserved exclusively for VMs.
Runs on `linux-hardened` — the same kernel the final hypervisor host uses.

Key parameters:
- `vfio-pci.ids=10de:249d,10de:228b` — PCI IDs of RTX 3070 + HDMI audio
- `modprobe.blacklist=nouveau` — blocks the open-source driver
- `video=efifb:off` — disables EFI framebuffer (required on laptop)
- `pcie_port_pm=off` — **laptop freeze fix** (see problems/)
- `kvm.ignore_msrs=1` — prevents crashes in certain Windows games inside VM

## Arch Linux (Hardened)
Kernel with extra security patches.
Use: malware analysis, security testing. High-risk browsing lives in an isolated Whonix VM under the Vfio profile.

## Hardware IDs (RTX 3070 Mobile)

```
10de:249d  →  NVIDIA GA104M GeForce RTX 3070 Mobile / Max-Q
10de:228b  →  NVIDIA GA104 High Definition Audio Controller
```

Verify with: `lspci -nnk | grep -A3 NVIDIA`
