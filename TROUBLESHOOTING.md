# Troubleshooting by symptom

Return to [the setup guide](SETUP.md) or [FAQ](FAQ.md). Diagnose before changing
state. Commands here are read-only observations in the named context; keep their
output private. A diagnosis is not a successful installation. Stop on an
unexpected result, failed prerequisite or ambiguous ownership. Historical fixes
below are source history; open integration/hardware gates remain open.

## Live networking

**Symptom:** clone/bootstrap cannot reach the internet, or no wireless device
is visible. **Context:** root on the authenticated live medium, before disk
selection (the same checks also apply at installed-root first login).

Run `ip link`, `rfkill`, `ip address`, `ip route`, `ping -c 1 archlinux.org`
and `timedatectl status`; inside `iwctl`, use `device list` and `station DEVICE
show` with the name actually listed. Expect a usable interface/radio, address,
route, DNS/ICMP reply and sane time. A listed radio is not a DHCP lease. Missing
device, blocked radio, absent route or a DNS/ICMP failure stops bootstrap.
Follow [step 1a](SETUP.md#1a-confirm-the-live-environment-and-connect) to connect
with a private password prompt, or use supported wired connectivity. Do not
assume `wlan0`, skip the connectivity guard or disable TLS/package verification.

**Source:** [official installation networking](https://wiki.archlinux.org/title/Installation_guide#Connect_to_the_internet)
and [iwctl manual](https://man.archlinux.org/man/iwctl.1.en); the repository's
network guard is in the [bootstrap engine](https://github.com/importriri/arch-bootstrap/blob/main/installer).
There is no local problem note about initial live Wi-Fi; these are the upstream
instructions rather than an invented historical fix.

## Dry run or busy target

**Symptom:** rehearsal asks for a LUKS secret, says `sgdisk (pretend) failed`,
or refuses `/mnt`/an existing mapper. **Context:** live root, bootstrap checkout;
no new installation attempt while state is uncertain.

Inspect `lsblk`, `findmnt -rno TARGET` and the prior run's output. Two matching
LUKS prompts in dry run are deliberate; the secret is unused. On a disk with
GPT, pretend mode can show the old table and return nonzero because it cannot
simulate `--zap-all`. Expect **failure**, not a rehearsal pass. Rehearse on
blank disposable storage instead of erasing valuable data for a green check.
A mounted `/mnt` subtree or existing `cryptroot`/`cryptvm` must trigger refusal,
even in dry run. If mount enumeration itself fails, it must also refuse.

Stop, establish which run/person owns every mount and mapper, and preserve the
log. Cleanup of this run's work is distinct from destroying an earlier run's or
someone else's state. Do not paste suggested unmount/close commands until their
ownership and recovery impact are reviewed. A dry run should unmount/close
nothing. Any cleanup failure is visible and needs review before rerunning.

**Source and status:** [dry-run prompts, GPT limit and cleanup history](https://github.com/importriri/arch-bootstrap/blob/main/problems/dry-run-asks-for-luks-passphrase.md).
Prompt documentation and owned cleanup were corrected; the existing-GPT
rehearsal limitation remains.

## Boot or storage handoff

**Symptom:** no root unlock, emergency shell, wrong VM mount, or stage 2 refuses
its storage contract. **Context:** installed-root console, or the live recovery
medium only after the intended installed root is positively identified/mounted.
Do not run bootstrap again on the installed disks.

Read the relevant system's `etc/mkinitcpio.conf`, loader entry, `etc/fstab`,
`etc/crypttab` and `etc/privatestack/bootstrap-storage.yml` (prefix with `/mnt`
only when that is the verified installed root). The running host's
`cat /proc/cmdline` describes the entry actually booted. For this stack expect
`systemd` + `sd-encrypt`, an `options` value containing
`rd.luks.name=LUKS-UUID=cryptroot`, and the **LUKS container UUID**, not GPT
PARTUUID. The read-only `cryptsetup luksUUID /dev/disk/by-partlabel/ARCH_ROOT`
identifies it only after checking that label uniquely belongs to the intended
disk. Multiple `options` lines are valid and combine in order; shell-style
backslash continuations are invalid. Do not copy a placeholder UUID, unrelated
mapper name or trailing backslash into a boot entry.

On the installed host, inspect:

```bash
stat -c '%U:%G %a %n' /etc/privatestack/bootstrap-storage.yml
findmnt -J -T /var/lib/libvirt/images -o TARGET,SOURCE,FSTYPE,FSROOT,OPTIONS
lsattr -d /var/lib/libvirt/images
```

Expect a regular, non-symlink root-owned `0644` schema-1 contract and encrypted
Btrfs: `cryptroot` / FSROOT `/@vm` on one disk, or `cryptvm` / FSROOT `/` on two;
`C` should have been established while empty. A partial file is not a completed
handoff. If the bootstrap did not print its final wrapper success messages,
stop: stage 2 cannot repair the installation by guessing a contract. Do not
fabricate the YAML, layer a second mount over the first, change `+C` after images
exist or run the legacy-adoption procedure as an automatic fallback. Keep a
known-good boot entry and recovery medium; repair requires a reviewed plan.

**Sources and status:** [boot dialect fix](problems/boot-entries-legacy-encrypt-syntax.md),
[loader continuation fix](problems/boot-entries-backslash-continuation.md),
[storage writer failure semantics](https://github.com/importriri/arch-bootstrap/blob/main/docs/release-gates.md#a-failed-storage-hand-off).
Dialect/config defects were corrected; your actual boot and mounted handoff
still require observation.

**Related symptom:** `resolv.conf: Device or resource busy` during chroot.
With the installation still mounted and its owner known, inspect the previous
error and `findmnt -rno TARGET` from the live host. While a chroot is active,
expect its resolver file to appear as a mount target; after exit its temporary
bind mounts should be gone. Stop rather than deleting the busy resolver file. Current bootstrap
creates the resolver symlink outside the last chroot. The
[resolver problem note](https://github.com/importriri/arch-bootstrap/blob/main/problems/arch-chroot-bind-mounted-resolv-conf.md)
records the historical fix; do not replay its failed `rm` experiment.

## Unknown hardware profile

**Symptom:** preflight reports zero or multiple complete matches, missing PCI
functions or an invalid explicit profile. **Context:** installed-root/admin
console; no GPU workload started. Read `lspci -Dnnk` and preflight's refusal;
compare complete numeric GPU/audio identities with
[hardware/compatibility.yml](hardware/compatibility.yml). Expect exactly one
reviewed match for `auto`. A similar GPU name or copied PCI address is no match.

Stop for profile/IOMMU review. A deliberate foundation-only host may select
`no-gpu-passthrough` persistently in its local variables; it has no automatic
fallback and cannot run VFIO Machines. Never force Nitro IDs onto unknown
hardware. This is a refusal contract, not a broken detector to bypass.

**Sources:** [hardware profile procedure](https://github.com/importriri/hyperlab-ansible/blob/main/docs/hardware-profiles.md),
[no-passthrough decision](https://github.com/importriri/hyperlab-ansible/blob/main/docs/adr/0052-host-without-gpu-passthrough.md).

## Missing agent or server Template

**Symptom:** Debian Template absent/draft, guest-agent wait times out, or strict
SSH inventory cannot read the host key. **Context:** administrator on the host,
existing managed guest only. Inspect `hyperlabctl machine templates`, the
selected local manifest and the previous creation/inventory output. For an
already running guest whose identity is known, the read-only
`virsh -c qemu:///system qemu-agent-command NAME '{"execute":"guest-info"}'`
should return agent capabilities. No response is not SSH closure evidence.

Expect `server-debian` to remain draft while `debian-server` is not built.
The sealed upstream Debian base lacks the agent; a DHCP lease proves no agent
or trusted SSH identity. Stop before creation/provisioning. Follow the
[offline Workbench derivation](https://github.com/importriri/hyperlab-ansible/blob/main/docs/golden-image-workbench.md#deriving-offline-debian-server)
only with its sealed local base and full provenance/sealing prerequisites.
Do not weaken SSH checking, manually accept a network key, enable unrestricted
guest execution or install into an untrusted guest via an unpinned connection.

Fedora's ready Template is source status, not a recorded SSH pass. If the
inventory fails there, inspect guest-local agent/SELinux logs through the
reviewed recovery console as the guest administrator. Preserve the refusal;
agent host-key readability still needs its physical observation. A base whose
receipt predates corrected policy needs the exact rereceipt procedure, not a
hand-edited receipt.

**Sources and status:** [Debian agent claim corrected in source](https://github.com/importriri/hyperlab-ansible/blob/main/problems/sealed-image-claimed-guest-agent.md),
[Fedora key-read investigation, open](https://github.com/importriri/hyperlab-ansible/blob/main/problems/fedora-host-key-through-agent.md),
[first host-key pin fix](https://github.com/importriri/hyperlab-ansible/blob/main/problems/guest-host-key-unknown-after-first-boot.md).
The Debian replacement image and the two-server SSH campaign remain pending.

## Missing runtime inventory

**Symptom:** a guest runs but SSH/Looking Glass action cannot find its inventory
following login, reboot or cleanup. **Context:** normal administrator session on
the host. Read `id`, `printf '%s\n' "$XDG_RUNTIME_DIR"` and, for the selected
known guest, `stat -c '%F %U %a %n' "$XDG_RUNTIME_DIR/NAME.ini"`. Expect a private
real runtime directory and a regular operator-owned `0600` file; a missing file
is plausible because `/run` is ephemeral. An absent runtime directory requires a
new real login first; do not manufacture one or export another user's path.

Only a genuinely missing inventory is eligible for regeneration through the
authoritative `vm-guest-inventory.yml` playbook, with a running agent-capable
managed guest, selected spec and the same local identity overrides. The CLI’s
`hyperlabctl vm inventory` route delegates to that playbook, but does not
automatically load this guide’s local override file; use the explicit playbook
for the manual route with your chosen account.
That regeneration writes runtime state and pins, so it is a separate explicit
step after diagnosis. If it stops with `Runtime inventory requires the
operator-owned runtime directory, private SSH identity and strict known-hosts
database`, inspect `stat -c '%U %a %F %n'` on `$HOME/.ssh/hyperlab_ed25519` and
`$HOME/.ssh/known_hosts`. A genuinely absent `known_hosts` is prepared as in
[SETUP 5](SETUP.md#5-exercise-explicit-vm-lifecycle); any other state is a stop. An unsafe, linked, unreadable or wrong-owner file is a
refusal requiring investigation, not permission to delete it. Do not copy a
stale IP or disable strict host-key checking. Automatic repair is not accepted
merely because code exists.

**Source and status:** [runtime inventory self-heal](https://github.com/importriri/hyperlab-ansible/blob/main/problems/runtime-inventory-self-heal.md),
open integration/hardware gate.

## kvmfr permission denied

**Symptom:** QEMU cannot open `/dev/kvmfr0`, or the desktop client cannot map it.
**Context:** normal host administrator session; no permission edits. Observe
`ls -l /dev/kvmfr0` and `id`. Expect both intended openers: QEMU's managed owner
and the active user's access, normally `libvirt-qemu:kvm`, mode `0660` with a
logind `uaccess` ACL (`+` in the listing). A different QEMU identity policy must
be checked against that campaign's contract. The same `EACCES` can come from
node permissions, libvirt's device ACL or its namespace; mode alone does not
identify the culprit.

Stop and review the managed rule, retrigger handler and complete device ACL
against source. The historical fix covers both openers and retriggers an
already-existing node. Do not make the device world-writable, alternate its
owner between users, unload it from a live VM or replace the device ACL with a
one-entry list. Re-login if session access is stale; a reboot check belongs in
the planned campaign after clean shutdown.

**Source and status:** [kvmfr two-opener investigation](problems/kvmfr-device-permissions.md),
automated historical fix. Historical 32 MiB transport examples do not override the
[current transport contract](configs/looking-glass.md).

## Looking Glass shows a desktop

**Symptom:** plausible image, soft picture, host-application-not-running message,
keyboard but no mouse, or no producer frames. **Context:** host administrator
reviewing saved client logs, plus the prepared guest's producer log through its
safe console. Expect real shared-memory `FRAME_TYPE_BGRA` frames and kvmfr path;
`spice_surfaceCreate` and host-application-not-running identify fallback. The
absence of an error alone is insufficient: require moving real frames.

Stop counting video success. Check guest capture readiness/display before
changing transport. In Windows, `Failed to locate a valid output device` points
to the guest's capture display/driver. Use the reviewed workshop, not an
unverified installer or historical command that only copied driver files.
Keep recovery Console. Never count this picture as an input or audio pass.

**Sources and status:** [SPICE mistaken for success](problems/looking-glass-shows-spice-and-calls-it-success.md)
(no fallback bug to patch), [missing display investigation](problems/geforce-passthrough-needs-a-display.md)
and [current Windows display procedure](configs/virtual-display-windows.md).

## Pre-login input repeats or disappears

**Symptom:** Ly visible in Looking Glass but password input repeats, or the
console closes before the capture session is ready. **Context:** host operator,
prepared Linux experimental VFIO guest. Observe PRIMARY's window transition and
saved logs: it should use a temporary owned `virt-viewer` console at Ly, wait
for Hyprland plus the reviewed `HEADLESS-0` mode, then close only that console
and open real Looking Glass. A Hyprland PID alone is not display readiness.

Stop repeated password entry into the built-in fallback. Use the explicit
`hyperlabctl open console NAME` recovery action once the managed guest's identity
and prerequisites are confirmed. PRIMARY itself owns its temporary console;
do not kill unrelated viewer/sender processes. Video, pre-login handoff,
shortcut isolation, logout cleanup and physical audio have separate gates.

**Source and status:** [Linux pre-login PRIMARY handoff](https://github.com/importriri/hyperlab-ansible/blob/main/problems/looking-glass-linux-prelogin-primary-handoff.md).
The note records a successful later Nitro automatic handoff; it does not close
the remaining input-security/candidate qualification gates.

## Hard freeze at passthrough start

**Symptom:** earlier Predator/Nitro power-management failure resembles an
immediate whole-host hang. **Context:** recovery after a failure, no new start
attempt. Preserve available logs and read the booted `/proc/cmdline` against the
managed profile; expect its reviewed PCIe workaround to remain present.

Stop the campaign if policy differs. Do not remove the workaround, reproduce
the freeze to prove it exists, reset live GPU trust or apply copied kernel
parameters from a different laptop. Arrange a reviewed recovery/boot plan first.

**Source and status:** [PCIe power-management investigation](problems/gpu-freeze-power-management.md),
historical component fix; the full frozen Predator pipeline remains pending.
