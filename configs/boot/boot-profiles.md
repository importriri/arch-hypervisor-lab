# Boot Profiles — Arch Linux

This system has 4 selectable boot profiles in systemd-boot.
Each profile loads a different set of kernel parameters depending on intended use.

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
Blacklists NVIDIA drivers and binds the GPU to vfio-pci.
The GPU is NOT usable on the host — reserved exclusively for VMs.

Key parameters:
- `vfio-pci.ids=10de:2470,10de:2248` — PCI IDs of RTX 3070 + HDMI audio
- `modprobe.blacklist=nouveau` — blocks the open-source driver
- `video=efifb:off` — disables EFI framebuffer (required on laptop)
- `pcie_port_pm=off` — **laptop freeze fix** (see problems/)
- `kvm.ignore_msrs=1` — prevents crashes in certain Windows games inside VM

## Arch Linux (Hardened)
Kernel with extra security patches.
Use: malware analysis, security testing, high-risk browsing.

## Hardware IDs (RTX 3070 Mobile)

```
10de:2470  →  NVIDIA GA104M GeForce RTX 3070 Mobile / Max-Q
10de:2248  →  NVIDIA GA104 High Definition Audio Controller
```

Verify with: `lspci -nnk | grep -A3 NVIDIA`
