# Looking Glass transport

Looking Glass is the display path for GPU workloads whose dGPU cannot drive the
laptop panel. kvmfr carries shared memory between QEMU and the physical-host
client. SPICE stays configured for input/recovery plumbing; a visible SPICE
surface is not proof that kvmfr video is working.

## Shared contract

The active transport values live in `hyperlab-ansible/group_vars/all/looking-glass.yml`.
Do not duplicate them in a runbook.

Current Nitro contract:

- pinned Looking Glass build: `B7-263-g0140a3f6fb`;
- target frame: 1920×1080;
- host kvmfr shared region: 64 MiB;
- device: `/dev/kvmfr0`;
- SPICE endpoint used by the client: `127.0.0.1:5900`.

The role calculates the shared-memory size from the declared frame dimensions and
selects the next supported allocation bucket. The 64 MiB value is therefore
policy, not a number to copy into unrelated guest module settings.

## Windows path

```text
RTX dGPU
  -> Windows virtual display
  -> Looking Glass host application
  -> ivshmem / host kvmfr backing
  -> physical-host Looking Glass client
```

The Arch host side is automated by `hyperlab-ansible`. Windows installation,
virtio/NVIDIA drivers, the signed Looking Glass host application and the virtual
display remain workshop steps inside the private Windows image.

The physical dGPU output on the Nitro is not usable, so the virtual display is
what keeps a capturable desktop on that GPU. See
[`virtual-display-windows.md`](virtual-display-windows.md).

## Linux VFIO path

```text
RTX dGPU
  -> NVIDIA-only Hyprland
  -> HEADLESS-0
  -> XDPH / PipeWire
  -> Looking Glass Linux sender
  -> guest IVSHMEM-backed /dev/kvmfr0
  -> host kvmfr backing
  -> physical-host Looking Glass client
```

The Linux sender is experimental and stays disabled by default. It is built from
the same pinned upstream commit as the client. The guest kvmfr device comes from
the IVSHMEM PCI function; the guest must not configure host-style
`static_size_mb` policy.

Nitro has already produced real 1920×1080 frames through this path. The remaining
release work is fresh-session headless persistence, deterministic XDPH source
selection and keyboard/pointer return.

## Host ownership

`hyperlab-ansible` owns:

- kvmfr DKMS build and boot loading;
- the host shared-memory size;
- device permissions and the libvirt QEMU device ACL;
- the pinned Wayland Looking Glass client;
- client configuration;
- VFIO domain ivshmem/SPICE/input plumbing.

The explicit libvirt device ACL matters. Unix device mode alone is not enough,
and replacing libvirt's implicit device set with an incomplete ACL can remove
QEMU access to core devices such as `/dev/kvm`.

## What proves video

A valid proof needs more than a window that looks right:

1. the workload owns the intended NVIDIA GPU;
2. the producer reports real frames at the expected dimensions;
3. `/dev/kvmfr0` is the configured shared-memory path;
4. the physical-host client receives those frames;
5. a screenshot or benchmark is tied to the same run.

For Windows, use the guest host log plus the physical client log. For Linux, use
the sender PipeWire/frame log plus the client and kvmfr state. SPICE appearance
alone does not satisfy the gate.

## Input is a separate gate

Video and input fail independently. The current Linux proof established video
without working keyboard/pointer return. Keep input as its own acceptance item
instead of treating a successful frame as proof that the complete interactive
path is finished.

## Portability

A laptop with a usable dGPU-connected output may use a physical dummy display
instead of a software virtual display. The Nitro reference machine cannot rely on
that path. Predator must re-run the same transport gates against the frozen
software commits rather than inherit Nitro's result from a matching GPU family.
