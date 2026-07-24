# Bug: /dev/kvmfr0 permission denied — first for QEMU, then for the client

## Symptom

Two failures that look unrelated and are the same one, seen from two sides.

The VM refuses to start:

```
internal error: QEMU unexpectedly closed the monitor (vm='win11'):
qemu-system-x86_64: can't open backing store /dev/kvmfr0 for guest RAM: Permission denied
```

Fix that, and the client refuses to start:

```
ivshmem.c:137 | ivshmemOpenDev | KVMFR Device : /dev/kvmfr0
ivshmem.c:144 | ivshmemOpenDev | Failed to open: /dev/kvmfr0
ivshmem.c:145 | ivshmemOpenDev | Permission denied
main.c:1286   | lg_run         | Failed to map memory
```

Fix *that* the obvious way and the first one comes back.

## Setup

- Arch Linux, libvirt with modular daemons, kvmfr built via DKMS
- QEMU runs as the system user `libvirt-qemu` (uid/gid 963, `nologin`)
- The client runs as the desktop user, in a sway session

## Root cause

Two facts collide.

**First: two different processes need the same device node.** QEMU opens it as
a memory backend when the guest starts. The client mmaps it from the desktop
session. They are not the same user and neither can be dropped.

The instinctive fix — `chown` the node to the QEMU user — makes the VM start
and locks the client out. The mirror fix locks QEMU out. Ownership alone cannot
express "these two, and nobody else".

**Second: udev does not revisit devices that already exist.** Rules are applied
to devices as they appear. Writing `/etc/udev/rules.d/70-kvmfr.rules` after the
module is already loaded changes nothing at all, and `udevadm control --reload`
does not help either: it reloads the rule set for *future* events. The node
keeps whatever ownership it was born with — `root:root 0600` — and every
verification of the rule file itself comes back correct.

## Why it is hard to diagnose

**`/dev/kvm` is mode 0666 on modern systemd.** So the VM having worked
perfectly for weeks proves nothing about the user's group membership, and
"other VMs start fine" is not evidence about permissions the way it feels like
it is. The kvmfr node is `0660 root:kvm` — a group that was never needed
before.

**The error is honest but ambiguous.** `EACCES` at `open()` can equally be
discretionary permissions on the node, libvirt's cgroup device controller
refusing the device, or libvirt's private `/dev` namespace not containing it.
Three different fixes, one message.

The discriminator is cheap and worth knowing:

```bash
sudo -u libvirt-qemu dd if=/dev/kvmfr0 of=/dev/null bs=1 count=1
```

The cgroup controller only applies inside the VM's cgroup, so this tests the
file permissions and nothing else. `Permission denied` → it is the node.
Any other error, including `Invalid argument` (kvmfr wants `mmap`, not `read`)
→ the open succeeded, and the problem is elsewhere.

## Solution

One rule that satisfies both openers:

```
# /etc/udev/rules.d/70-kvmfr.rules
SUBSYSTEM=="kvmfr", OWNER="libvirt-qemu", GROUP="kvm", MODE="0660", TAG+="uaccess"
```

`OWNER` covers QEMU. `TAG+="uaccess"` covers the human: systemd-logind puts an
ACL for the seat's active session on top, so the desktop user gets in without
the node being world-writable and without adding anyone to a group.

Then make it apply to the node that is already there:

```bash
udevadm control --reload
udevadm trigger --subsystem-match=kvmfr --action=change
```

The synthetic `change` event is the part that is easy to leave out and the part
that does the work. It also means no `modprobe -r`, and no stopping a running
VM to fix its permissions.

## Verification

```bash
ls -l /dev/kvmfr0
# crw-rw----+ 1 libvirt-qemu kvm 235, 0 ...
#          ↑ the plus is the uaccess ACL. Without it the client cannot open the node.
```

The real test is a reboot: check the node **before** starting anything. A
`chown` survives until the module reloads and lies to you in the meantime.

## For an immediate unblock

```bash
sudo setfacl -m u:$USER:rw /dev/kvmfr0
```

Permissions are checked at `open()`, so a process that already holds the file
descriptor is unaffected — this can be done with the VM running. It does not
survive a module reload, which is why it is a stopgap and not a fix.

## Two neighbouring traps

**Modular libvirt daemons.** If `cgroup_device_acl` in `/etc/libvirt/qemu.conf`
needs editing, the daemon to restart is the one that is actually running —
`virtqemud` on a modular Arch install. Restarting `libvirtd` there reloads
nothing. And that list *replaces* the default, it does not extend it: adding
only `/dev/kvmfr0` removes `/dev/kvm` from the guest and produces a much more
confusing failure than the one being fixed.

**Private `/dev` namespace.** If the error ever changes from
`Permission denied` to `No such file or directory` on a node that visibly
exists, that is libvirt's mount namespace, not permissions — `namespaces = []`
in the same file.

## Now automated

This is a brick:
[`privatestack-ansible` → `roles/looking_glass`](https://github.com/importriri/privatestack-ansible).
The rule is a template, the retrigger is a handler, and two of the repo's
invariant tests exist specifically so this cannot silently regress: one asserts
that both openers are named in the rendered rule, the other that
`--action=change` is still in the handler. Catalogued as mutations 17 in
`tests/MUTATIONS.md` — the breakage is replayable on demand.
