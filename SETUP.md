# From the upstream Arch live prompt to the lab

This is the canonical route across the three repositories: authenticated upstream
Arch Linux medium → `arch-bootstrap` → `hyperlab-ansible` → explicit images and
workloads → evidence here. Start with a disposable rehearsal, then a backed-up
machine. This guide documents the implemented route and its stops; **there is
no qualified complete v1 installation path today**.

The intended primary distribution is a project installer ISO, still pending.
The [ISO proposal](https://github.com/importriri/arch-bootstrap/blob/main/docs/adr/0001-iso-build-and-distribution.md)
is Proposed; no profile, build, image, signature or download is available. Use
upstream archiso and the repositories below. See [FAQ](FAQ.md) and
[symptom-based troubleshooting](TROUBLESHOOTING.md).

## Before the live prompt

**Context:** a trusted download computer, ordinary user. **Prerequisites:** an
external backup whose restore you have checked, firmware access, AC power,
installation USB, internet access and a second device with this guide. Keep
recovery media and passphrases offline. Disconnect backup disks before selecting
installation targets. A snapshot on a disk about to be erased is not a backup.

Obtain the current x86_64 ISO, its detached signature and checksums through the
[official download page](https://archlinux.org/download/). Follow that page's
current verification commands on the trusted computer: retrieve the release
signing key through Arch's published WKD instructions, verify the detached
signature, and authenticate the full signing-key fingerprint through trusted
[Arch developer key information](https://archlinux.org/people/developers/).
A short key ID or a newly imported key alone
is insufficient. A matching SHA-256/BLAKE2 hash checks integrity; a checksum
from the same untrusted mirror does not authenticate its author. Stop on a bad
signature, wrong key, missing input or uncertain key identity. Record the actual
ISO filename, digest, signer fingerprint and verification date privately; this
guide does not pin a monthly ISO or a release pair for you.

Prepare the medium using Arch's linked
[USB installation instructions](https://wiki.archlinux.org/title/USB_flash_installation_medium)
on that computer, checking the USB target independently. Writing the medium
requires that computer’s disk-write privilege; follow its OS-specific procedure
only for the confirmed USB. Boot it through the
firmware's **64-bit UEFI** entry, following the
[installation guide](https://wiki.archlinux.org/title/Installation_guide).
The upstream installation medium needs Secure Boot disabled to boot; do not
confuse this temporary firmware state with later enrollment of the installed
host. If firmware recovery or key custody is unclear, stop before changing keys.

Official sources consulted 2026-10-28: the download and installation pages above,
[iwctl(1)](https://man.archlinux.org/man/iwctl.1.en),
[pacman(8)](https://man.archlinux.org/man/pacman.8.en),
[timedatectl(1)](https://man.archlinux.org/man/timedatectl.1.en) and the
[trademark policy](https://terms.archlinux.org/docs/trademark-policy/).
These describe upstream Arch, without implying endorsement of this project.

## Hardware, storage and choices

| Profile | Component evidence and numeric GPU / HDMI-audio IDs | Full pipeline |
| --- | --- | --- |
| `nitro-3060` — Acer Nitro 5, RTX 3060 Mobile | VFIO and virtual-display components; `10de:2520` / `10de:228e`; reviewed CPU pinning is specific to the 8-thread i5-10300H | `pipeline-pending` |
| `predator-3070` — Acer Predator Helios 300, RTX 3070 Mobile / Max-Q | Passthrough power-management fix; `10de:249d` / `10de:228b` | `pipeline-pending`; replay the frozen Nitro automation pair |
| `no-gpu-passthrough` — explicitly selected | No VFIO IDs; foundation skips VFIO boot and GPU handoff, and refuses VFIO Machines | No physical single-GPU compatibility claim; no accelerated/Looking Glass qualification |

The [matrix](hardware/compatibility.yml) and [evidence policy](hardware/README.md)
separate component history from a reproducible installation. Do not infer support
for every laptop, or copy IDs from a GPU's marketing name. Requirements are
x86_64 KVM virtualization enabled in firmware, 64-bit UEFI, and enough RAM and
storage for the selected workloads. VFIO additionally needs enabled IOMMU and
interrupt remapping, reviewed PCI groups, both GPU functions available, and an
iGPU/display route keeping the host usable while the dGPU belongs to a guest.
The guest GPU needs a usable display/capture route too; a passed-through GeForce
alone does not prove it can publish frames. See the
[display investigation](problems/geforce-passthrough-needs-a-display.md).

Budget capacity from the actual selected spec/Template, not the download size.
For example, `vm-specs/arch-dev.yml` requests 8 GiB RAM, four vCPUs and a 24 GiB
disk; the captured workstation used by `workstation-dev` has a 100 GiB disk floor.
Nitro reserves 2048 MiB host RAM, 512 MiB per QEMU domain and 256 MiB VFIO overhead;
Predator reserves 2560/512/256 MiB. Automatic per-guest ceilings are 16384 MiB
and 12288 MiB respectively, not promises that those amounts are free. The
no-passthrough profile caps automatic guests at 2048 MiB. Live budgets also
include running guests and inactive registered services. Keep room for bases,
independent permanent copies, temporary capture copies, exports and backups;
there is no universal minimum whole-disk capacity in the contract. See
[profiles](https://github.com/importriri/hyperlab-ansible/blob/main/group_vars/all/hardware.yml)
and [first-Machine resources](https://github.com/importriri/hyperlab-ansible/blob/main/docs/first-machine.md).

Choose these before starting; do not edit tracked defaults:

- **Disks:** bootstrap erases the entire confirmed primary disk, including an
  existing ESP and other operating systems. It creates a 1 GiB ESP and encrypted
  Btrfs root. Single disk: VM store is `cryptroot`, subvolume `@vm`. Optional
  second disk: that entire confirmed disk becomes `cryptvm`, Btrfs filesystem
  root `/`, mounted at `/var/lib/libvirt/images`. Its unlock key is inside
  encrypted root, final mode `0400`; back up root and recovery material as well
  as guest data. This is no dual-boot or data-preserving installer.
- **Language and time:** choose `TARGET_LOCALE`, `TARGET_KEYMAP`,
  `TARGET_TIMEZONE` and `TARGET_HOSTNAME`. Defaults are `en_US.UTF-8`, `us`,
  `Europe/Rome`, `hypervisor-01`. Console keymap, desktop keyboard layout and
  locale are separate settings; both laptop desktop profiles fix `it`, with a
  runtime cycle to `us` and `ara` (see [2a](#2a-root-prepares-the-foundation-and-creates-the-account)).
  Recheck the keyboard before entering secrets. The bootstrap installs zram,
  no swap partition; stage 2 refuses unencrypted disk swap.
- **Identity:** choose your own administrator name and hostname. Bootstrap
  sets **only root's password**. Stage 2's base role creates `admin_user` in
  `wheel` but sets **no account password**. Step 2 handles this transition.
  Guest administration also needs your own SSH key, never someone else's
  private key or an example key from documentation.
- **Boot trust:** generated keys and signed files are only preparation.
  Enrollment and firmware enablement are manual, with recoverable vendor trust
  reviewed first. Secure Boot here does not authenticate the separate initramfs
  or command line; module trust/lockdown is a separate open gate. Read the
  [Secure Boot procedure](https://github.com/importriri/hyperlab-ansible/blob/main/docs/nitro-secure-boot-acceptance.md).

### Time to set aside

These are **planning estimates, not measurements**: one familiar operator,
working network/mirrors, SSDs, known hardware, verified backup already available,
no firmware or software failure. Active time means decisions/typing; waiting
means downloads, tests and reboots. Slow links and learning add time.

| Stage | Active | Waiting |
| --- | --- | --- |
| Medium verification and choices | 20–45 min | 10–30 min |
| Live prompt, network, source and software checks | 10–25 min | 5–20 min |
| Bootstrap review and real installation | 15–30 min | 15–60 min |
| Enrollment review and two first boots | 20–60 min | 5–15 min |
| Step 2 account transition and existing host target | 20–45 min | 20–90 min |
| Step 3 network review and step 9 evidence review | 10–25 min | 0–10 min |
| Steps 4–8, full v1 host, Create/provision, GPU lease and qualification | Blocked or prerequisite-dependent | No completion estimate |

Total for the existing host route only: **95–230 min active + 55–225 min waiting**
(about 2½–7½ hours elapsed, sequentially). This is not a time-to-v1 claim.
Unknown image builds, manual Windows work and unresolved gates have no promised
end time.

## 1. Install the base host

### 1a. Confirm the live environment and connect

**Context:** upstream live medium, root at its local console; start `bash` for
the shell commands here. **Prerequisite:** authenticated medium and reviewed
firmware boot selection. Run one command at a time and stop on an unexpected
result:

```bash
bash
id -u
cat /sys/firmware/efi/fw_platform_size
localectl list-keymaps
ip link
rfkill
```

Expect UID `0`, firmware size `64`, and the real network device names. Use
`loadkeys` with a layout from the list if needed (for example `loadkeys us`).
For Ethernet, attach the cable and allow DHCP. For Wi-Fi enter `iwctl`; replace
`DEVICE` with the discovered name and `SSID` with your network:

```text
device list
station DEVICE scan
station DEVICE get-networks
station DEVICE connect "SSID"
exit
```

Enter the Wi-Fi password only at its private prompt. Then, back in Bash:

```bash
ip address
ip route
ping -c 1 archlinux.org
timedatectl status
```

Expect an address, route, successful DNS/ICMP and a sane synchronized clock.
Bootstrap itself requires that ping; HTTPS alone is not enough for its guard.
No interface, blocked radio, failed DHCP/DNS or wrong clock: stop at
[live networking](TROUBLESHOOTING.md#live-networking), without selecting a disk.

### 1b. Acquire source and record its revision

**Context:** live root Bash, network working; files under `/root` are temporary.
Install missing verification tools on the live medium only:

```bash
pacman -Sy --needed git shellcheck bats python-yaml
cd /root
git clone https://github.com/importriri/arch-bootstrap.git
cd /root/arch-bootstrap
git rev-parse HEAD
git status --short
bash verify.sh
```

This `-Sy` without `-u` is a deliberate, limited install into the ephemeral
live environment, the same pattern the bootstrap engine itself uses for its
keyring and `cryptsetup` updates. It is not an official installation-guide
step, and Arch does not support partial upgrades. A dependency, library or
`error while loading shared libraries` failure is a stop: boot a newer official
ISO and start again. Do not run `pacman -Syu` on the live medium.

Package names checked against the official Arch package database on 2026-10-28:
[git](https://archlinux.org/packages/extra/x86_64/git/),
[shellcheck](https://archlinux.org/packages/extra/x86_64/shellcheck/),
[bats](https://archlinux.org/packages/extra/any/bats/),
[python-yaml](https://archlinux.org/packages/extra/x86_64/python-yaml/).
The bootstrap also requires the live tools its
[engine](https://github.com/importriri/arch-bootstrap/blob/main/installer)
uses: `sgdisk`, `cryptsetup` with argon2id, Btrfs/FAT tools, `pacstrap`,
`genfstab`, `arch-chroot`, `bootctl`, mount and device-discovery tools.
A missing tool is a stop, not a reason to run a partial installer.

Expect a clean tracked tree and `arch-bootstrap verification: PASS`. Standalone
storage cross-repository comparison may explicitly report SKIPPED; it proved
no integration. Missing tools, a failed test or a dirty checkout stop the run.
Retain the full commit and check log off the live RAM filesystem before reboot,
without recording secrets. A fresh clone chooses current source, not a qualified
release. For a campaign, first obtain and review the exact public bootstrap and
Ansible commits selected together; inspect and record those actual checkouts
before proceeding. No frozen pair is supplied by this guide.

### 1c. Rehearse, then install only the reviewed layout

**Context:** same live root, `/root/arch-bootstrap`. **Prerequisites:** checked
source, backup, independently identified disk paths, no mounted `/mnt` tree or
existing `cryptroot`/`cryptvm`. Review the devices with `lsblk` and mounts with
`findmnt`. Keep the same choices in both commands; replace the example locale,
keymap, time zone and hostname with your decisions:

```bash
export TARGET_HOSTNAME=hypervisor-01
export TARGET_TIMEZONE=Europe/Rome
export TARGET_LOCALE=en_US.UTF-8
export TARGET_KEYMAP=us
bash bootstrap
```

Use **bootstrap**, never the internal `installer`: the wrapper verifies the VM
store and writes the stage-2 handoff. Default dry run asks for the primary disk,
its full path typed back, the LUKS passphrase twice, and optional VM disk/path
confirmation. It only announces the later root-password step. Secrets must
never go in a command, transcript or shared log. It formats/mounts nothing.

**Stop:** on an existing GPT, `sgdisk --pretend` does not simulate `--zap-all`;
it can print old partitions and fail with `sgdisk (pretend) failed`. That is a
failed rehearsal. Do not erase a disk to make the rehearsal green or silently
skip to real installation. Rehearse on blank disposable storage; an existing-disk
campaign needs a separately reviewed destructive plan. A busy-target refusal
also requires investigation; do not paste the suggested cleanup blindly.

Only after a successful, understood rehearsal and explicit review that **all
data on each selected disk will be lost**, run separately:

```bash
DRY_RUN=0 bash bootstrap
```

The real run repeats disk confirmations and LUKS prompts, then asks for the new
root password twice. It prepares LUKS2/argon2id, Btrfs, the hardened kernel,
networking and signed loader/kernel assets. Expect exit zero and both:

```text
[OK] stage-2 storage contract written: /etc/privatestack/bootstrap-storage.yml
[OK] arch-bootstrap complete — storage is ready for hyperlab-ansible
```

Anything else is a failed installation, including a partial contract left on
disk. It has no rollback. Cleanup releases only this run's mounts/mappers and
reports failures; retain the log, stop and consult
[dry-run/busy-target guidance](TROUBLESHOOTING.md#dry-run-or-busy-target).

### 1d. Review boot assets and perform the first boots

**Context:** live root after successful bootstrap; the installed system remains
mounted below `/mnt`. **Prerequisite:** both success messages above. Review
`/mnt/etc/fstab`, `/mnt/etc/crypttab` (second disk),
`/mnt/etc/privatestack/bootstrap-storage.yml`, and the loader entry under
`/mnt/boot/loader/entries/`. Retain the known-good recovery route. Follow
[Arch's unmount/reboot procedure](https://wiki.archlinux.org/title/Installation_guide#Reboot)
to leave the mounted installation and boot its `linux-hardened` entry; do not
rerun bootstrap to repair an existing installation.

**Context changes to installed-host root, local TTY login**, with the root
password just set. Rediscover networking using step 1a (`ip link`, `iwctl`
device discovery, `ping`); live-medium Wi-Fi state is not a configured host
account. Installed iwd handles Wi-Fi DHCP, networkd handles `en*` wired DHCP,
and resolved supplies DNS. An unusual wired name needs review, not a guessed
interface. Follow the
[Secure Boot enrollment and recovery review](https://github.com/importriri/hyperlab-ansible/blob/main/docs/nitro-secure-boot-acceptance.md)
before changing firmware keys. Do not blindly clear vendor keys or bypass the
Option ROM guard. The bootstrap's printed enrollment reminder is not the full
hardware-specific enrollment procedure. Missing recovery material is a stop.

From installed root, record on each of two boots:

```bash
uname -r
cat /proc/sys/kernel/random/boot_id
bootctl status
sbctl status
networkctl status
stat -c '%U:%G %a %n' /etc/privatestack/bootstrap-storage.yml
findmnt -J -T /var/lib/libvirt/images -o TARGET,SOURCE,FSTYPE,FSROOT,OPTIONS
lsattr -d /var/lib/libvirt/images
```

Expect hardened kernel, different boot IDs, reviewed Secure Boot state and
networking; contract `root:root 644`; Btrfs `cryptroot` with FSROOT `/@vm`, or
`cryptvm` with FSROOT `/`, and `C` on the empty VM directory. On two disks root
unlock should keyfile-unlock the VM disk without a second passphrase. Boot,
encryption, enrollment or mount failure stops stage 2; use the recovery medium
and [boot/storage diagnosis](TROUBLESHOOTING.md#boot-or-storage-handoff).

## 2. Build the host and transition to your administrator

### 2a. Root prepares the foundation and creates the account

**Context:** installed host, root login, Bash, networking working. **Prerequisite:**
step 1 handoff and reviewed source revisions. Root initially owns the checkout;
there is no ordinary account to run it yet. Obtain stage 2 and verification tools:

```bash
pacman -Syu --needed ansible-lint ruff shellcheck bats python-yaml
cd /root
git clone https://github.com/importriri/hyperlab-ansible.git
cd /root/hyperlab-ansible
git rev-parse HEAD
git status --short
ansible-galaxy collection install -r collections/requirements.yml
./verify.sh
```

The additional package names
[ansible-lint](https://archlinux.org/packages/extra/any/ansible-lint/) and
[ruff](https://archlinux.org/packages/extra/x86_64/ruff/) were checked 2026-10-28.
Git and Ansible came from bootstrap. Follow any additional dependency refusal
from this checkout's verifier; never skip its checks. If the upgrade replaces
the running kernel, reboot into the installed kernel before compiling modules,
then return to this checkout. Expect clean source, recorded commit and full
`ALL GREEN`; an incomplete privileged render judge is not a pass. Stop on
`VERIFICATION FAILED` or `VERIFICATION INCOMPLETE` and preserve the output.
At a TTY its render judge needs the private runtime directory of a real login
and prints `BECOME password (attempt N/3)`. It refuses an empty answer. As
installed root, type root's own password there. Three refused answers end with
`Render tests could not validate sudo credentials.` and a failed verification.

Create `/root/hyperlab-host.yml` with `umask 077` and a local editor, **outside
the checkout**. This non-secret file persists all identity overrides. Example
values must be replaced with your chosen name/hostname; keep the hostname from
step 1:

```yaml
admin_user: labadmin
guest_cloud_init_user: labadmin
host_hostname: hypervisor-01
host_profile: auto
```

Keep `guest_cloud_init_user` equal to `admin_user` for the later workstation
procedures: [guest defaults](https://github.com/importriri/hyperlab-ansible/blob/main/group_vars/all/guest.yml)
set it independently, and overriding `admin_user` alone does not change it.
Use an ordinary lowercase account name with the default `/home/NAME` home,
never `root`. For a deliberate no-passthrough foundation set
`host_profile: no-gpu-passthrough` here instead; `auto` never falls back to it.
The desktop keyboard is not a local choice today. The recorded hardware
profile wins over the
[desktop input defaults](https://github.com/importriri/hyperlab-ansible/blob/main/roles/host_desktop_sway/defaults/main.yml),
both laptop profiles set `it`, the Sway session loads the layouts `it`, `us`,
`ara` in that order, and the Hyprland role refuses any other baseline. Do not
put `host_desktop_sway_input_defaults` or `host_profiles` in this file: the
first does not change a laptop's layout, and the second replaces the reviewed
profile contract. In Sway, `$mod+Ctrl+space` or the bar's keyboard indicator
cycles `it` → `us` → `ara` and remembers the choice in
`~/.config/hyperlab/keyboard-layout`. A different default layout needs a
reviewed stage 2 change, not a local variable. `TARGET_KEYMAP` still sets
the console keymap.

Every subsequent Ansible command in this guide uses the same file:

```bash
export LAB_VARS=/root/hyperlab-host.yml
ansible-playbook -K playbooks/preflight.yml -e "@$LAB_VARS"
ansible-playbook -K playbooks/foundation.yml --check --diff -e "@$LAB_VARS"
ansible-playbook -K playbooks/foundation.yml -e "@$LAB_VARS"
ansible-playbook -K playbooks/foundation.yml -e "@$LAB_VARS"
```

Run each only after its predecessor succeeds. `-K` requests become authorization;
answer with root's own password, since no administrator password exists yet. Preflight validates the selected
hardware; foundation checks storage before image-state writes. Unknown or
ambiguous hardware stops here. Expect the selected profile, created account,
managed foundation and `changed=0`, `failed=0`, `unreachable=0` on the final run.
Check mode previews changes; it does not install dependencies. Any failure,
storage refusal or unexplained repeat change stops the sequence.

### 2b. Set the account password, transfer ownership, log in anew

**Context:** still installed root, foundation succeeded. **Prerequisite:** the
account exists, home is `/home/NAME`, and its name equals `admin_user` in the
local YAML. Review that YAML as a regular, non-symlink file with exactly one
value for each shown key. Read the account from it rather than assuming a default.
Run these commands one at a time, stopping on any nonzero exit (the `test`
commands succeed silently):

```bash
LAB_ADMIN=$(python -c 'import os, yaml; print(yaml.safe_load(open(os.environ["LAB_VARS"]))["admin_user"])')
getent passwd "$LAB_ADMIN"
test ! -L "/home/$LAB_ADMIN"
test ! -L "/home/$LAB_ADMIN/.config"
test ! -L "/home/$LAB_ADMIN/.config/hyperlab"
test ! -e "/home/$LAB_ADMIN/.config/hyperlab/host.yml"
test ! -L "/home/$LAB_ADMIN/.config/hyperlab/host.yml"
test ! -e "/home/$LAB_ADMIN/hyperlab-ansible"
test ! -L "/home/$LAB_ADMIN/hyperlab-ansible"
passwd "$LAB_ADMIN"
install -d -m 0700 -o "$LAB_ADMIN" -g "$LAB_ADMIN" "/home/$LAB_ADMIN/.config" "/home/$LAB_ADMIN/.config/hyperlab"
install -m 0600 -o "$LAB_ADMIN" -g "$LAB_ADMIN" "$LAB_VARS" "/home/$LAB_ADMIN/.config/hyperlab/host.yml"
mv /root/hyperlab-ansible "/home/$LAB_ADMIN/hyperlab-ansible"
chown -R "$LAB_ADMIN:$LAB_ADMIN" "/home/$LAB_ADMIN/hyperlab-ansible"
cmp "$LAB_VARS" "/home/$LAB_ADMIN/.config/hyperlab/host.yml"
rm -- "$LAB_VARS"
unset LAB_VARS
```

From here on the administrator's `~/.config/hyperlab/host.yml` is the only
identity file. Root's copy is removed once `cmp` reports identical bytes, so a
later edit cannot leave a stale `admin_user` behind. If `cmp` reports a
difference, stop and keep both files for review.

Check `getent` shows the chosen ordinary account and expected home before
`passwd`. Set its password privately at the terminal; never put a password/hash
in YAML or a command. Expect `passwd` success and only this checkout/local
configuration transferred. This location matches the desktop roles’ default
`/home/{{ admin_user }}/hyperlab-ansible`; a different checkout location needs
a persistent checkout-variable override. Stop if an existing destination, wrong
home, missing account or failed operation makes ownership uncertain. Do not run later commands
from the old working directory. Root's collections need not be shared.

Log out at the TTY and perform a **new local login as the chosen administrator**.
A switched-user shell or manually exporting a runtime path is insufficient for
the desktop/user manager. In that new login:

```bash
id
printf '%s\n' "$XDG_RUNTIME_DIR"
stat -c '%U %a %n' "$XDG_RUNTIME_DIR"
export LAB_VARS="$HOME/.config/hyperlab/host.yml"
cd "$HOME/hyperlab-ansible"
ansible-galaxy collection install -r collections/requirements.yml
./verify.sh
```

Expect your user in `wheel`, a real private `/run/user/UID` directory owned by you
(mode `700`), readable local overrides and full verifier success with your
normal sudo credential. Log in again if group/session state is stale. Missing
runtime directory or a failed verifier is a stop before user services.
At every later login, set `LAB_VARS` to that same absolute file before running
the commands; do not fall back to repository identity defaults.

### 2c. Reconcile the existing laptop target; stop before claiming v1

**Context:** new administrator login, own checkout, no active VMs. **Prerequisites:**
2b succeeded, overrides loaded and the laptop's passthrough profile validated.
For `no-gpu-passthrough`, stop at the foundation: the accelerated cockpit path
below is not that profile's qualification route.

```bash
ansible-playbook -K playbooks/preflight.yml -e "@$LAB_VARS"
ansible-playbook -K playbooks/lab.yml --check --diff -e "@$LAB_VARS"
ansible-playbook -K playbooks/lab.yml -e "@$LAB_VARS"
ansible-playbook -K playbooks/lab.yml -e "@$LAB_VARS"
```

Expect no failed/unreachable tasks and final `changed=0`. Stop on failures,
unreviewed boot changes or nonzero repeat changes. Review the managed VFIO boot
entry and its recovery entry before the next reboot.

The `playbooks/lab.yml` run in step 2 already installed Sway, then the host-side
Looking Glass transport. Its actual import is `foundation.yml`, followed by
`host_desktop_common`, `host_desktop_sway` and `looking_glass` with their guards.
The narrow `host-desktop-sway.yml` and `looking-glass.yml` playbooks are maintenance
entrypoints, not additional installation stages. Host convergence creates no
private image, Machine or service workload.

**Product stop:** Hyprland is preferred and Sway remains a first-class recovery
compositor in the product contract. `lab.yml` does **not** assemble the complete
v1 Hyprland/session/Create target. `host-desktop-hyprland.yml` is explicitly a
non-active configuration/staging target outside `lab.yml`; assembling narrow
roles manually does not qualify v1. Wait for an accepted integrated host
entrypoint, its check/apply/apply results, and installed-session/Create evidence.
Do not guess a playbook name. The
[roadmap](https://github.com/importriri/hyperlab-ansible/blob/main/docs/roadmap.md#v1-scope-and-evidence-status)
records provisioning, disposable, lease and release-manifest gaps separately.
The later sections explain those conditional boundaries, not a bypass of this
stop.

## 3. Check the trust domains

**Context:** installed administrator after host convergence; local read-only
inspection. **Prerequisite:** the selected host target succeeded. Run:

```bash
virsh -c qemu:///system net-list --all
```

| Domain | Subnet | Forwarding |
| --- | --- | --- |
| clean | `10.10.1.0/24` | NAT |
| dirty | `10.10.2.0/24` | NAT |
| dev | `10.10.3.0/24` | NAT |
| lab | `10.10.4.0/24` | none |
| services | `10.10.5.0/24` | NAT |

Expect five persistent product networks. Their existence alone does not prove
isolation. Guest-to-host default deny and cross-domain blocking need the
[reviewed probes and control fixtures](https://github.com/importriri/hyperlab-ansible/blob/main/docs/network-flows.md).
`lab` must remain offline; a DNS timeout with a broken control is no isolation
proof. Stop before untrusted workloads if isolation is unobserved or differs.
Only explicitly reviewed service exposures may open a flow.

## 4. Prepare and seal images

**Context:** conditional image workshop on the installed host, administrator,
checkout root; `-K` for host writes. **Prerequisites:** accepted host path for
the intended campaign, checked manifest, storage capacity, source availability
and reviewed provenance. A fresh install has **empty Machines** and an empty
local image store. `status: sealed` in Git or `status: ready` on a Template does
not download anything to a stranger's disk.

A Golden Image is a generalized, digest/receipt-verified read-only base. A
Template pins that image and limits network, devices, lifecycle and resources.
A Machine records one person's explicit instance intent, then projects a VM
spec; it is neither a Template nor every domain libvirt happens to contain.
A Desk/Project lives inside a workstation Machine.

For an available official Arch cloud source, the existing image transaction is:

```bash
ansible-playbook -K playbooks/image-prepare.yml --check --diff -e "@$LAB_VARS" \
  -e image_factory_manifest=images/arch.yml
ansible-playbook -K playbooks/image-prepare.yml -e "@$LAB_VARS" \
  -e image_factory_manifest=images/arch.yml
ansible-playbook -K playbooks/image-validate.yml -e "@$LAB_VARS" \
  -e image_factory_manifest=images/arch.yml
```

Run sequentially. Expect the pinned digest, valid provenance receipt and sealed
base validation, including the claimed guest-agent content. A missing URL,
changed digest, unavailable inspection tool, failed receipt or absent base is a
stop. Never substitute a new download or checksum just to pass. See the
[image playbook map](https://github.com/importriri/hyperlab-ansible/blob/main/docs/playbooks.md#image-provenance).

`arch-dev-20261003` is a **local workstation capture**, not a public qcow2
URL. On a new host, `workstation-dev` cannot create a usable Machine until the
correct reviewed image is locally available and sealed. The
[Workbench procedure](https://github.com/importriri/hyperlab-ansible/blob/main/docs/golden-image-workbench.md)
requires an explicitly adopted non-product candidate, prepared session,
shut-off disk, flat copy, offline generalization, leftover scan, package/build
provenance, import and validation. Do not capture a product Machine or promote
a placeholder. Known-location scans do not prove the absence of every secret.

**Debian stop:** `server-debian` is draft; `debian-server` is not built/sealed.
The upstream Debian base has no QEMU Guest Agent. The Workbench's offline derive
procedure adds it before sealing; it is not a first-boot SSH workaround.
**Fedora stop:** `server-fedora` is ready in source; its actual SSH/agent-key
readback proof remains open. Both require local image preparation and validation.
See [missing agent](TROUBLESHOOTING.md#missing-agent-or-server-template).

Optional Windows and manual-install distributions use the
[Windows workshop](https://github.com/importriri/hyperlab-ansible/blob/main/docs/windows-image-workshop.md)
and [Linux ISO workshop](https://github.com/importriri/hyperlab-ansible/blob/main/docs/linux-iso-workshop.md).
They require legitimately obtained private media, guest-side installation and
reviewed generalization/sealing; keep media, accounts, keys and receipts local.
They are not prerequisites for the first server or the host target.

## 5. Exercise explicit VM lifecycle

**Context:** conditional Machine workshop, administrator in checkout root, valid
user runtime session. **Prerequisites:** all relevant host/image gates, chosen
ready Template backed by its exact local sealed image, capacity and your guest
SSH public key. The illustrative names in detailed procedures are examples;
carry `-e "@$LAB_VARS"` to **every** host and guest playbook so `admin_user`
remains your chosen account. The default-account examples are not mandatory
usernames. Cloud-init follows `guest_cloud_init_user`, while workstation roles
use `admin_user`; the local file deliberately sets both to the same chosen name.

Create a dedicated ed25519 SSH key as your administrator if absent, using
`ssh-keygen -t ed25519 -f "$HOME/.ssh/hyperlab_ed25519"`, with a private
passphrase prompt. Never overwrite an existing key. Make its signing capability
available to your normal SSH client before guest provisioning (for example in
your login's SSH agent). Only the `.pub` key enters cloud-init; private keys
stay with you. Confirm the public fingerprint with
`ssh-keygen -lf "$HOME/.ssh/hyperlab_ed25519.pub"`.

The inventory step below also needs `~/.ssh/known_hosts`, and nothing in
stage 2 creates it. `vm-guest-inventory.yml` refuses to pin a guest unless the
private key and that file are both regular, non-symlink files owned by you.
As your administrator, inspect without following links:

```bash
test ! -L "$HOME/.ssh"
stat -c '%U %a %F %n' "$HOME/.ssh" "$HOME/.ssh/hyperlab_ed25519"
stat -c '%U %a %F %n' "$HOME/.ssh/known_hosts"
```

Expect your account, `700 directory` and `600 regular file`. If `known_hosts`
exists, the last `stat` must show your account, `regular file` or `regular
empty file`, and no group/other write bit: keep its contents and create
nothing. A symbolic link, another owner or type, or an unreadable file is a
stop for review, never a reason to delete or replace it. Only when that `stat`
reports `No such file or directory` (and exits 1, expected here), create an
empty file, one command at a time, stopping on any nonzero exit:

```bash
test ! -e "$HOME/.ssh/known_hosts"
test ! -L "$HOME/.ssh/known_hosts"
install -m 0600 /dev/null "$HOME/.ssh/known_hosts"
stat -c '%U %a %F %n' "$HOME/.ssh/known_hosts"
```

Expect your account and `600 regular empty file`. Leave it empty: do not fill
it with `ssh-keyscan` or by accepting an SSH prompt. Guest host keys enter it
only through the inventory step, which reads them with the QEMU Guest Agent.

Follow the [first-Machine procedure](https://github.com/importriri/hyperlab-ansible/blob/main/docs/first-machine.md)
only when its prerequisites are met. `hyperlabctl machine templates` and
`hyperlabctl machine create-plan` inspect current choices; failure/absence of
the CLI or an unready/local-image-missing Template stops creation. `machine
create` records intent, `project` derives the spec, and `vm-create.yml` creates
the domain. Starting is separate unless the explicit transaction sets
`guest_start_after_create=true`. The `vm-start.yml`, `vm-shutdown.yml`,
`vm-stop.yml`, `vm-reset.yml` and `vm-destroy.yml` transactions remain separate;
forced actions require their exact printed confirmation. A failed provisioning
can leave a record/spec/domain; inspect it before retrying instead of deleting
unknown state. Never rerun host convergence as a workload reset.

**SSH prerequisite:** a running managed Linux guest with working QEMU Guest
Agent, plus the key and `known_hosts` file prepared above.
`playbooks/vm-guest-inventory.yml` (host `-K`, selected `guest_spec`, local
overrides) obtains the address and new host key through the agent, pins that key
and writes an operator-owned regular `0600` runtime inventory under
`/run/user/UID`. Guest playbooks then use **both** `inventory.ini` and that runtime
inventory, plus the same overrides. Strict host-key checking stays on. A manual
pin or a key learned only from the network is not proof of trusted identity.
After profile provisioning, `guest-close-access.yml` must prove the agent's
execution call refused and its reread host key equal to the pin. Server accounts
without a password still retain passwordless sudo; that limitation remains.

If the inventory disappears after a new session/reboot, use only the
authoritative inventory step to regenerate genuinely missing state; redirected,
unsafe or unreadable files must be refused. The
[integration gate](https://github.com/importriri/hyperlab-ansible/blob/main/problems/runtime-inventory-self-heal.md)
is open: an on-demand action is not guaranteed to repair it. CLI/desktop
self-heal and shell provisioning do not automatically load this guide’s local
override file; use the explicit playbook with the overrides for this manual
route, and stop if an action cannot retain the chosen identity.

**Product stop:** CLI history does not qualify shell Create. The runner/Create
view have software contracts; real shell provisioning remains unqualified.
Disposable disk discard exists in source, but agent restriction and SSH host-key
renewal at each later boot are unresolved. Do not use a disposable Machine as a
safe access/recovery path today or claim that repeating inventory closes this
gap. See the [current scope](https://github.com/importriri/hyperlab-ansible/blob/main/docs/roadmap.md#v1-scope-and-evidence-status).

## 6. Use the dGPU through VFIO

**Context:** conditional physical-host campaign, administrator; root-owned boot
and handoff policy, explicit privileged lifecycle operations. **Prerequisites:**
reviewed profile/groups, managed VFIO entry booted, host iGPU display intact,
image/session ready and prior campaign stops resolved. Read-only `lspci -Dnnk`
must show both selected GPU/audio functions on `vfio-pci` before guest start.
Unexpected driver, device, group or host display loss means stop at recovery.

Only one running VM may own the dGPU; multiple shut-off definitions may name it.
`services` is a network identity and **may** use the GPU through an explicitly
reviewed handoff profile and matching spec/Template. Within a boot GPU uses go
clean → dev → dirty → lab, never back up; a higher-trust use after a lower one
requires a host reboot. A reset does not prove erasure of GPU state. Never delete
or reset the live trust record. The optional per-run GPU lease is Proposed and
unimplemented; it does not make arbitrary Templates usable both with/without
GPU. See [GPU policy](https://github.com/importriri/hyperlab-ansible/blob/main/docs/gpu-handoff-policy.md).
Keep the managed PCIe power-management workaround; do not reproduce the known
[freeze](problems/gpu-freeze-power-management.md).

## 7. Looking Glass: separate video, input and audio

**Context:** conditional physical workstation gate, administrator's graphical
login and prepared guest; guest-side installation is inside that guest.
**Prerequisites:** working host transport, matching reviewed build, guest
capture/display route and a proven administrative/recovery connection.

For Windows, the signed Looking Glass host application and reviewed virtual
display are manual guest steps in the workshop; physical-host kvmfr is managed
by stage 2. Linux's PipeWire sender remains experimental. Historical Nitro
1920×1080 shared-memory frames do not close candidate session/input gates.

For Linux experimental VFIO, `hyperlabctl open looking-glass NAME` owns PRIMARY:
if at Ly it opens a temporary **owned** `virt-viewer` console, accepts login
there, waits for Hyprland and the reviewed 1920×1080@144 `HEADLESS-0` output,
closes only that console, starts the session-bound sender and opens Looking
Glass. `hyperlabctl open console NAME` remains explicit recovery. The built-in
Looking Glass SPICE fallback is rejected as PRIMARY authentication; do not
repeat password entry into its unreliable input path. The
[handoff note](https://github.com/importriri/hyperlab-ansible/blob/main/problems/looking-glass-linux-prelogin-primary-handoff.md)
records a later Nitro automatic-transition observation as component history;
final candidate acceptance remains separate.

Require three independent observations:

- **Video:** actual shared-memory frames and moving content; client logs such
  as `FRAME_TYPE_BGRA` and the kvmfr path. A visible SPICE surface or
  host-application-not-running message is fallback, not a Looking Glass pass.
- **Input:** stable pre-login console, automatic owned handoff, keyboard and
  pointer capture/release, host shortcut isolation, reconnect and guest logout
  ending the sender. Closing the host client should leave the guest session
  alive. These physical security gates remain open.
- **Audio:** actually hear guest playback through the intended output, check
  volume limits and verify no microphone/capture is exposed. Logs or HDMI-audio
  binding alone prove neither audible playback nor microphone isolation.

Any failed observation stops that gate; use recovery Console and
[display/input diagnosis](TROUBLESHOOTING.md#looking-glass-shows-a-desktop).

## 8. Register services before creation

**Context:** optional service workshop after host/storage/network/image gates,
administrator in checkout root. **Prerequisites:** checked service and VM specs,
locally sealed agent-capable base, capacity and strict runtime SSH inventory.
The reference Jellyfin specs depend on the unbuilt `debian-server`, so this is
currently a **stop**, not a runnable newcomer requirement.

The [service procedure](https://github.com/importriri/hyperlab-ansible/blob/main/docs/service-vm-contract.md)
orders `service-register.yml` (check then apply) → `service-validate.yml` →
`vm-create.yml` → inventory/key proof → guest application configuration with
`jellyfin.yml`. Pass the spec each step expects and the same local overrides;
use `-K` for host writes. Registration reserves identity, static lease and
inactive RAM before VM creation. Application installation runs inside the
service VM. Expect validated registration and only the declared active-service
exposure; failure or image absence stops before the next transaction.
Backup/restore are offline, exactly confirmed owned transactions; registration
or a green host apply proves no service/recovery hardware acceptance.

## 9. Record evidence without promoting it

**Context:** repository check commands run as the ordinary user in a checkout of
this evidence repository. **Prerequisites:** reviewed source; on a future
hardware campaign, exact automation commits and private logs from each gate.
Acquire this repository explicitly if not already present:

```bash
cd "$HOME"
git clone https://github.com/importriri/arch-hypervisor-lab.git
cd "$HOME/arch-hypervisor-lab"
git rev-parse HEAD
git status --short
python scripts/verify_repo.py
bash -n scripts/collect-hardware-report.sh
shellcheck scripts/collect-hardware-report.sh
```

Expect clean tracked source and successful checks. Missing dependencies or a
broken link is a stop before publication. These commands check repository
consistency, not an installation. The
[collector](scripts/collect-hardware-report.sh) is a separate future hardware
observation, not a step executed to validate this guide. Its output can contain
addresses and raw tool errors despite its privacy footer: review all bytes
privately under the [evidence threat model](EVIDENCE-THREAT-MODEL.md) before
sharing, including logs and screenshots. Never publish keys, serials, MACs,
private addresses or account/image contents.

Freeze the exact public `arch-bootstrap` and `hyperlab-ansible` commits for a
campaign. Record this evidence repository's publishing revision separately;
it is not a third hardware input. Nitro requires clean installation, two boots,
correct storage, full intended host check/apply/apply (`changed=0`), isolation,
server/Machine lifecycle, real video/input/audio, reboot/cold-start/recovery and
reviewed evidence. Existing v2 release gates omit selected v1 requirements;
passing them alone cannot qualify v1. Full install acceptance, software remedies,
complete provenance/rights review, private-reporting activation and the future
ISO remain dependencies. See [security scope](FAQ.md#what-security-does-this-provide).

**Predator:** only after Nitro qualification, replay the **same automation pair**
with `predator-3070`, its real PCI/group/storage observations and separate display,
input and audio evidence. Do not use Nitro-specific checker assumptions to
certify it. Automation changes reopen Nitro. Both full-pipeline statuses stay
pending until the operator publishes the corresponding complete evidence.
