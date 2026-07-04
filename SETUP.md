# Setup — how to reproduce this lab

This lab is meant to be **reproducible by anyone**, not just on my machine.
The point is not to lock the hardware down — it is to make dangerous work
(malware, offensive/defensive testing against PLCs) safe to run on your own
gear, with the consequences contained and documented. Security here means
freedom made safe, not freedom removed.

The build is a pipeline of three stages. Each stage is reproducible on its own
and hands a known-good state to the next.

```
  arch-bootstrap            Ansible roles              this repo
  (bash installer)   ─────▶ (configuration)   ─────▶  (configs + writeups)
  base OS, encrypted        network, VMs, VFIO,        boot profiles, the
  disk, hardened kernel     GPU hooks, hardening       four-domain lab
        🚧                        📋                         ✅ (grows)
```

---

## Stage 1 — Base install → [arch-bootstrap](https://github.com/importriri/arch-bootstrap)

A bash installer, written and tested from scratch, that produces the base the
whole lab stands on: LUKS2-encrypted disk, Btrfs subvolumes, systemd-boot,
Secure Boot with custom keys, `linux-hardened`, zram.

- Status: **in progress.** Partitioning is done and covered by a test suite;
  encryption is next. Live roadmap in that repo README.
- When done, this stage is a single script run from the Arch ISO.

Until stage 1 is complete, follow the Arch Wiki for the install and use this
repo boot profiles as your systemd-boot entries (see below).

---

## Stage 2 — Configuration → Ansible roles

Everything above the base OS, as reusable Ansible roles: the four network
domains (nftables), the libvirt VMs, VFIO/GPU passthrough, the GPU handoff
hooks, host hardening, the malware lab.

- Status: **planned.** This becomes its own repo; this line turns into a link
  when it lands.
- Goal: rebuild the entire configured host with one command, so the lab is not
  a week of manual setup but an afternoon.

---

## Stage 3 — The lab → this repo

The configs and writeups that make the four-domain lab real. They land here as
each piece goes live and is verified on real hardware.

### Boot profiles (`configs/boot/`)

systemd-boot entries, one per intended use. **Vfio and Hardened are the base of
the lab; Integrated and Nvidia are optional conveniences.**

| Profile | Kernel | GPU | Use |
|---|---|---|---|
| **Hardened** | linux-hardened | none special | secure default, malware analysis, security testing |
| **Vfio** | linux-hardened | dGPU → VFIO | run a VM with GPU passthrough (main lab profile) |
| Integrated | linux-hardened | iGPU only | light work, battery saving |
| Nvidia | linux-hardened | dGPU on host | native Linux gaming / rendering |

All four are placeholders until you set your own `PARTUUID` and confirm your
GPU PCI IDs (`lspci -nn | grep -i nvidia`). See each `.conf` for the details.

### Network domains (`configs/network-domains.md`)

The four isolated segments and the nftables design that keeps them apart,
including the GPU handoff rule (the card never moves from a low-trust domain to
a high-trust one without a full shutdown through the host).

### The rest

`configs/libvirt/`, `configs/hooks/`, `configs/malware-lab/` fill in as stage 2
produces and verifies them.

---

## Why this matters for what comes next

Future work — offensive and defensive security, especially against PLCs — needs
somewhere legal and isolated to run. This lab is that place: the air-gapped
Malware Lab domain is where payloads get analysed against simulated industrial
targets without touching anything real, on hardware I own, asking no one for
permission.

That is why reproducibility is the whole point. The faster someone can stand
this lab up, the sooner they can get to the actual experiments. Future repos
will list this lab as a prerequisite — and thanks to stages 1 and 2, meeting
that prerequisite should take an afternoon, not days.
