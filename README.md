# Arch Linux Hypervisor Lab

Architecture, hardware evidence and failure writeups for a laptop KVM/VFIO lab
on Arch Linux.

The project is split so installation, configuration and evidence do not certify
one another:

```text
arch-bootstrap  ->  hyperlab-ansible  ->  arch-hypervisor-lab
base system         host + workloads      evidence + writeups
```

Start with [`SETUP.md`](SETUP.md), the canonical newcomer guide from an
authenticated upstream Arch Linux live prompt through installation, the first
account and the existing host target. Use [Troubleshooting](TROUBLESHOOTING.md)
for symptoms and [FAQ](FAQ.md) for hardware, media, erasure and security limits.
The complete v1 installation remains blocked on software and hardware gates;
the guide marks the stops. A project ISO is intended but not built or available.

## Lab shape

```text
Arch Linux host
|
|-- clean     10.10.1.0/24  NAT       trusted accounts and games
|-- dirty     10.10.2.0/24  NAT       untrusted software and mods
|-- dev       10.10.3.0/24  NAT       development and 3D work
|-- lab       10.10.4.0/24  ISOLATED  controlled research
`-- services  10.10.5.0/24  NAT       private service VMs

NVIDIA dGPU -- VFIO --> one workload VM at a time
```

The existing `lab.yml` target uses the iGPU for Sway and Looking Glass; the dGPU
belongs to one running VFIO workload at a time. Hyprland is preferred in the
product contract and Sway remains the recovery compositor, but `lab.yml` does
not assemble the complete v1 Hyprland/session/Create path. Services may use the
GPU through an explicitly reviewed handoff profile and matching Template/spec.
The clean → dev → dirty → lab GPU ladder only lowers within a host boot;
returning to a cleaner use requires a host reboot. The optional per-run GPU
lease is still Proposed and unimplemented. See the
[setup boundaries](SETUP.md#2c-reconcile-the-existing-laptop-target-stop-before-claiming-v1).

## Repository set

1. [`arch-bootstrap`](https://github.com/importriri/arch-bootstrap) installs the
   encrypted Arch base and writes the storage hand-off contract.
2. [`hyperlab-ansible`](https://github.com/importriri/hyperlab-ansible) configures
   KVM, VFIO, networking, isolation, the Sway cockpit and Looking Glass, then
   owns explicit image/VM/service transactions.
3. This repository records what the architecture is and what has actually been
   proven on hardware.

A green CI run is not a compatibility claim. Hardware status changes only after
the named machine runs the matching frozen commits and evidence gate.

## Hardware status

The Nitro
bootstrap-to-stage-2 host path has been reproduced on the Acer Nitro 5 with an
RTX 3060 Mobile. Within that path,
the normal laptop target adds Sway and the Looking Glass host transport in that
order. Host VFIO and the accelerated Linux video path have real evidence. Final
Linux guest session persistence and Looking Glass input checks are still open.

Both full-pipeline statuses are `pipeline-pending`; historical host/component
results do not qualify the complete current v1 path. An explicit
`no-gpu-passthrough` profile supplies a foundation without VFIO, with no
accelerated desktop or physical single-GPU compatibility claim.

The Acer Predator Helios 300 with RTX 3070 Mobile has a reviewed profile and
individual component history, but the complete pipeline remains pending until it
replays the same frozen repository commits used for the Nitro release.

See [`hardware/README.md`](hardware/README.md) and
[`hardware/compatibility.yml`](hardware/compatibility.yml).

## Why the problem notes matter

The useful parts of a hardware lab are usually the assumptions that turned out
to be wrong. `problems/` keeps those failures with their symptom, cause, fix and
verification so a future refactor does not have to rediscover them.

Notable examples include PCIe power-management freezes, kvmfr permissions,
Looking Glass display requirements and configuration parsing failures.

## Repository map

- `configs/`: boot, network, libvirt and display contracts;
- `hardware/`: compatibility policy, reports and evidence templates;
- `problems/`: failure investigations;
- `scripts/`: sanitized hardware collection and repository checks;
- [`SETUP.md`](SETUP.md): live-medium-to-lab route, prerequisites and current stops;
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md): symptoms, read-only diagnosis and exact problem-note sources;
- [`FAQ.md`](FAQ.md): short answers about hardware, ISO, recovery, workloads and security;
- [`PROVENANCE-AUDIT.md`](PROVENANCE-AUDIT.md): file origins, candidate
  third-party notices and what is still unresolved;
- [`SECURITY.md`](SECURITY.md): private reporting of vulnerabilities and of
  private data published here by mistake;
- [`EVIDENCE-THREAT-MODEL.md`](EVIDENCE-THREAT-MODEL.md): what the evidence
  here can and cannot establish, and the manual review before publication;
- [`CONTRIBUTING.md`](CONTRIBUTING.md): the checks, write-ups and evidence
  contributions.

Run the repository checks before publishing evidence:

```bash
python scripts/verify_repo.py
bash -n scripts/collect-hardware-report.sh
```

They check consistency only. They are not a privacy review and do not
show that a result happened; see
[`EVIDENCE-THREAT-MODEL.md`](EVIDENCE-THREAT-MODEL.md).

## Scope

The isolated network is for controlled work on systems you own or are authorized
to examine. It has no uplink by default and the host blocks forwarding between
trust domains unless an exposure is explicitly declared.

## Author

[importriri](https://github.com/importriri) is the author and maintainer.
