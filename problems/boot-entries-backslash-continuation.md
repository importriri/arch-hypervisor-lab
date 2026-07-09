# Bug: multi-line `options` with backslash — a continuation that does not exist

Caught in review, again before it cost a reboot — and this one would have
*passed* the reboot. All four profiles in `configs/boot/` had their kernel
parameters split over several lines with a trailing `\`, shell-style:

```
options rd.luks.name=...=cryptroot root=/dev/mapper/cryptroot \
        zswap.enabled=0 rw rootfstype=btrfs \
        intel_iommu=on iommu=pt \
        vfio-pci.ids=10de:249d,10de:228b \
        ...
```

The Boot Loader Specification has **no line continuation**. Entries are
strict `key value` lines: the first word of a line is the key, and a line
whose first word is not a known key is simply ignored.

## Symptom (the one that makes this bug dangerous)

**The machine boots fine.** `rd.luks.name` and `root=` sit on the first
line, so the root unlocks and the system comes up looking healthy. What the
kernel actually received is the first line only — plus a literal `\` as a
garbage parameter. Everything on the continuation lines silently vanished:

- Vfio profile: no `intel_iommu=on`, no `vfio-pci.ids=…` → **nouveau grabs
  the GPU and passthrough is dead**, with nothing pointing at the boot entry
- Hardened profile: no `lockdown=confidentiality`, no `lsm=` stack — the
  "hardened" boot is silently un-hardened
- every profile: whatever came after the first `\` never existed

A config error that *prevents* boot gets found in five minutes. One that
boots and drops half the parameters can survive for months.

## Root cause

A shell habit imported into a format that is not shell. The spec is
explicit on both points:

| The format actually says | What the backslash version assumed |
|---|---|
| lines are `key value`, newline-separated | `\` joins physical lines |
| unknown first words → line ignored | indented params still get read |
| `options` may appear **more than once**; all occurrences are combined in order | one giant options line is the only way |

So the fix was already sitting inside the spec: the readability that the
backslashes were faking is provided, legitimately, by multiple `options`
lines.

## Solution

One `options` line per logical group, no continuations:

```
options rd.luks.name=YOUR-LUKS-UUID-HERE=cryptroot root=/dev/mapper/cryptroot rw rootfstype=btrfs rootflags=subvol=@ zswap.enabled=0
options intel_iommu=on iommu=pt
options vfio-pci.ids=10de:249d,10de:228b
options modprobe.blacklist=nouveau module_blacklist=nouveau nvidia-drm.modeset=0
options video=efifb:off pcie_port_pm=off pcie_aspm=off kvm.ignore_msrs=1
```

While in there, `grep` found the siblings (the lesson from the last
writeup, applied): `modprobe.blacklist=nouveau` was **duplicated** in the
Vfio and Nvidia profiles — a leftover of the `rd.driver.blacklist=` →
`modprobe.blacklist=` conversion landing next to an already-existing line.
Duplicates removed; the intentional pair `modprobe.blacklist=nouveau` +
`module_blacklist=nouveau` in the Vfio profile stays, because those are two
*different* mechanisms (modprobe/udev level vs. the kernel itself) and the
comment now says so.

## Verification

On the repo, before any deploy:

```bash
grep -n '\\$' configs/boot/*.conf          # must return nothing
grep -c '^options' configs/boot/*.conf     # ≥ 2 per file: the groups survived
grep -rn "cryptdevice" configs/boot/       # still nothing (previous bug stays dead)
```

On the machine, after copying an entry into `/boot/loader/entries/`:

```bash
bootctl list          # the entry must show ALL parameters, merged in order
# then reboot into it and:
cat /proc/cmdline     # every group present, no stray '\' anywhere
```

Same rollout rule as always: one entry at a time, keep a known-good entry
in the menu until the new one has actually booted **and** `/proc/cmdline`
has been read.

## The lesson

The most dangerous config error is the one that still boots. A parameter
list is only real once it has been read back from `/proc/cmdline` — and a
format's rules come from that format's spec, not from the habits of the
language you edit it in.
