# Windows guest display setup

This is the manual half of the Windows Looking Glass image. Do it in the private
workshop VM, verify it, then seal the image through the Stage 2 workshop flow.

The manual boundary exists because signed Windows drivers, account setup and the
virtual display are guest operations. The Arch host side remains declarative.

## Before starting

Require all of these first:

- Windows boots through the recovery console;
- Device Manager sees the passed NVIDIA GPU with its guest driver installed;
- the domain contains the managed IVSHMEM device, SPICE endpoint and virtio input
  devices;
- the host-side Looking Glass build is known. The Windows host application must
  use the same pinned build.

The current reference build is `B7-263-g0140a3f6fb`.

## 1. Install virtio input

Install the `vioinput` driver from the reviewed virtio-win media.

Do not rely on a legacy PS/2 keyboard/mouse path. The current managed VFIO domain
removes legacy PS/2 input; virtio input is part of the recovery/input contract.
A dead pointer or keyboard is therefore an input-device/driver problem until
proved otherwise, not evidence that frame capture failed.

## 2. Install IVSHMEM and the Looking Glass host application

Run the signed Looking Glass host installer for the exact build used by the
physical-host client. Install the IVSHMEM driver and host service.

Device Manager must show the IVSHMEM device without an error. A generic PCI RAM
controller means the driver did not bind and the shared-memory path is not ready.

## 3. Install the virtual display

The Nitro dGPU has no usable physical display attached. Without a display,
Windows may expose no capturable desktop on that adapter even though the NVIDIA
driver itself is healthy.

Install the reviewed signed Virtual Display Driver used by the private Windows
workshop. Verify that the new display adapter appears in Device Manager after the
required reboot. Keep installer/version evidence with the private workshop
receipt rather than hard-coding an unverified download step in this repository.

## 4. Set the capture mode

Set the virtual monitor to `1920x1080`. Keep the recovery display available until
Looking Glass has produced real frames and the guest log proves the intended
NVIDIA capture path.

The current host shared-memory contract is 64 MiB for the declared 1080p path.
That size is owned by `hyperlab-ansible/group_vars/all/looking-glass.yml`; do not
copy an older 32 MiB value from historical notes or invent a second guest module
size setting.

Once the Looking Glass path is proven, select only the intended virtual display
for normal use. Keep a documented recovery route so a wrong display selection
does not force an image rebuild.

## 5. Verify from the host-application log

A working Windows producer must identify the passed NVIDIA adapter and reach a
real capture start. For the pinned D3D12 path, the useful markers include:

```text
Device Description: NVIDIA GeForce RTX 3060 Laptop GPU
Trying           : D12
==== [ Capture Start ] ====
Using            : D12
```

`Failed to locate a valid output device` means the guest still has no usable
capture output on the intended adapter. Fix the virtual display before debugging
kvmfr on the Arch host.

The physical-host client must separately prove it receives real frames. A visible
SPICE desktop is recovery, not shared-memory evidence.

## 6. Seal instead of repeating the workshop

After drivers, capture, updates and reboot state are reviewed, collect the private
Windows workshop evidence and seal the exact qcow2 through
`hyperlab-ansible/docs/windows-image-workshop.md`.

Keep the personal clean image and generalized lower-trust template separate.
Credentials or personal identity from the clean image must not cross into the
dirty template.

## Failure map

| Symptom | First boundary to check |
| --- | --- |
| IVSHMEM appears as generic PCI RAM | IVSHMEM driver |
| no virtual display adapter | virtual-display installation |
| host log cannot locate output | virtual display / selected output |
| producer log is healthy but client has no frames | host kvmfr/client path |
| video works but keyboard/pointer does not | virtio/SPICE input path |
| visible recovery desktop without producer frames | SPICE fallback, not LG proof |
