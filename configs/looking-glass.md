# Looking Glass — the window onto the GPU VM

> Design contract. What is automated, what is manual, and why the line falls
> where it does. Verified on the bench machine; the numbers below are real.

The passthrough VM owns the dGPU. The host has no cable to it — on this laptop
the only port wired to the dGPU is a broken HDMI. Looking Glass closes that gap:
the guest writes finished frames into a block of shared memory, the host reads
them out of the same block and draws them in a window. No encode, no network,
no compression — the frame you see is the frame the guest rendered.

That last point matters when judging quality: **Looking Glass carries raw
frames, SPICE compresses**. At equal resolution Looking Glass cannot look worse
than SPICE. If it does, you are not looking at Looking Glass — see
[`problems/looking-glass-shows-spice-and-calls-it-success.md`](../problems/looking-glass-shows-spice-and-calls-it-success.md).

---

## The path a frame takes

```
   GUEST (Windows, owns the dGPU)                HOST (Arch, blind)
 ┌────────────────────────────────┐          ┌──────────────────────────┐
 │  dGPU renders the desktop      │          │                          │
 │            ↓                   │          │                          │
 │  virtual display (IDD)  ← the  │          │                          │
 │            ↓            missing│          │                          │
 │  looking-glass-host.exe  cable │          │  looking-glass-client    │
 │  captures it via D3D12         │          │            ↑             │
 └────────────┬───────────────────┘          └────────────┼─────────────┘
              │                                           │
              └──────────► /dev/kvmfr0 (ivshmem) ─────────┘
                           one buffer, two sides

   keyboard + mouse travel the other way, over SPICE — never over kvmfr
```

Three things must be true at once, and each one fails differently:

1. **The shared memory exists and both ends can open it.** QEMU opens the node
   as a memory backend; the client mmaps it from the desktop session. Two
   different users, one node —
   [`problems/kvmfr-device-permissions.md`](../problems/kvmfr-device-permissions.md).
2. **The guest has something to capture.** A GPU with no display attached has no
   output, and the host application exits in under a tenth of a second —
   [`problems/geforce-passthrough-needs-a-display.md`](../problems/geforce-passthrough-needs-a-display.md).
3. **Client and host application are the same build.** They do not negotiate.
   Mismatched builds leave the client waiting forever, which looks exactly like
   a permissions problem and is not one.

---

## Where the automation line falls

| Piece | Where it lives | Status |
|---|---|---|
| kvmfr module (DKMS), sizing, boot loading | `privatestack-ansible` → `roles/looking_glass` | automated |
| device node permissions (udev) | same role | automated |
| client built from a pinned commit | same role | automated |
| client configuration | same role | automated |
| ivshmem + SPICE + input devices in the VM XML | [`libvirt/looking-glass.xml`](libvirt/looking-glass.xml) | documented; lands in the `guest` brick |
| virtio drivers, host application, virtual display **inside Windows** | [`virtual-display-windows.md`](virtual-display-windows.md) | manual, by design |

The line is not laziness. Everything on the host side is a package, a file, or a
build from a pinned commit — all of it declarative and testable, so all of it is
a brick. Everything inside the Windows guest is a signed binary installed by a
GUI. Automating that would mean driving an installer over WinRM: more moving
parts than the manual procedure it replaces, and unverifiable in CI.

So the guest half is done **once**, by hand, on the image that every later VM is
cloned from. Reproducibility is preserved where it can be checked, and the
manual part is written down instead of remembered — which is what
[`virtual-display-windows.md`](virtual-display-windows.md) is for.

---

## Host side

With the ansible brick:

```bash
ansible-playbook playbooks/desktop.yml      # the Wayland session the client needs
ansible-playbook playbooks/looking-glass.yml
```

By hand, the same four things in order:

**1. The kvmfr module.** Built out of the Looking Glass source tree with DKMS,
against the headers of the running kernel (`linux-hardened-headers` here — not
`linux-headers`, that is a different kernel).

**2. Its size.** The shared block must hold two frames plus headroom:

```
width × height × 4 bytes × 2 + 10 MiB, rounded up to a power of two
1920 × 1080  →  25.8 MiB  →  32
```

```ini
# /etc/modprobe.d/kvmfr.conf
options kvmfr static_size_mb=32
```

```
# /etc/modules-load.d/kvmfr.conf
kvmfr
```

