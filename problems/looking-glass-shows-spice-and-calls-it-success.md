# Bug: Looking Glass shows a working desktop while the host application is not running

## Symptom

The client starts, connects, and draws the Windows desktop. It looks like it
works. Three things are subtly off:

- the picture is **softer than SPICE**, not sharper;
- in fullscreen the keyboard reaches the guest, **the mouse does not**;
- the resolution changes on its own, following the guest's display settings.

Every one of those was investigated as its own problem. All three were the same
problem, and none of them was the one being debugged.

## Setup

- Host: Arch Linux, sway, Looking Glass client `B7-263-0140a3f6` built from source
- Guest: Windows 11, RTX 3060 Mobile passed through, host application same build
- Transport: `/dev/kvmfr0`, 32 MiB, input over SPICE

## Root cause

The client has a documented fallback: while no host application is publishing
frames, it renders the SPICE display so the window is not blank. That is a
feature. It is also indistinguishable from success if you judge by the picture.

The host application inside the guest was exiting a fraction of a second after
starting (its own bug —
[`geforce-passthrough-needs-a-display.md`](geforce-passthrough-needs-a-display.md)),
so **not one Looking Glass frame was ever transported**. What was on screen was
SPICE the entire time.

That explains all three symptoms at once:

- **Softer than SPICE** because it *was* SPICE, upscaled from 1280×800 onto a
  1080p panel. The comparison that was supposed to prove Looking Glass was worse
  was Looking Glass versus itself.
- **Dead mouse** because the tablet device had been removed, as the Looking
  Glass docs prescribe. In the fallback the client sends absolute pointer
  positions; with no absolute pointer in the guest they land nowhere. The
  keyboard kept working because it rides the emulated PS/2 controller Q35
  provides regardless. *That asymmetry — keyboard yes, mouse no — is the
  fingerprint of input reaching the guest through a path the picture is not
  using.*
- **Resolution changing** because the SPICE surface follows the guest's display
  settings, which is exactly what a Looking Glass surface does not do.

## Why it is hard to diagnose

The failure produces a working-looking system. Nothing errors. The window fills,
the desktop is live, and the guest responds to the keyboard — so the natural
next move is to tune what looks wrong (quality, then input) instead of asking
whether the transport is running at all.

Worse: the true state is printed in the log at every single start, in plain
English, and it scrolls past in the first half second among fifty informational
lines. It is not hidden. It is just not an error, so it does not look like one.

## Time spent

About two days, most of it spent optimising a path that was never carrying data.

## The tell

```
main.c:1529 | lg_run | The host application seems to not be running
main.c:1530 | lg_run | Waiting for the host application to start...
main.c:951  | spice_surfaceCreate | Create SPICE surface: id: 0, size: 1280x800
```

`spice_surfaceCreate` in the client log means the picture is coming from SPICE.
Full stop.

## Solution

There is no patch — the fallback is correct behaviour. The fix is a rule:

> **The definition of "Looking Glass works" is the absence of
> `The host application seems to not be running` in the client log.**
> Not the window. Not the mouse. The log line.

When it is genuinely working, the log says so just as plainly:

```
main.c:555  | main_frameThread | Using DMA buffer support
main.c:731  | main_frameThread | Format: FRAME_TYPE_BGRA 1920x1080 (1920x1080) stride:1920 ...
```

`FRAME_TYPE_BGRA` is a real frame out of shared memory. `Using DMA buffer
support` means it came through kvmfr rather than a copy.

## Verification

```bash
looking-glass-client 2>&1 | grep -E "host application|spice_surfaceCreate|frameThread"
```

Nothing from the first two, lines from the third: working. Anything from the
first two: you are looking at SPICE, and every measurement taken from that
window is void.

## Related trap in the same family

`looking-glass-client --help` prints each option's **effective value after
`client.ini` has been parsed** — not the compiled-in default. It is the fastest
way to find out that an edit never took:

```
| input:escapeKey     | -m | 110 = KEY_INSERT | ...
| input:captureOnFocus |   | no               | ...
```

If a setting you just wrote still shows its old value there, the file was not
read, and no amount of testing the behaviour will tell you why.

(Also: the escape key list is `-m help`. Bare `-m` is parsed as a flag missing
its value and silently ignored.)

## Lesson

A fallback that renders something plausible is a debugging hazard even when it
is the right design. The guard is to define success as a log assertion before
starting, not as an impression of the screen afterwards.
