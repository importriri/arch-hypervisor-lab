# Setup FAQ

Start at [SETUP.md](SETUP.md); use [Troubleshooting](TROUBLESHOOTING.md) for a
symptom. Current source and software checks do not certify a complete install.

## Will it work on my laptop?

The component profiles are Acer Nitro 5 / RTX 3060 Mobile and Predator Helios
300 / RTX 3070 Mobile; **both full pipelines remain pending**. KVM, 64-bit UEFI,
IOMMU/groups and a host display route independent of the passed GPU matter more
than the marketing name. An unknown profile stops preflight. Explicit
`no-gpu-passthrough` supports a foundation without VFIO; it is no promise of an
accelerated desktop or physical single-GPU compatibility. See the
[hardware table](SETUP.md#hardware-storage-and-choices).

## Where is the installer ISO?

There is no project ISO to download or boot. Its intended priority is recorded
in a [Proposed design](https://github.com/importriri/arch-bootstrap/blob/main/docs/adr/0001-iso-build-and-distribution.md);
implementation/build, admitted payload, signing/distribution and physical boot
are pending. Today use an authenticated **upstream Arch Linux** medium, clone
`arch-bootstrap` and run `bootstrap`, then stage 2. No monthly medium or exact
automation pair is frozen by this guide. `lab.yml` currently supplies Sway and
Looking Glass, not the complete preferred Hyprland/Create v1 target.

## Will this erase my disk, and can I undo it?

A real bootstrap run erases every confirmed whole target disk, including its
ESP and other systems; the optional VM disk is erased too. It has no rollback.
Dry run is the default and asks for matching LUKS passphrases without using them.
An existing GPT can make rehearsal fail; do not wipe it for a green dry run.
Verify an external backup and recovery medium first. Lost LUKS keys/passphrase
or a lost dedicated-disk keyfile cannot be repaired by rerunning bootstrap.
Snapshots on an erased disk are no recovery. Follow
[the installation stops](SETUP.md#1c-rehearse-then-install-only-the-reviewed-layout)
and [boot/storage diagnosis](TROUBLESHOOTING.md#boot-or-storage-handoff).

## Why are Machines empty, or a ready Template unusable here?

A Template is policy pinned to one sealed Golden Image; it is not a bundled
download. Your store must contain that exact validated base before a Machine
can be materialized. The captured `arch-dev-20261003` workstation is local,
not a public image URL. Debian's server Template remains draft until the
agent-capable `debian-server` is built/sealed; Fedora's ready status is not
its pending SSH observation. See [images and prerequisites](SETUP.md#4-prepare-and-seal-images).

## Do I need Windows or manual installation media?

No, they are optional workshops. Windows needs legitimately obtained private
media, driver/display preparation and reviewed local receipts; manual-install
Linux distributions need their own ISO-to-qcow2 workshop. They never enter Git.
Do not clone personal Windows identity into a dirty image. Final managed VMs
use the explicit lifecycle, not virt-manager as a second owner. See
[the workshop links](SETUP.md#4-prepare-and-seal-images).

## Can several Machines or services share the GPU?

Only one running VM owns it at a time; several shut-off definitions may name it.
Services can use it only through reviewed policy and a matching Template/spec.
The clean → dev → dirty → lab ladder only lowers within a host boot. Returning
to a cleaner use needs a host reboot; a GPU reset is no sanitization proof.
The optional per-run lease is Proposed and unimplemented, so do not assume an
existing workstation can freely switch device shape. Never clear the live trust
record. See [GPU boundaries](SETUP.md#6-use-the-dgpu-through-vfio).

## Are disposable Machines ready for untrusted browsing?

No qualified usable disposable path is claimed. Transient disk discard is
software-verified, but repeated-boot agent closure, new SSH pins and real
stop/start/crash observations remain open. Discarding a disk proves nothing
about GPU state or network isolation. Do not bypass an agent/pin failure with
manual key acceptance or disabled checking. See
[the lifecycle stop](SETUP.md#5-exercise-explicit-vm-lifecycle).

## What security does this provide?

Host-controlled trust networks, explicit lifecycle/provenance and a GPU-use
ladder provide compartmentalization on KVM. **HyperLab does not provide Qubes OS
security properties.** The host session/kernel, KVM and QEMU are trusted;
input isolation, process confinement and other physical/security gates remain
open. Separate signed loader/kernel assets leave initramfs and command line
outside that authentication. A convincing guest window, green CI or one
successful component is no full-pipeline/security guarantee. Read the
[stage-2 threat model](https://github.com/importriri/hyperlab-ansible/blob/main/docs/threat-model.md)
and this repository's [evidence threat model](EVIDENCE-THREAT-MODEL.md).
Use [SECURITY.md](SECURITY.md) for vulnerabilities or published private data;
a policy file does not activate a private-reporting service. Rights/provenance
review and service activation remain release dependencies.
