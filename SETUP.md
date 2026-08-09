# Nitro setup guide

This is the short path through the three repositories. The detailed failure and
release notes stay in their owning repository.

```text
Arch ISO
  -> arch-bootstrap
  -> hyperlab-ansible
  -> images and explicit workloads
  -> VFIO / Looking Glass
  -> hardware evidence here
```

Use pinned commits for a release run. Keep the three commit IDs with the final
evidence.

## 1. Install the base host

From the Arch installer environment, clone the stage-1 repository and run its
checks before touching disk state:

```bash
git clone https://github.com/importriri/arch-bootstrap.git
cd arch-bootstrap
sudo bash verify.sh
sudo bash bootstrap
```

`bootstrap` is dry-run by default. Review the selected disks and printed plan.
Only then run the real installation:

```bash
sudo env DRY_RUN=0 bash bootstrap
```

The result is an encrypted Arch host with the stage-2 storage contract already
written. Complete Secure Boot enrollment and first-boot networking exactly as
described by `arch-bootstrap` before continuing.

## 2. Build the Nitro host

```bash
git clone https://github.com/importriri/hyperlab-ansible.git
cd hyperlab-ansible
ansible-galaxy collection install -r collections/requirements.yml
./verify.sh
ansible-playbook -K playbooks/preflight.yml
ansible-playbook -K playbooks/lab.yml --check --diff
ansible-playbook -K playbooks/lab.yml
ansible-playbook -K playbooks/lab.yml
```

`preflight.yml` must select `nitro-3060`. The last real apply must report
`changed=0`.

The `playbooks/lab.yml` run in step 2 already installed Sway, then the host-side
Looking Glass transport. `playbooks/desktop.yml` and
`playbooks/looking-glass.yml` are narrow maintenance entrypoints, not extra
installation steps. The complete target owns the headless foundation and local
cockpit; it does not create private workloads.

## 3. Check the trust domains

The persistent networks are:

| Domain | Subnet | Forwarding |
| --- | --- | --- |
| clean | `10.10.1.0/24` | NAT |
| dirty | `10.10.2.0/24` | NAT |
| dev | `10.10.3.0/24` | NAT |
| lab | `10.10.4.0/24` | none |
| services | `10.10.5.0/24` | NAT |

The isolated lab must have no internet route. Cross-domain forwarding stays
blocked unless a reviewed service exposure says otherwise.

## 4. Prepare and seal images

Public images use `images/*.yml` manifests with pinned provenance. Windows and
installer-only distributions use the workshop path instead of committing private
media to Git.

For the Arch base:

```bash
ansible-playbook -K playbooks/image-prepare.yml --check --diff \
  -e image_factory_manifest=images/arch.yml
ansible-playbook -K playbooks/image-prepare.yml \
  -e image_factory_manifest=images/arch.yml
ansible-playbook -K playbooks/image-validate.yml \
  -e image_factory_manifest=images/arch.yml
```

For Windows, follow `hyperlab-ansible/docs/windows-image-workshop.md`. Keep the
Windows media, accounts, signed guest binaries and workshop receipts local.

## 5. Exercise explicit VM lifecycle

Use the checked-in VM spec that matches the workload. Creation, start, shutdown,
reset and destruction remain separate transactions. A rerun of the host target
must never imply a workload decision.

For a standard Arch guest, preview, creation, start and shutdown remain distinct:

```bash
ansible-playbook -K playbooks/vm-create.yml --check --diff \
  -e guest_spec=vm-specs/arch-dev.yml \
  -e '{"guest_cloud_init_ssh_public_keys":["ssh-ed25519 AAAA..."]}'
ansible-playbook -K playbooks/vm-create.yml \
  -e guest_spec=vm-specs/arch-dev.yml \
  -e '{"guest_cloud_init_ssh_public_keys":["ssh-ed25519 AAAA..."]}'
ansible-playbook -K playbooks/vm-start.yml \
  -e guest_spec=vm-specs/arch-dev.yml
ansible-playbook -K playbooks/vm-shutdown.yml \
  -e guest_spec=vm-specs/arch-dev.yml
```

Forced stop, reset and destroy require the exact confirmation printed by their
check-mode refusal.

The reference Nitro set is:

