# Contributing

`arch-hypervisor-lab` records what the lab is and what has actually been
proven on hardware. A contribution here is a correction, a write-up or
evidence, and each is reviewed first for what it might expose or overstate.

Security problems, including private data published by mistake, are not
contributions: report them privately as [`SECURITY.md`](SECURITY.md) says,
never in an issue or a pull request. A compatibility failure is welcome as
a normal issue, with sanitized output only.

## Repository map

| Path | What it is |
|---|---|
| `README.md`, `SETUP.md` | The overview and the operator path through the three repositories |
| `configs/` | Boot, network, libvirt and display contracts, with sanitized examples |
| `hardware/README.md` | The compatibility policy and the promotion checklist |
| `hardware/compatibility.yml` | The machine-readable status of each named profile |
| `hardware/report-template.md` | The form a hardware report starts from; empty, not a result |
| `problems/` | Failure write-ups, indexed in `problems/README.md` |
| `scripts/collect-hardware-report.sh` | The hardware collector; read [what it actually prints](EVIDENCE-THREAT-MODEL.md#what-the-collector-actually-reads) before using it |
| `scripts/verify_repo.py` | The repository consistency checks |
| `.github/workflows/ci.yml` | CI: the three checks below |
| `SECURITY.md` | Private reporting |
| `EVIDENCE-THREAT-MODEL.md` | What the evidence here can and cannot establish, and how it is reviewed |
| `PROVENANCE-AUDIT.md`, `file-inventory.tsv` | File origins and unresolved rights questions, at one input commit |

The installer and the automation are in
[`arch-bootstrap`](https://github.com/importriri/arch-bootstrap) and
[`hyperlab-ansible`](https://github.com/importriri/hyperlab-ansible);
changes to their behaviour belong there.

## Set up

The checks need Bash, Python 3 with PyYAML, and ShellCheck. On Arch Linux:

```bash
# Install the check toolchain (Arch package names).
sudo pacman -S --needed python python-yaml shellcheck
```

CI installs PyYAML with `pip install pyyaml` and ShellCheck with
`apt-get` on its Ubuntu runner.

## Verify

Run the same three checks CI runs, from the repository root, as your
normal user:

```bash
# Links, the compatibility file and the documented contracts.
python scripts/verify_repo.py
# Bash syntax of every script.
bash -n scripts/*.sh
# ShellCheck of every script.
shellcheck scripts/*.sh
```

The first must print `repository verification: OK`; the other two print
nothing on success. None of them needs root, runs the collector, reads
hardware or contacts libvirt. Passing them means the tree is consistent,
not that anything works on a laptop.

## Make a change

- **Small and reviewable.** One concern per pull request and per commit,
  each commit keeping the three checks green. Say why in the message.
- **Keep the documents true.** A correction changes every page that states
  the same fact, in the same commit. Do not state more than the evidence
  shows, and do not weaken a check in `scripts/verify_repo.py` to make a
  change pass.
- **Write it up.** A failure that taught something gets a note in
  `problems/`, in the shape of the existing ones: the symptom, the cause,
  the fix and the proof that it is fixed (the commands and what they
  showed), and a line in `problems/README.md`.
- **Commit messages** follow the recent history: an imperative subject
  with a capital first letter, no type prefix, no final period, at most 72
  characters; the body says why.

Open a pull request against `main`. Only the maintainer merges and
publishes.

## Contributing evidence

Evidence is reviewed under
[`EVIDENCE-THREAT-MODEL.md`](EVIDENCE-THREAT-MODEL.md). In short:

- **Minimize.** Submit only what the claim needs: profile, PCI IDs,
  versions, the two automation commits, digests and a short reviewed
  summary. Raw logs, collector output, transcripts, disk or guest image
  contents and anything from a home directory stay private, outside Git.
- **Review by hand.** Read every line of text, remove image metadata and
  check every visible word of every screenshot and every text-bearing frame
  of a recording. No tool here anonymizes anything, and a passing check is
  not a review.
- **Rights and provenance.** Submit only what you made or may publish
  under the [MIT licence](LICENSE). Say where anything else comes from
  (another project's output, a quotation, a screenshot of someone else's
  software), with its source, revision and licence, and keep its notices.
  A submission whose origin cannot be stated is not accepted.
  [`PROVENANCE-AUDIT.md`](PROVENANCE-AUDIT.md) covers the files present at
  its input commit only; it does not clear new material.

By contributing you confirm that you have the right to submit your work
under the MIT licence. There is no contributor licence agreement and no
sign-off line.

## Hardware results

### Promoting a named profile

A profile moves from `pipeline-pending` to `pipeline-verified` only when
every item of the promotion checklist in
[`hardware/README.md`](hardware/README.md#promotion-to-pipeline-verified)
passed on that machine at pinned commits, and the maintainer reviewed the
evidence. A new laptop starts as a candidate profile built from its own
numeric PCI IDs and IOMMU layout, never copied from a profile with the same
GPU name, and stays `pipeline-pending` until then.

Both full pipelines are pending today: `nitro-3060` and `predator-3070`
are `pipeline-pending` in
[`hardware/compatibility.yml`](hardware/compatibility.yml).

### The automation pair

A result names the exact 40-character commits of the two automation
inputs, `arch-bootstrap` and `hyperlab-ansible`, that ran on the machine.
That pair is the identity of the result.

- The Predator replay uses exactly the pair that passed Nitro. A result at
  any other pair is a different candidate, not a replay. If the Predator
  needs an automation change, Nitro is reopened at the new pair before
  either result is published.
- The `arch-hypervisor-lab` commit that publishes a report records its
  publication. It is not a third input: it may advance when reviewed Nitro
  evidence is added before the Predator report.

### Nitro and Predator stay separate

Each machine has its own report and its own status. A Nitro result is
never copied to, or inferred for, the Predator, and the reverse. A
component result stays at its component.

### What is not a release gate list

The release order checked in to `hyperlab-ansible`
(`release/acceptance.v2.yml`) was written before the current v1 scope and
does not cover its additions; what replaces it is not decided. Do not
treat that list, or the boxes in `hardware/report-template.md`, as the v1
qualification.

### Not implemented

Some pieces are proposed or planned and do not exist as working steps.
Do not describe them as available:

- there is no validator for campaign summaries in this repository; review
  of submitted evidence is manual;
- the installer image is proposed in `arch-bootstrap` and not built;
- the GPU lease is proposed in `hyperlab-ansible` and not built;
- later hardening (enforced QEMU confinement, driver Machines for the
  network card and USB controller, measured boot) is built only in part,
  switched off or proposed, as the
  [stage-2 roadmap](https://github.com/importriri/hyperlab-ansible/blob/main/docs/roadmap.md)
  records.
