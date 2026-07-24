# The guest half — virtual display and host application, by hand

> The part that stays manual. Done once, on the image every later VM is cloned
> from. Written down so it is repeated, not remembered.

Everything here happens inside the Windows guest, through `virt-manager` — not
through Looking Glass, which cannot work until this is finished. The procedure
is keyboard-only on purpose: the machine it was written on has no working
pointer of its own, and a procedure that needs a mouse is a procedure you cannot
run when the mouse is the thing that is broken.

Order matters. Each step is verifiable before the next one starts.

---

## 0. Before you begin

- The VM boots and Windows sees the passed GPU in Device Manager.
- The NVIDIA driver is installed **inside the guest** and the card is in use.
- The ivshmem device, the SPICE graphics and the virtio input devices are in
  the domain XML — see [`libvirt/looking-glass.xml`](libvirt/looking-glass.xml).
- You know which Looking Glass build the host side is on. Client and host
  application must match exactly; here that is `B7-263-0140a3f6`.

---

## 1. virtio input drivers

Mount the `virtio-win` ISO and install **vioinput**.

Skip this and the symptom is asymmetric and misleading: the keyboard keeps
working (it rides the emulated PS/2 controller Q35 provides anyway) while the
mouse is dead. That looks like a Looking Glass capture problem and is not one.

---

## 2. The IVSHMEM driver and the host application

Run `looking-glass-host-setup.exe` for **the same build as the client**, as
administrator.

The component list of this build offers exactly four things:

```
[x] IVSHMEM Driver          ← the shared memory device
[x] Looking Glass (host) Service
[ ] Desktop Shortcut
[ ] Start Menu Shortcut
```

There is no virtual display component. Looking Glass has its own indirect
display driver in development upstream, but it does not ship in this installer —
which is why step 3 exists at all.

Verify in Device Manager → System devices: **IVSHMEM Device**, no yellow
triangle. If instead you see a *Standard PCI RAM Controller*, the driver did not
bind and the rest cannot work.

---

## 3. The virtual display

The GPU has no monitor. Windows disables the output of a display adapter with
nothing attached, the host application finds nothing to capture, and it exits.
An indirect display driver creates a monitor in software and closes that gap.

Used here: **Virtual Display Driver** ([VirtualDrivers/Virtual-Display-Driver](https://github.com/VirtualDrivers/Virtual-Display-Driver),
"VDD by MTT"), signed, still maintained. The older
[roshkins/IddSampleDriver](https://github.com/roshkins/IddSampleDriver) works
the same way and is self-signed — fine if Secure Boot is off inside the VM,
which is a decision about the guest's own firmware, not the host's.

**Install it from the GUI installer on the Releases page.**

> `winget install --id=VirtualDrivers.Virtual-Display-Driver -e` reports success
> and creates no device. It drops files; it does not install the driver. A
> reboot after it changes nothing, and Device Manager shows no new adapter — the
> one symptom that tells you which of the two happened.

Then reboot the guest and verify in Device Manager → Display adapters. Three
entries, not two:

```
NVIDIA GeForce RTX 3060 Laptop GPU
Red Hat VirtIO GPU DOD controller     ← the emulated display, still there
Virtual Display Driver                ← the new one
```

*(An unrelated yellow triangle on "NVIDIA Platform Controllers and Framework",
code 31, is normal in a VM — it is a laptop platform driver with no hardware to
talk to. It has nothing to do with this.)*

---

## 4. Set the mode, then reduce to one display

Settings → System → Display → Advanced display. Select the virtual monitor and
set it to **1920×1080**.

This must match the shared memory sizing on the host. 32 MiB holds 1080p SDR and
nothing larger; a higher mode means resizing the buffer on both sides.

Then leave the emulated display alone **until the client shows real frames**. It
is the safety net: while it is on, `virt-manager` still shows you the desktop,
so a mistake is recoverable. Only once Looking Glass is confirmed working:

```
Win+P  →  Second screen only  →  Enter
```

`virt-manager` goes black at that point. That is correct — you now live inside
Looking Glass. `Win+P` gets you back if you picked the wrong screen.

---

## 5. Verify from the log, never from the picture

Restart the service (`Win+R` → `services.msc` → `L` until **Looking Glass
(host)** → `Shift+F10` → Restart) and read
`%ProgramData%\Looking Glass (host)\looking-glass-host.txt` from the bottom.

**Working:**

```
Device Description: NVIDIA GeForce RTX 3060 Laptop GPU
Trying           : D12
==== [ Capture Start ] ====
Using            : D12
Max Frame Size   : 14 MiB
```

**Not working — no display on the card:**

```
Not using unsupported adapter: Microsoft Basic Render Driver
Failed to locate a valid output device
Failed to find a supported capture interface
Host application exited
```

The second block means step 3 did not take. Nothing on the host side can
compensate for it.

---

## 6. Bake it, do not repeat it

This procedure is the reason the guest image is treated as a golden base: once
Windows is activated, driven and carrying these three drivers, it is frozen and
every later VM is a copy-on-write overlay on top of it. The Windows blob is not
reproducible from source, so it is reproduced from an image — and this page is
what makes that image rebuildable if it is ever lost.

---

## If it still refuses

| What you see | What it means |
|---|---|
| Host log: `Failed to locate a valid output device` | no display on the passed GPU — step 3 |
| Host log stops at IVSHMEM | the shared memory device is not bound — step 2 |
| Client log: `The host application seems to not be running` | the guest side never published a frame; read the guest log, not the host one |
| Client shows a desktop but the log says the host is not running | SPICE fallback — [the writeup](../problems/looking-glass-shows-spice-and-calls-it-success.md) |
| Keyboard works, mouse does not | vioinput missing — step 1 |
| Resolution flapping, capture restarting in a loop | two active displays fighting — finish step 4 |
