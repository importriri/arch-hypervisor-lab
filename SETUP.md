# Reproduce and validate the pipeline

This is a three-stage system. Run each stage at a pinned commit and keep the
logs together; a compatibility claim without commit IDs is not reproducible.

```text
arch-bootstrap ──> privatestack-ansible ──> arch-hypervisor-lab evidence
base OS            host + VM transactions   architecture + compatibility
```

## 0. Record the candidate

Before touching a laptop, record the commit of all three repositories and the
intended hardware profile. Back up the machine and verify that the backup can
be read.

## 1. Install the encrypted base

Follow `arch-bootstrap/docs/release-gates.md`:

1. run its local verification;
2. run the default dry-run;
3. perform the clean install;
4. complete Secure Boot enrollment manually;
5. boot the Hardened entry twice and verify mounts/networking.

The optional second disk is a separate LUKS2 container mounted at
`/var/lib/libvirt/images`. Its No_COW contract is established with `chattr +C`
while empty, not with a misleading per-subvolume mount option.

## 2. Detect the laptop and assemble the host

```bash
# Fetch the published stage-2 automation from main.
git clone https://github.com/importriri/privatestack-ansible.git

# Enter the repository so every relative contract path resolves correctly.
cd privatestack-ansible

# Install the Ansible collections declared by the reviewed checkout.
ansible-galaxy collection install -r collections/requirements.yml

# Verify the exact checkout before it changes host state.
./verify.sh

# Detect the Nitro or Predator profile without changing the host.
ansible-playbook -K playbooks/preflight.yml

# Preview the complete laptop target and display the managed diff.
ansible-playbook -K playbooks/lab.yml --check --diff

# Apply the complete target: foundation, Sway and Looking Glass host transport.
ansible-playbook -K playbooks/lab.yml

# Prove immediate idempotence; this pass must report changed=0.
ansible-playbook -K playbooks/lab.yml
```

The preflight must select exactly one reviewed profile (`nitro-3060` or
`predator-3070`) and validate both the GPU and its HDMI-audio function. The
second real run must report `changed=0`.

Existing active libvirt networks are not silently replaced. When the role finds
persistent XML drift, stop attached guests and opt into the maintenance-window
restart it prints:

```bash
# Apply the same target while explicitly allowing changed network restarts.
ansible-playbook -K playbooks/lab.yml -e network_domains_restart_changed=true
```

## 3. Verify the five domains

The expected persistent networks are:

| Domain | Bridge | Subnet | Forwarding |
|---|---|---|---|
| clean | `virbr-clean` | `10.10.1.0/24` | NAT |
| dirty | `virbr-dirty` | `10.10.2.0/24` | NAT |
| dev | `virbr-dev` | `10.10.3.0/24` | NAT |
| lab | `virbr-lab` | `10.10.4.0/24` | none |
| services | `virbr-services` | `10.10.5.0/24` | NAT |

Verify persistent XML with `virsh net-dumpxml --inactive NAME`, not only the
currently active bridge. Test that guests cannot cross bridges, that the lab
cannot reach the internet, and that services are reachable only through
explicitly documented exposure rules.

## 4. Prepare and seal images

Images are explicit transactions. Public cloud bytes require a pinned vendor
checksum; Windows and installer-only distributions use the private workshop
handoff documented by PrivateStack.

```bash
# Preview acquisition and validation of the pinned official Arch cloud image.
ansible-playbook -K playbooks/image-prepare.yml --check --diff \
  -e image_factory_manifest=images/arch.yml

# Acquire, inspect and commit the image transaction.
ansible-playbook -K playbooks/image-prepare.yml \
  -e image_factory_manifest=images/arch.yml

# Revalidate the sealed base without replacing it.
ansible-playbook -K playbooks/image-validate.yml \
  -e image_factory_manifest=images/arch.yml
```

Do not put image files, Windows accounts, signed guest installers or private
workshop receipts in Git.

## 5. Exercise explicit VM lifecycle