- `win11clean-valley`: trusted Windows/VFIO baseline;
- `arch-dev`: standard Arch development/recovery workstation;
- `arch-dev-vfio`: accelerated Arch candidate;
- `win11dirty-disposable`: lower-trust disposable Windows/VFIO workload;
- service VMs registered under `service-specs/`, with Jellyfin as the reference
  service.

For Windows, build and seal the clean master first, then derive workload variants
from that reviewed base rather than reinstalling Windows for each VM. The exact
workshop boundary is in `hyperlab-ansible/docs/windows-image-workshop.md`.

For `arch-dev-vfio`, follow
`hyperlab-ansible/docs/nitro-arch-dev-vfio-campaign.md`; its resource profile,
SSH key input and hardware gates are intentionally more specific than a generic
VM-create example.

## 6. Use the dGPU through VFIO

Boot the managed VFIO host entry. The RTX 3060 display and HDMI-audio functions
must both be bound to `vfio-pci` before a GPU workload starts. Only one workload
VM owns the dGPU at a time. `services` never receives it.

A move from a lower-trust GPU workload to a higher-trust one requires the host
reboot defined by the GPU handoff policy.

## 7. Looking Glass

### Windows guests

Install the signed Looking Glass host application and the reviewed virtual
display inside Windows. These are guest-side manual steps. The physical Arch host
uses the kvmfr transport configured by `hyperlab-ansible`.

Do not treat a visible SPICE desktop as proof of Looking Glass shared-memory
capture. Keep SPICE for recovery/input plumbing and verify the actual client and
kvmfr path.

### Linux VFIO guest

The experimental Linux sender is manual. Nitro has already produced real
1920×1080 frames through Hyprland, XDPH/PipeWire, kvmfr and the physical-host
Looking Glass client. Fresh-session persistence, deterministic portal source
selection and keyboard/pointer return still need their final gates.

## 8. Register services before creation

A service reserves identity, static lease and inactive RAM before its VM is
created. Application installation runs inside the service guest, not on the
hypervisor:

```bash
ansible-playbook -K playbooks/service-register.yml --check --diff \
  -e service_spec=service-specs/svc-jellyfin.yml
ansible-playbook -K playbooks/service-register.yml \
  -e service_spec=service-specs/svc-jellyfin.yml
ansible-playbook -K playbooks/vm-create.yml --check --diff \
  -e guest_spec=vm-specs/svc-jellyfin.yml \
  -e '{"guest_cloud_init_ssh_public_keys":["ssh-ed25519 AAAA..."]}'
ansible-playbook -K playbooks/vm-create.yml \
  -e guest_spec=vm-specs/svc-jellyfin.yml \
  -e '{"guest_cloud_init_ssh_public_keys":["ssh-ed25519 AAAA..."]}'
ansible-playbook -K playbooks/jellyfin.yml --check --diff
ansible-playbook -K playbooks/jellyfin.yml
```

Backup and restore remain offline transactions. LAN exposure exists only while
the matching registered service VM is active.

## 9. Prove the result

Run the repository verifiers again and collect a sanitized hardware report from
this repository:

```bash
sudo scripts/collect-hardware-report.sh hardware/reports/nitro-3060-YYYYMMDD.md
python scripts/verify_repo.py
```

Review every report before publishing it. Serial numbers, MAC addresses, private
IP data, credentials, image contents and account details do not belong in the
public evidence.

A Nitro release is complete only when the recorded commit IDs, second-pass
idempotence and named hardware gates agree.

## What counts as a ready Nitro lab

Before calling the machine ready, require all of these:

- `preflight.yml` selects `nitro-3060`;
- the host target converges twice and the second apply reports `changed=0`;
- all five libvirt trust domains exist with `lab` isolated;
- the dGPU is owned by `vfio-pci` before a GPU workload starts;
- at least one standard guest and the declared VFIO workload path pass their
  lifecycle gates;
- Looking Glass is proven through its actual kvmfr path rather than a plausible
  recovery display;
- the final evidence names the exact repository commits used on hardware.

Open Linux sender persistence/input items remain release blockers until their
runbook gates are closed; the guide does not silently promote them to complete.

## Predator

Predator uses the same pipeline, not a separate set of instructions. Its profile
is `predator-3070`. Run it only after the Nitro release candidate is frozen, and
use the exact same three repository commits. Differences that require code
changes reopen Nitro before the Predator result can be published.
