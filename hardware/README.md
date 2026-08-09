# Hardware compatibility policy

This matrix separates **a component worked once** from **the public pipeline is
reproducible on this laptop**. `compatibility.yml` is machine-readable; reports
and links supply the evidence.

## Promotion to `pipeline-verified`

A profile needs all of the following at pinned commits:

- clean `arch-bootstrap` install and two successful boots;
- Secure Boot state recorded;
- correct root and optional VM-disk mounts;
- `hyperlab-ansible` preflight selects the expected profile;
- first lab run succeeds and immediate second run reports `changed=0`;
- five persistent libvirt networks and isolation probes pass;
- VFIO binds both expected PCI functions;
- at least one full guest start/shutdown/handoff cycle;
- host-side Looking Glass convergence and one real shared-memory guest capture
  cycle (a visible SPICE fallback does not count);
- sanitized report plus logs/screenshots linked from the profile.

## Keeping the two files in step

`compatibility.yml` records the IDs that were observed. `hyperlab-ansible`
carries the IDs it binds. They used to be able to drift apart for months, so
`tests/cross_repo_contract.py` over there now compares them:

```bash
cd ../hyperlab-ansible
python tests/cross_repo_contract.py ../arch-hypervisor-lab
```

Without a checkout of this repository it skips and says so rather than
reporting a pass. The CI job that exists to compare the pair checks out both
and is not allowed to skip.

The status columns above live here and nowhere else. A repository cannot
certify itself, which is why the ansible profile carries no status field and
the check refuses one that reappears.

## Adding a friend's laptop

Create a candidate profile only after collecting numeric PCI IDs and IOMMU
layout. Never copy an existing profile based only on the GPU marketing name.
Run the full checklist, keep failures as writeups, and use `pipeline-pending`
until every gate passes.

The collector intentionally excludes serial numbers, MAC addresses and IP
addresses. Start from [`report-template.md`](report-template.md) and review every
report manually before publishing it.
