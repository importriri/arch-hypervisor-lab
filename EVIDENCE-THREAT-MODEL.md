# Evidence threat model

What this repository's evidence can establish, what it trusts, and how
private data could leak through it. It covers the evidence only: the
documents, the two scripts, the CI workflow and what is published here.

The lab itself has its own threat models, which this page does not
restate or extend: the
[stage-2 threat model](https://github.com/importriri/hyperlab-ansible/blob/main/docs/threat-model.md)
for the host, networks, VFIO and Machines, and the
[bootstrap threat model](https://github.com/importriri/arch-bootstrap/blob/main/docs/threat-model.md)
for the encrypted base. The lab is a compartmentalization on KVM. It is not
Qubes OS and does not provide Qubes OS security properties, and nothing
published here can show that it does.

## What this repository can establish

Four kinds of statement, each with its own limit:

1. **Source checks.** `python scripts/verify_repo.py` checks that relative
   Markdown links resolve, that `hardware/compatibility.yml` names exactly
   the two profiles with two VFIO IDs each and a known `full_pipeline`
   state, and a set of fixed properties of the guides and configuration
   examples. `bash -n` and ShellCheck check the scripts. These say the tree
   is consistent with itself. They say nothing about a machine.
2. **Explicit claim scopes.** `hardware/compatibility.yml` separates
   `component-verified` (one named subsystem has repeatable evidence) from
   `pipeline-verified` (every release gate passed at pinned commits). A
   statement holds at the scope it names and no wider.
3. **Named-machine observations bound to two automation commits.** A
   hardware result names one profile (`nitro-3060` or `predator-3070`) and
   the exact 40-character `arch-bootstrap` and `hyperlab-ansible` commits
   that ran on it. The `arch-hypervisor-lab` commit that publishes the
   result is a publication record, not a third input: it may advance when
   reviewed Nitro evidence is added before a Predator replay.
4. **Reviewed sanitized evidence.** What is committed here is what the
   maintainer reviewed and chose to publish: scalar values, PCI IDs,
   versions, digests, short excerpts and write-ups. Raw material stays
   private.

Today both profiles are `pipeline-pending`. The component results recorded
for them are history at their own scope, not a pipeline pass.

## Who and what is trusted

- **The maintainer** named in [`AUTHORS.md`](AUTHORS.md) is the only
  publication authority. Only the maintainer merges into `main`, changes a
  compatibility status or accepts evidence. That review is a human
  judgement, and every claim here rests on it.
- **The operator of a named machine** (today the maintainer) runs the
  automation and the collector, keeps the raw output privately and decides
  what to submit. The machine is trusted to report its own state: a
  compromised host can print anything, and no document here can detect it.
- **Contributors** are not trusted. A pull request, an issue or a submitted
  report is input to review, never evidence by arriving.
- **Code and tool inputs** are trusted as far as they run: the two scripts
  here, Bash and coreutils, `lscpu`, `lspci` and `virsh` on the collecting
  machine, Python with PyYAML for the verifier, and for CI the GitHub
  Actions runner, `actions/checkout@v4` and the packages it installs. The
  sibling repositories are trusted only at the commits a result names.
- **GitHub** stores and serves the repository and runs CI. It is trusted
  for availability and for showing what was pushed, not for any statement
  about hardware.

## Bytes are not observations

A SHA-256 digest binds bytes: anyone can recompute it and see that a file
is the one that was hashed. It says nothing about whether those bytes
describe something that happened.

The release receipt sealed by `hyperlab-ansible`'s
`tools/release_acceptance.py` binds the plan and evidence digests, the two
commits, the storage topology and the ordered gate IDs. It is generated on
the operator's machine from values the operator recorded. Nothing in it is
witnessed by anyone else, so it does not authenticate an observation: a
well-formed receipt can be produced for a run that never took place. A
receipt is accepted here only together with the maintainer's review of the
evidence behind it, and the record says so.

## What cannot be established here

- **A green CI run** checks this tree on a hosted Ubuntu runner. It runs no
  laptop, no collector and no hardware campaign, so it is never a pipeline
  pass or a compatibility claim.
- **A configuration example** under `configs/` shows a reviewed shape. It
  does not show that it ran, or that it ran on a given machine.
- **One component result** stays `component-verified`. It does not raise
  `full_pipeline`, and it does not carry over to another subsystem.
- **A pending template.** `hardware/report-template.md` and its unchecked
  boxes are a form to fill in, not a result.
- **Another laptop's compatibility.** A Nitro result says nothing about the
  Predator, and neither says anything about a third machine, even with the
  same GPU family. Each profile is proved on its own hardware.
- **A different automation pair.** A result at other `arch-bootstrap` or
  `hyperlab-ansible` commits is a different candidate. A Predator replay at
  a pair other than the one that passed Nitro is not a replay; an
  automation change it needs reopens Nitro.
- **A script exiting zero.** Neither the collector nor the verifier judges
  privacy, authenticity or meaning (see below).

## What the collector actually reads

`scripts/collect-hardware-report.sh` is named as a sanitized report, but
its output is only as private as the machine it reads. Reading the script:

- it prints DMI strings (`sys_vendor`, `product_name`, `product_version`,
  `bios_version`), which are free text written by the vendor;
- it prints the kernel release, a UTC timestamp of the run and four
  `lscpu` fields (architecture, CPU model, virtualization, CPU count);
- it prints `lspci -Dnnk` lines around display and audio functions,
  including subsystem names and kernel modules, and up to three following
  lines that may belong to other devices;
- it prints `stat` output for `/dev/kvm` and `/dev/kvmfr0` with owner and
  group: these are the names of local users and groups;
- it prints `virsh net-list --all` with its error output, so any libvirt
  diagnostic reaches the report, including connection URIs and socket
  paths; network names are whatever the host defined;
- what `virsh` shows depends on the user running the script, because root
  and a normal user can reach different libvirt connections;
- a missing command or an unreadable file becomes `unavailable`, an empty
  section or a short note, and the report is still written: the script
  prints `wrote` and exits zero with a report that has gaps;
- the closing privacy sentence is fixed text, printed every time. It is
  not the result of a check;
- with no argument it writes `hardware-report.md` in the current directory,
  which is inside the checkout when run from its root.

It does omit serial numbers, MAC addresses and IP addresses by not reading
them. That is the whole of its sanitizing. Any other private string on the
machine can still reach the output.

## Manual review before publication

Every artifact is reviewed by a person before it is committed. No step is
automatic, and no tool here anonymizes anything.

- **Raw material stays private and outside Git.** Write collector output,
  logs, transcripts, screenshots and recordings to a private directory
  outside every checkout, even where an older example in this repository
  shows a path inside it. Never put raw material in a fork, a gist, an
  issue attachment or a pull request.
- **Text.** Read every line. Remove or replace user and group names, host
  names, home and runtime paths, network names that identify a person or
  place, IP and MAC addresses, serials, UUIDs, keys, fingerprints, tokens
  and passwords. Keep only what the claim needs.
- **Image metadata.** Inspect and remove embedded metadata (for example
  EXIF, XMP or PNG text chunks) before publishing an image. Removing
  metadata does not establish who made the image or that it may be
  published.
- **Every text-bearing frame.** In a screenshot, look at every visible
  word: window titles, terminal prompts, notifications, panels, file
  dialogs and browser tabs. In a recording, review every frame that shows
  text, not a sample. A clean transcript does not clear the frames, and a
  clean frame does not clear the others.
- **Meaning.** Check that the artifact shows what the claim says, on the
  named machine, at the named pair, and that nothing failed out of view.

## A leak that is already public

Once a private value has been pushed, it may already be in clones, forks,
mirrors, caches and archives. A later commit that removes it does not make
it private again, and this repository does not promise to rewrite its
history.

Report it privately as [`SECURITY.md`](SECURITY.md) says, naming the path,
the commit and the kind of value, never the value. The maintainer then
assesses what was exposed and, where the value is a credential or key,
revokes and replaces it wherever it is valid. Evidence is not deleted
silently: a correction records what changed and why, without repeating the
value, so the published record stays truthful about its own history.

## What the verifier does not certify

`python scripts/verify_repo.py` reads the tree for the structural checks
above. It does not read a report for private values, does not look at
images, and does not check that a result happened. A report that contains
an account name, or a receipt for a run that never took place, passes it.
It is a consistency check, not a privacy or authenticity certificate.

## Current stage-2 boundaries

Evidence here describes the lab at the boundaries the
[stage-2 roadmap](https://github.com/importriri/hyperlab-ansible/blob/main/docs/roadmap.md)
states today. Where an older guide in this repository says otherwise, the
roadmap is current:

- a `services` Machine may be GPU-capable through a reviewed handoff
  profile; the GPU ladder still orders every use within one host boot;
- Hyprland is the preferred host session; Sway is a first-class session
  and the recovery compositor.

A protection is described as active only when it is observed active on
the named machine. Code or a decision record is not enough. Today the
roadmap records that the shared QEMU AppArmor profile is built and starts
in complain mode, that per-Machine QEMU identities are built behind a
switch that is off, and that neither is proved; that driver Machines for
the network card and the USB controller are proposed; and that measured
boot is proposed, with its image builder behind a switch that is off.
Evidence here does not claim any of them as active.

## Counterexamples

None of these is safe or accepted because a script exits zero:

| Input | Why it is not accepted |
|---|---|
| Raw collector output containing an account name | `stat` printed the owner; the collector wrote it and exited zero, and the verifier would pass it. Review removes it, and raw output never enters Git. |
| A screenshot nobody reviewed | Metadata and every visible word are unchecked; a terminal prompt or a notification may carry a user or host name. |
| A forged receipt | Its digests verify its own bytes; nothing in it shows that the run happened. |
| A green CI run with no hardware campaign | CI ran no laptop; it is a source check, never a pipeline pass. |
| A Predator report at a different automation pair | It is a different candidate, not a replay of the Nitro pair. |

A private reporting form that has not been enabled is not a working route
either. Until a repository administrator enables it and checks it from a
reporter's side, private reporting remains an open release prerequisite.
