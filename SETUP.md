# Reproduce and validate the pipeline

This is a three-stage system. Run each stage at a pinned commit and keep the
logs together; a compatibility claim without commit IDs is not reproducible.

```text
arch-bootstrap ──> privatestack-ansible ──> arch-hypervisor-lab evidence
base OS            host configuration       architecture + compatibility
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
git clone https://github.com/importriri/privatestack-ansible.git
cd privatestack-ansible
ansible-galaxy collection install -r collections/requirements.yml

ansible-playbook playbooks/preflight.yml
ansible-playbook playbooks/lab.yml --check --diff
ansible-playbook playbooks/lab.yml
ansible-playbook playbooks/lab.yml
```

The preflight must select exactly one reviewed profile (`nitro-3060` or
`predator-3070`) and validate both the GPU and its HDMI-audio function. The
second real run must report `changed=0`.

Existing active libvirt networks are not silently replaced. When the role finds
persistent XML drift, stop attached guests and opt into the maintenance-window
restart it prints:

```bash
ansible-playbook playbooks/lab.yml -e network_domains_restart_changed=true
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

## 4. Validate VFIO and GPU handoff

Boot the managed VFIO entry and verify that the selected profile's two PCI IDs
are bound to `vfio-pci`. Start one GPU VM at a time. A transition from lower to
higher trust requires a host reboot; `services` never participates in GPU
rotation.

## 5. Add the optional cockpit

Run `playbooks/desktop.yml` before `playbooks/looking-glass.yml`. The libvirt
SPICE endpoint for the Looking Glass guest must be fixed at
`127.0.0.1:5900`, matching the client configuration. `autoport='yes'` is not a
valid contract when the client is pinned to port 5900.

The Windows Looking Glass host and virtual display remain manual. Use the log
assertions in `configs/looking-glass.md`; a visible SPICE fallback is not proof
that shared-memory capture works.

## 6. Produce compatibility evidence

From this repository:

```bash
sudo scripts/collect-hardware-report.sh hardware/reports/<profile>-<date>.md
python scripts/verify_repo.py
```

Review the report before publishing. The script intentionally excludes serial
numbers, MAC addresses and IP addresses. Complete
`hardware/report-template.md`, link logs/screenshots/writeups, and only then
change `full_pipeline` from `pending` to `verified` in
`hardware/compatibility.yml`.
