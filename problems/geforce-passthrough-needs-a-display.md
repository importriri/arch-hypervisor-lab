# Bug: the Looking Glass host application exits in 66 milliseconds

## Symptom

The host application starts inside the guest, opens the shared memory
correctly, and then dies before anything reaches the host. From
`%ProgramData%\Looking Glass (host)\looking-glass-host.txt`:

```
ivshmemInit          | IVSHMEM 0* on bus 0x0, device 0x4, function 0x0
app_main             | IVSHMEM Size     : 32 MiB
app_main             | KVMFR Version    : 20
app_main             | Trying           : D12
d12_enumerateDevices | Not using unsupported adapter: Microsoft Basic Render Driver
d12_enumerateDevices | Failed to locate a valid output device
captureStart         | Failed to initialize the capture device
app_main             | Trying           : DXGI
dxgi_init            | Failed to locate a valid output device
app_main             | Failed to find a supported capture interface
app_main             | Host application exited
```

Total elapsed: 66 ms. Nothing is wrong with the transport — the shared memory
is mapped, the version handshake is fine. The client, meanwhile, shows a
desktop and appears to work, which is
[its own trap](looking-glass-shows-spice-and-calls-it-success.md).

## Setup

- Guest: Windows 11, RTX 3060 Mobile passed through, NVIDIA driver installed
  and the card in use
- Host: Arch Linux, Looking Glass `B7-263-g0140a3f6fb`
- **The laptop's HDMI port is physically broken**, and on this chassis it is the
  only port wired to the dGPU

## Root cause

A GPU with no display attached has no output to capture. Windows disables the
output of a display adapter with nothing on it, and Looking Glass captures a
*display*, not a device — so there is nothing for D3D12 or DXGI to enumerate.

The desktop Windows was drawing lived on the emulated adapter, and Looking
Glass rejects that on purpose — the log says so in the line above the failure:
*Not using unsupported adapter: Microsoft Basic Render Driver*. Capturing the
software rasteriser would produce a picture and defeat the entire point.

Upstream states the requirement plainly: the guest GPU must have a monitor
attached, physical or dummy. Confirmed from inside the guest by NVIDIA's own
tooling, which reported *no displays connected to this GPU* while the desktop
was visibly on screen — on the other adapter.

## Why it is hard to diagnose

The obvious reading of "no dummy plug needed, use a virtual display" is that the
virtual display is a convenience. It is not: on this hardware it is the only
possible display. And the failure is silent from the host side — the client
keeps showing a picture, so the guest log is the only place the truth appears.

## Three dead ends, all plausible

**1. Looking Glass's own indirect display driver (LGIdd).** Upstream has one in
development, and its existence in the source tree makes it look installable. It
is not shipped: the installer for this build offers exactly four components —
IVSHMEM driver, the host service, and two shortcuts. Upstream's own release
notes place finishing it *after* B7 ships. Two hours went into looking for a
checkbox that does not exist.

**2. Loading an EDID from file in the NVIDIA Control Panel.** This works, and is
a genuinely elegant solution to exactly this problem — on **Quadro** cards only.
GeForce refuses; it wants a signal from a physically wired port. Any memory of
having done this before on a GeForce is a memory of bare metal, where the
laptop's own panel was that display.

**3. `winget install --id=VirtualDrivers.Virtual-Display-Driver -e`.** Reports
success. Creates no device. It drops files without installing the driver, and a
reboot changes nothing — Device Manager still shows two display adapters.
The driver installs from the GUI installer on the Releases page, and only from
there.

## Solution

A third-party indirect display driver, installed from its GUI installer:
[VirtualDrivers/Virtual-Display-Driver](https://github.com/VirtualDrivers/Virtual-Display-Driver)
("VDD by MTT"), signed and maintained. It creates a monitor in software on its
own adapter; Windows composes it with the dGPU; Looking Glass captures it.

Full procedure: [`../configs/virtual-display-windows.md`](../configs/virtual-display-windows.md).

## Verification

The same log, after:

```
d12_enumerateDevices | Device Name       : \\.\DISPLAY3
d12_enumerateDevices | Device Description: NVIDIA GeForce RTX 3060 Laptop GPU
d12_dd_init          | Feature Level     : 0xb100
captureStart         | ==== [ Capture Start ] ====
app_main             | Using            : D12
lgmpSetup            | Max Frame Size   : 14 MiB
```

Note *which* device is being captured: `DISPLAY3` is the RTX 3060. The concern
that a software virtual display would drag the capture back onto the emulated
adapter did not materialise — the desktop is composed by the dGPU and captured
from the dGPU.

Proof it is really the hardware path, measured inside the VM through Looking
Glass: **Unigine Valley, Extreme HD preset, 8×AA, 1920×1080 — 46.8 FPS average**
(min 18.7, max 65.5), GPU reporting 2100 MHz and 86 °C. The software adapter
scores single digits.

## Note for others

**The virtual display is not a downgrade in rendering.** 3D work already runs on
the dGPU regardless of where the monitor lives; attaching a real display would
not add frames. What a hardware dummy plug buys is slightly steadier capture
(reports on r/VFIO put a software IDD marginally behind on frame drops) and a
working display section in the NVIDIA Control Panel. Neither is worth chasing if
your hardware cannot provide the port.

**The NVIDIA Control Panel will keep saying no display is attached.** True, and
harmless: the virtual monitor is on the IDD adapter, not on a physical output.
It is not a symptom.

**The real performance levers are elsewhere.** 86 °C is where this card
throttles, and that throttle is what the 18.7 FPS minimum measures. CPU pinning
and cooling move that number; the display path does not.

## References

- [Looking Glass — requirements](https://looking-glass.io/docs/B7/requirements/)
- [VirtualDrivers/Virtual-Display-Driver](https://github.com/VirtualDrivers/Virtual-Display-Driver)
- [roshkins/IddSampleDriver](https://github.com/roshkins/IddSampleDriver) — the
  older self-signed original, same mechanism
- [Optimus laptop dGPU passthrough guide (Misairu-G)](https://gist.github.com/Misairu-G/616f7b2756c488148b7309addc940b28)
  — the Quadro-only EDID-from-file note
