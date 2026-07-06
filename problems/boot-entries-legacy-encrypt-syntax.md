# Bug: boot entries written for a hook stack this machine doesn't run

Caught in review before it cost a reboot. All four systemd-boot profiles in
`configs/boot/` carried `cryptdevice=PARTUUID=...:root` — the kernel cmdline
syntax of mkinitcpio's **legacy `encrypt` hook**. This machine's declared
stack is `systemd` + `sd-encrypt`, which ignores `cryptdevice=` completely.

## Symptom (the one a reboot would have produced)

initramfs comes up, never unlocks the root, drops to the emergency shell.
No typo to find: every parameter is spelled perfectly — for the wrong hook.

## Root cause

Two hook families, two dialects, zero overlap:

| Hook stack | Unlock parameter |
|---|---|
| `udev` + `encrypt` (legacy) | `cryptdevice=PARTUUID=<gpt-partuuid>:root` |
| `systemd` + `sd-encrypt` (this machine) | `rd.luks.name=<luks-uuid>=root` |

Double trap: even the *identifier* changes. `sd-encrypt` wants the **LUKS
container UUID** (`cryptsetup luksUUID /dev/nvme0n1pX`), not the GPT
PARTUUID that `blkid` shows first. Right syntax + wrong UUID fails exactly
the same way.

The fix had already landed in the `problems/gpu-freeze-power-management.md`
writeup — but only there. The four real `.conf` files never got the same
treatment. A fix that lives in the documentation and not in the configs is
a fix that hasn't happened.

## Solution

- All four profiles migrated to `rd.luks.name=YOUR-LUKS-UUID-HERE=root`,
  with the hint comment corrected: the UUID comes from `cryptsetup luksUUID`,
  **not** from the PARTUUID.
- While in there: `rd.driver.blacklist=` → `modprobe.blacklist=`. The former
  is dracut-only — on mkinitcpio it parses as noise and blocks nothing.

## Verification

```bash
grep -rn "cryptdevice" configs/boot/        # must return nothing
grep -rln "rd.luks.name" configs/boot/*.conf | wc -l    # must be 4
```

Roll out one entry at a time and keep a known-good entry in the loader menu
until the new one has actually booted: with a wrong `rd.luks.name` the
machine stops in initramfs, and the old entry is the way back.

## The lesson

A config that has never been booted is a claim, not a fact. And when a bug
gets fixed in a writeup, `grep` the whole repo for its siblings before
declaring victory.
