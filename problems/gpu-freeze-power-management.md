# Bug: Total system freeze on VM startup with GPU passthrough

## Symptom

As soon as a VM with RTX 3070 passthrough is started, **immediate and total system freeze** —
hypervisor included. No readable logs, no visible errors, no recovery possible without a hard reset.

## Hardware

- Laptop: Acer Predator Helios 300
- CPU: Intel Core i7 10th Gen (Comet Lake-H)
- Dedicated GPU (VM): NVIDIA GeForce RTX 3070 Mobile / Max-Q `[10de:2f4a]`
- GPU HDMI Audio: NVIDIA GA104 HD Audio `[10de:2f5f]`
- Integrated GPU (host display): Intel CometLake-H GT2 UHD Graphics
- OS: Arch Linux, linux-zen kernel
- Bootloader: systemd-boot
- Stack: KVM/QEMU/libvirt + VFIO

## Why it is hard to diagnose

The freeze happens **before any log is written**.
No terminal output, nothing in `journalctl`, no way to read what went wrong.

Laptop GPU passthrough documentation exists but is scattered across forums and
rarely covers Optimus hybrid setups in depth. The specific `pcie_port_pm=off` fix
was not found in any guide at the time — no AI tools were available either.
The solution came from months of systematic trial and error on r/VFIO and Level1Techs.

## Root cause

The Linux kernel tries to manage the power state of the PCIe ports connected
to the dedicated GPU. On laptops, the Acer firmware enforces aggressive PCIe port
power management even when the GPU is under VFIO control. The GPU fails to respond
correctly, the PCI bus stalls, and the entire system freezes.

## Time spent

~2 months. No AI tools available at the time. Documentation for this specific
combination (laptop + Optimus + VFIO + this firmware behavior) was not found anywhere.

## Solution

Add the following parameters to the kernel options in the systemd-boot VFIO profile:

```
# /boot/loader/entries/Arch-Linux-Zen-Vfio.conf

title   Arch Linux (Vfio)
linux   /vmlinuz-linux-zen
initrd  /initramfs-linux-zen.img
options cryptdevice=PARTUUID=YOUR-PARTUUID-HERE:root root=/dev/mapper/root \
        zswap.enabled=0 rw rootfstype=btrfs \
        intel_iommu=on iommu=pt \
        nvidia-drm.modeset=0 \
        rd.driver.blacklist=nouveau \
        modprobe.blacklist=nouveau \
        module_blacklist=nouveau \
        vfio-pci.ids=10de:249d,10de:228b \
        video=efifb:off \
        pcie_port_pm=off \
        pcie_aspm=off \
        kvm.ignore_msrs=1
```

### Parameter breakdown

| Parameter | Purpose |
|---|---|
| `intel_iommu=on iommu=pt` | Enables IOMMU in passthrough mode — required for VFIO |
| `pcie_port_pm=off` | **The actual fix** — disables PCIe port power management |
| `pcie_aspm=off` | Disables Active State Power Management — redundant on this hardware but useful safety net for similar laptops |
| `kvm.ignore_msrs=1` | Prevents crashes in Windows games accessing unsupported MSR registers |

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

## References

- [Arch Wiki — PCI passthrough via OVMF](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF)
- [Reddit r/VFIO](https://www.reddit.com/r/VFIO/)
- [Level1Techs Forum](https://forum.level1techs.com/)