**The same number goes in the guest XML.** They are one buffer seen from two
sides; if they disagree the smaller wins and the picture loses its bottom edge.

**3. Its permissions.** Both openers, in one rule:

```
# /etc/udev/rules.d/70-kvmfr.rules
SUBSYSTEM=="kvmfr", OWNER="libvirt-qemu", GROUP="kvm", MODE="0660", TAG+="uaccess"
```

```bash
udevadm control --reload
udevadm trigger --subsystem-match=kvmfr --action=change   # not optional — see the writeup
```

**4. The client**, built from the same commit as the Windows host application:

```bash
git clone --recursive https://github.com/gnif/LookingGlass.git
cd LookingGlass && git checkout 0140a3f6
mkdir -p client/build && cd client/build
cmake -DENABLE_X11=no -DENABLE_WAYLAND=yes -DENABLE_LIBDECOR=yes ../
make -j"$(nproc)" && sudo make install
```

`ENABLE_X11=no` keeps the whole path Wayland-only, same contract as the rest of
the cockpit. `libdecor` draws the window decorations sway does not draw for it.

---

## Fixed SPICE input endpoint

The managed client uses `127.0.0.1:5900`. The libvirt domain therefore uses:

```xml
<graphics type='spice' port='5900' autoport='no' listen='127.0.0.1'/>
```

Check it with `virsh domdisplay <guest>`. A client pinned to 5900 and a domain
using `autoport='yes'` are not the same configuration, even when video happens
to arrive through kvmfr.

The pinned B7 client also expects INI comments to begin with `;`, not `#`. See
[`../problems/looking-glass-client-ini-comments.md`](../problems/looking-glass-client-ini-comments.md).


## Verification protocol

Three lines decide whether this works. Nothing else counts — not what the
window shows, not whether the mouse moves.

**In the guest**, `%ProgramData%\Looking Glass (host)\looking-glass-host.txt`:

```
Device Description: NVIDIA GeForce RTX 3060 Laptop GPU     ← capturing the right card
==== [ Capture Start ] ====                                 ← it found a display
Max Frame Size   : 14 MiB                                   ← fits inside the 32
```

`Failed to locate a valid output device` here means the guest has no display on
the passed GPU. Nothing downstream can fix that.

**On the host**, in the client log:

```
The host application seems to not be running     ← MUST be absent
main_frameThread | Format: FRAME_TYPE_BGRA       ← real frames
Using DMA buffer support                         ← going through kvmfr, not a copy
```

While that first line is present, whatever the window shows is the SPICE
fallback surface, and every conclusion drawn from it is wrong.

**Proof the GPU is actually rendering** — not the software rasteriser — is a
3D benchmark inside the VM. On the bench: Unigine Valley, Extreme HD preset,
8×AA, 1920×1080, **46.8 FPS average** (min 18.7, max 65.5), GPU at 2100 MHz.
The software adapter scores single digits; there is no ambiguity in that number.

---

## Known limits

**One GPU VM at a time, and it must fit in RAM.** A PCI hostdev forces the IOMMU
to pin the guest's entire memory: no lazy allocation, no swap, ballooning
ineffective. On an 8 GB bench machine a 7 GB guest is killed by the OOM killer
before it finishes booting, and the failure is silent — QEMU dies with no error
of its own. 6000 MiB is the working ceiling here.

**The virtual display costs a little smoothness.** Reports from r/VFIO put a
software IDD slightly behind a hardware dummy plug on frame drops. It is not
visible at desktop and CAD workloads; it may be under a twitch shooter. Where a
port wired to the dGPU exists and works, a dummy plug is still the better
transport — this machine does not have that option.

**Heat is the real ceiling.** 86 °C at load on the bench, which is where the
card starts throttling and where that 18.7 minimum comes from. The lever for
smoothness is thermal and CPU pinning, not the display path.

**NVIDIA Control Panel will say no display is attached.** That is true and
harmless: the virtual monitor lives on the IDD adapter, not on a physical
output. Only the display section of the panel is affected; 3D settings are not.

---

## Portability note

Everything above is card-agnostic except one thing: whether your laptop wires a
usable port to the dGPU. If it does, a dummy plug replaces the whole virtual
display procedure and the guest half shrinks to installing the host
application. If it does not — broken port, or a muxless design that never
exposes one — the virtual display is not a workaround, it is the only path.

Check before assuming: on the bench, NVIDIA's own panel reports zero displays on
the card, and that is the honest state of the hardware.
