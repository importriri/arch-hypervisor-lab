# Hardware validation report

- Profile:
- Date (UTC):
- Laptop vendor/model:
- GPU and audio PCI IDs:
- BIOS/UEFI version (no serial):
- Kernel:
- arch-bootstrap commit:
- hyperlab-ansible commit:
- arch-hypervisor-lab commit:

## Release gates

- [ ] clean install completed
- [ ] two Hardened boots completed
- [ ] Secure Boot state checked
- [ ] expected Btrfs/LUKS mounts checked
- [ ] preflight selected expected profile
- [ ] first Ansible lab run completed
- [ ] immediate second run `changed=0`
- [ ] five persistent networks match
- [ ] isolation probes passed
- [ ] VFIO binds GPU and audio
- [ ] VM start/shutdown/handoff passed
- [ ] Looking Glass transport passed (when claimed)

## Evidence

Link logs, screenshots and any new problem writeups. Redact serial numbers, MAC
addresses, IP addresses, account names and guest secrets.