`lab.yml` never creates or destroys workloads. Use one checked-in spec and keep
create, start, shutdown, reset and destroy as separate reviewed transactions.
For a cloud-init Linux guest, creation also needs at least one safe host-local
SSH public key:

```bash
# Preview the disposable Arch guest transaction and its complete managed diff.
ansible-playbook -K playbooks/vm-create.yml --check --diff \
  -e guest_spec=vm-specs/arch-bootstrap-gate.yml \
  -e '{"guest_cloud_init_ssh_public_keys":["ssh-ed25519 AAAA..."]}'

# Create the guest from its sealed base and private runtime identity.
ansible-playbook -K playbooks/vm-create.yml \
  -e guest_spec=vm-specs/arch-bootstrap-gate.yml \
  -e '{"guest_cloud_init_ssh_public_keys":["ssh-ed25519 AAAA..."]}'

# Start only after live capacity and ownership checks pass.
ansible-playbook -K playbooks/vm-start.yml \
  -e guest_spec=vm-specs/arch-bootstrap-gate.yml

# Request a Guest Agent shutdown and wait for the managed state transition.
ansible-playbook -K playbooks/vm-shutdown.yml \
  -e guest_spec=vm-specs/arch-bootstrap-gate.yml
```

Forced stop, reset and destroy require the exact confirmation printed by their
check-mode refusal. Permanent and disposable specs use the same lifecycle
engine; disposable means a named resettable overlay, not a one-session VM.

## 6. Validate VFIO and GPU handoff

Boot the managed VFIO entry and verify that the selected profile's two PCI IDs
are bound to `vfio-pci`. Start one GPU VM at a time. A transition from lower to
higher trust requires a host reboot; `services` never participates in GPU
rotation.

## 7. Validate the integrated cockpit

The `playbooks/lab.yml` run in step 2 already installed Sway, then the host-side
Looking Glass transport. `playbooks/desktop.yml` and
`playbooks/looking-glass.yml` are narrow maintenance entrypoints, not extra
installation steps. The libvirt SPICE endpoint for the Looking Glass guest
must be fixed at `127.0.0.1:5900`, matching the client configuration.
`autoport='yes'` is not a valid contract when the client is pinned to port 5900.

The Windows Looking Glass host and virtual display remain manual. Use the log
assertions in `configs/looking-glass.md`; a visible SPICE fallback is not proof
that shared-memory capture works.

## 8. Register services before creation

A service reserves identity, static lease and inactive RAM before its VM is
created. Application installation runs inside the service guest, not on the
hypervisor:

```bash
# Preview registration and its identity, lease and memory reservations.
ansible-playbook -K playbooks/service-register.yml --check --diff \
  -e service_spec=service-specs/svc-jellyfin.yml

# Commit the reviewed service registration.
ansible-playbook -K playbooks/service-register.yml \
  -e service_spec=service-specs/svc-jellyfin.yml

# Create the registered service VM with a host-local public key.
ansible-playbook -K playbooks/vm-create.yml \
  -e guest_spec=vm-specs/svc-jellyfin.yml \
  -e '{"guest_cloud_init_ssh_public_keys":["ssh-ed25519 AAAA..."]}'

# Configure Jellyfin inside the service guest, never on the hypervisor.
ansible-playbook -K playbooks/jellyfin.yml
```

Backup and restore stay offline transactions; LAN exposure exists only while a
matching registered service VM is active.

## 9. Produce compatibility evidence

From this repository:

```bash
# Collect a sanitized Nitro report; change only the reviewed profile and date.
sudo scripts/collect-hardware-report.sh hardware/reports/nitro-3060-YYYYMMDD.md

# Validate documentation links, configuration examples and compatibility states.
python scripts/verify_repo.py
```

Review the report before publishing. The script intentionally excludes serial
numbers, MAC addresses and IP addresses. Complete
[`hardware/report-template.md`](hardware/report-template.md), link reviewed
logs, screenshots and writeups, and only then change `full_pipeline` from
`pipeline-pending` to `pipeline-verified` in
`hardware/compatibility.yml`.
