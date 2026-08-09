# Bug: Total system freeze on VM startup with GPU passthrough

## Symptom

As soon as a VM with RTX 3070 passthrough is started, **immediate and total system freeze** —
hypervisor included. No readable logs, no visible errors, no recovery possible without a hard reset.

## Hardware

- Laptop: Acer Predator Helios 300
- CPU: Intel Core i7 10th Gen (Comet Lake-H)
- Dedicated GPU (VM): NVIDIA GeForce RTX 3070 Mobile / Max-Q `[10de:249d]`
- GPU HDMI Audio: NVIDIA GA104 HD Audio `[10de:228b]`
- Integrated GPU (host display): Intel CometLake-H GT2 UHD Graphics
- OS: Arch Linux (bug found on `linux-zen`; the fix is kernel-independent — the profile now runs `linux-hardened`)
- Bootloader: systemd-boot
- Stack: KVM/QEMU/libvirt + VFIO

## Why it is hard to diagnose

The freeze happens **before any log is written**.
No terminal output, nothing in `journalctl`, no way to read what went wrong.

Laptop GPU passthrough documentation exists but is scattered across forums and
rarely covers Optimus hybrid setups in depth. The specific `pcie_port_pm=off` fix
was not found in any guide at the time. The solution came from months of
systematic trial and error on r/VFIO and Level1Techs.

## Root cause

The Linux kernel tries to manage the power state of the PCIe ports connected
to the dedicated GPU. On laptops, the Acer firmware enforces aggressive PCIe port
power management even when the GPU is under VFIO control. The GPU fails to respond
correctly, the PCI bus stalls, and the entire system freezes.

## Time spent

~2 months. Documentation for this specific combination (laptop + Optimus + VFIO
+ this firmware behavior) was not found anywhere.

## Solution

Add the following parameters to the kernel options in the systemd-boot VFIO profile:

```
# /boot/loader/entries/Arch-Linux-Hardened-Vfio.conf

title   Arch Linux (Vfio)
linux   /vmlinuz-linux-hardened
initrd  /initramfs-linux-hardened.img
# LUKS container UUID (from: cryptsetup luksUUID /dev/nvme0n1pX) — NOT the GPT PARTUUID
options rd.luks.name=YOUR-LUKS-UUID-HERE=cryptroot root=/dev/mapper/cryptroot rw rootfstype=btrfs rootflags=subvol=@ zswap.enabled=0
options intel_iommu=on iommu=pt
options vfio-pci.ids=10de:249d,10de:228b
options modprobe.blacklist=nouveau module_blacklist=nouveau nvidia-drm.modeset=0
options video=efifb:off pcie_port_pm=off pcie_aspm=off kvm.ignore_msrs=1

# Replace YOUR-LUKS-UUID-HERE with your actual LUKS container UUID
# To find it: cryptsetup luksUUID /dev/nvme0n1pX   (the LUKS partition, e.g. ...p2)
#
# Key parameters explained:
#   intel_iommu=on iommu=pt  — enables IOMMU in passthrough mode (required for VFIO)
#   vfio-pci.ids=...         — binds RTX 3070 GPU + HDMI audio to vfio-pci at boot
#   modprobe.blacklist=nouveau — blocks nouveau at the modprobe/udev level
#   module_blacklist=nouveau   — same block, enforced by the kernel itself;
#                              two different mechanisms on purpose (belt+braces)
#   video=efifb:off          — disables EFI framebuffer (required on laptops with Optimus)
#   pcie_port_pm=off         — disables PCIe port power management
#                              THIS is the fix for the immediate freeze on this laptop
#   pcie_aspm=off            — disables Active State Power Management
#                              redundant on this hardware but useful safety net
#                              for similar laptops where freeze persists
#   kvm.ignore_msrs=1        — prevents crashes in Windows games that access
#                              unsupported MSR registers inside the VM

> `pcie_port_pm=off` and `pcie_aspm=off` control two different mechanisms.
> On this hardware only `pcie_port_pm=off` was needed to fix the freeze.
> Both are included for completeness and to help users with similar but not identical hardware.

## Verification

After rebooting with the Vfio profile:

```bash
# GPU must show vfio-pci as driver
lspci -nnk | grep -A3 NVIDIA
# Expected: Kernel driver in use: vfio-pci

# IOMMU must be active
dmesg | grep -i iommu | head -5
# Expected: IOMMU enabled / Adding to iommu group
```

Windows 11 inside the VM should recognize the GPU as "NVIDIA GeForce RTX 3070 Laptop GPU"
in Task Manager with 8GB dedicated VRAM.

## How it was found

Systematic trial and error, copying kernel parameters from various forum threads
(Reddit r/VFIO, Level1Techs, Arch Wiki). When the freeze disappeared, the responsible
parameter was identified by progressive exclusion.

## Note for others with the same issue

If you have a laptop with a dedicated NVIDIA GPU in Optimus/hybrid mode and experience
an immediate total freeze when starting a VFIO passthrough VM:

1. First try `pcie_port_pm=off` alone
2. If freeze persists, add `pcie_aspm=off`
3. Make sure `intel_iommu=on iommu=pt` is also present

## Related reports (found later)

When this fix was isolated, none of the reports below existed yet. Since then
the same power-management family has started surfacing on desktops, where it
announces itself in `dmesg` as
`Unable to change power state from D3cold to D0` before failing:

- [Arch BBS — NVIDIA GPU passthrough freezes on host startup](https://bbs.archlinux.org/viewtopic.php?id=286946)
  (mid-2023, desktop) — solved with `pcie_port_pm=off`, found by the author
  "in a post in proxmox forum"
- [Arch BBS — VFIO PCI graphics card freezing the system](https://bbs.archlinux.org/viewtopic.php?id=286995)
  (late 2023, HP Z840 workstation) — same parameter in the kernel cmdline
- Recent Proxmox-oriented guides now ship `pcie_port_pm=off pcie_aspm=off`
  in their example cmdlines for desktop passthrough

On this laptop the D3cold error never gets the chance to print — the freeze
lands before any log is written, which is what made the diagnosis blind.
The laptop/Optimus case — firmware-enforced port power management with the
GPU under VFIO control — is still not covered by the guides. This page is
that writeup.

## References

- [Arch Wiki — PCI passthrough via OVMF](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF)
- [Reddit r/VFIO](https://www.reddit.com/r/VFIO/)
- [Level1Techs Forum](https://forum.level1techs.com/)
