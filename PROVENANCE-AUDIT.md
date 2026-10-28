# Provenance audit: file origins and third-party licences

This audit records evidence and unknowns at input commit
`5abfddceb2d864aeead76bff35fa4d17c24806e2`: 27 tracked paths. Primary
records were retrieved or attempted on **2026-10-27 at 23:40 UTC**. The
accompanying [`file-inventory.tsv`](file-inventory.tsv) accounts for the
input bytes.

This repository contains documents, configuration fragments and two scripts.
It contains neither an installed lab nor a Windows workshop image. The root
[`LICENSE`](LICENSE) declares MIT and [`AUTHORS.md`](AUTHORS.md) names the
maintainer. Those statements do not establish each file's origin or grant
rights to the software described by the guides. **Provenance remains pending
for 26 paths.** The remaining path is the standard licence declaration
itself, not a finding that all contents are cleared.

## 1. Inventory boundary and method

The inventory has one row for each historical `git ls-files -z` path at the
input commit, including `.github/workflows/ci.yml`, all four boot entries
and the libvirt fragment. Its path set, modes and digests were checked
against Git objects independently of this report's counts. Temporary copies
with a missing fragment, duplicate path or wrong digest must be rejected;
these checks establish inventory integrity, not rights. From any clone that
contains the input commit, this prints nothing but the final line when the
inventory's paths, modes and digests match the input blobs:

```sh
git ls-tree -r 5abfddceb2d864aeead76bff35fa4d17c24806e2 |
  while read -r mode type oid path; do
    printf '%s\t%s\t%s\n' "$path" "$mode" "$(git cat-file blob "$oid" | sha256sum | cut -d' ' -f1)"
  done | diff - <(tail -n +2 file-inventory.tsv | cut -f1,2,4) && echo match
```

| Column | Meaning |
| --- | --- |
| `path` | exact input path |
| `mode` | Git mode, `100644` or `100755` |
| `file_type` | `regular`; no input symlinks or submodules |
| `sha256` | SHA-256 of the input blob, not the current working copy |
| `kind` | `doc`, `config`, `code`, `data`, `template` or `legal` |
| `origin` | what this path itself shows about its source; no ownership inferred from history |
| `evidence` | introducing commit/date and observations for this path |
| `relationship` | shared examples, quotations, reported output or external references |
| `licence` | declared licence and the limits of applying it to the bytes |
| `status` | `unresolved` or `documented-declaration` |
| `unresolved` | per-path `Pnn` case and any component `Un` cases below, or `-` |

Introduction commits record when bytes entered this history. They do not
prove who created them. The Vfio entry even contains a creation date earlier
than that history. Every input file was read as UTF-8 text, including
comments, fenced examples, XML comments and notices. No embedded image,
font, binary, encoded asset or data URI was found. Text diagrams and factual
device IDs are present. No file identifies an external generator; references
to generated configurations or collected reports do not establish that the
tracked file itself was generated.

Versioned Looking Glass examples were compared structurally with the XML
argument values and the udev rule. The standard MIT wording and the forum
quotation were also compared with the records cited below. This is a limited
source comparison, not an exhaustive similarity search. Absence of a match
is not evidence of independent authorship. Each `Pnn` case means the path
still needs its own source/derivation account, including any borrowed
comments, commands or factual-data formatting.

### New audit outputs

`PROVENANCE-AUDIT.md` and `file-inventory.tsv` are new records, absent at the
input commit. They are accounted for here, outside the input inventory,
so the inventory does not hash itself. `README.md` gains only the link to
this report; its input digest intentionally describes the earlier bytes.
The new analysis and inventory do not relicense the material they identify.
A later inventory can hash these outputs at their containing commit. This
report lists candidate notices for review; it is not the notices file of any
distribution.

## 2. Repository examples, quotations and notices

### Configuration examples needing provenance

**U1 — `configs/libvirt/looking-glass.xml`.** The four QEMU argument elements
match the JSON-style example in Looking Glass's
[`doc/ivshmem_kvmfr.rst`](https://github.com/gnif/LookingGlass/blob/0140a3f6fb616c5636d6c430eb71b8a7d5338e39/doc/ivshmem_kvmfr.rst)
at the pinned commit and at B7 (`27fe47cbe2a3a8da986d310ab866f0b646ed68f5`),
after changing the memory size from 32 to 64 MiB. The commented shmem and
tmpfiles fallback matches
[`doc/ivshmem_shm.rst`](https://github.com/gnif/LookingGlass/blob/0140a3f6fb616c5636d6c430eb71b8a7d5338e39/doc/ivshmem_shm.rst)
after changing size and the user placeholder. This establishes similarity,
not the source actually used. The namespace, other device fragments and
surrounding comments also lack a derivation record.

**U2 — `problems/kvmfr-device-permissions.md`.** Its udev rule and filename
match the pinned kvmfr documentation after adding the QEMU owner. The B7
rule differs: it names a user owner and lacks the active-seat tag. A B7
link alone therefore does not identify the version of this example. The
note gives no source for its rule.

**Supported Looking Glass notice.** The documentation configuration
[`doc/conf.py`](https://github.com/gnif/LookingGlass/blob/0140a3f6fb616c5636d6c430eb71b8a7d5338e39/doc/conf.py)
names “2024, Looking Glass team” and GPLv2. Its
[`LICENSE`](https://github.com/gnif/LookingGlass/blob/0140a3f6fb616c5636d6c430eb71b8a7d5338e39/LICENSE)
is the GPL version 2 text. These are candidate attribution/licence records
for U1/U2, rather than proof of a copying route or a complete notice for
this repository. If the examples were derived from that documentation,
retain the applicable copyright, licence and modification notices and
resolve the conditions on the actual reused material before clearance.
The audit does not determine whether these short functional fragments
attract copyright or whether their reuse meets those conditions.

**Possible ArchWiki source remains unchecked.** The freeze note names the
[PCI passthrough via OVMF page](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF).
Retrieval of that page returned access denial/bot protection, not source
text, so no revision of it was compared and no match is claimed. The
accessible [ArchWiki copyright record](https://wiki.archlinux.org/index.php?title=ArchWiki:Copyrights&oldid=613736)
(revision 613736) states GFDL 1.3 or later unless otherwise noted. If material
was taken from the wiki, establish the actual revision, contributor/history
attribution, applicable notice, modification history and licence-copy
requirements. A link or this candidate notice alone does not settle them.

### Other content found in the input

| Paths | Relationship and remaining limit |
| --- | --- |
| four `configs/boot/*.conf` files; `problems/gpu-freeze-power-management.md`; both boot-entry problem notes | repeated local loader/storage examples and comments; direction of reuse unrecorded. The freeze note explicitly says parameters were copied from various forums. Exact originating posts and versions are missing (U13). |
| `problems/boot-entries-backslash-continuation.md` | explanation of the [Boot Loader Specification](https://github.com/uapi-group/specifications/blob/5f0f51489defcf43999ed23cd03b6ebc69f940e3/specs/boot_loader_specification.md), plus local boot examples; no identified wholesale quotation. Derivation remains P19. |
| `configs/virtual-display-windows.md`; the GeForce, kvmfr, client-INI and SPICE-fallback notes | short reported Looking Glass logs, parser/help output, QEMU/libvirt errors and an NVIDIA tool message; diagnostic output, not bundled programs. The INI note describes a generated header without shipping its generator. Source versions/terms and the origin of the excerpts remain U14. |
| `problems/gpu-freeze-power-management.md` | six words quoted from [Arch BBS 286946](https://bbs.archlinux.org/viewtopic.php?pid=2108129#p2108129), by sick_mitch, post 15 (2023-07-05): “in a post in proxmox forum”. The excerpt matches the retrieved page; no reuse licence was established. The kernel message is a diagnostic excerpt (U13/U14). |
| `problems/geforce-passthrough-needs-a-display.md` | paraphrases [B7 display requirements](https://looking-glass.io/docs/B7/requirements/); names the VirtualDrivers product and repeats the README's winget command. A command match does not establish the origin of surrounding prose. |
| `configs/boot/boot-profiles.md`; compatibility data; freeze note | factual hardware identifiers, device labels and text diagrams. The exact device-name dataset version was not recorded; no PCI database or graphical asset is bundled. |
| problem-note reference lists | source links to ArchWiki, the Arch BBS, Reddit r/VFIO, Level1Techs, an Optimus gist, VirtualDrivers and roshkins/IddSampleDriver. A link is a reference, not a licence or evidence that code was copied. |

The `LICENSE` permission/disclaimer matches the standard
[MIT wording](https://github.com/spdx/license-list-data/blob/v3.29.0/text/MIT.txt)
after whitespace normalization; this does not prove where the file was
obtained. Preserve the existing root copyright and complete permission
notice in copies covered by it. No existing notice or input file was
changed by this audit. The per-path findings remain in the inventory;
shortness, publication history and factual subject matter are not used as
blanket rights clearance.

## 3. CI and collector tools obtained elsewhere

Only the workflow and script source bytes are bundled. CI installs or
fetches tools during its run; the collector assumes host tools already
exist. Their installed versions, build inputs and transitive dependencies
are not identified by this tree.

| Reference | Evidence and declared licence | Open case |
| --- | --- | --- |
| `actions/checkout@v4` | workflow tag; candidate [`LICENSE`](https://github.com/actions/checkout/blob/11d5960a326750d5838078e36cf38b85af677262/LICENSE) is MIT, copyright 2018 GitHub, Inc. and contributors; no immutable action commit is specified by CI | U9 |
| `pip install pyyaml`; `import yaml` | unpinned; retrieved [PyYAML licence](https://github.com/yaml/pyyaml/blob/main/LICENSE) is MIT, copyright Ingy döt Net and Kirill Simonov; this moving record is not the installed version's evidence (retrieved text SHA-256 `8d3928f9dc4490fd635707cb88eb26bd764102a7282954307d3e5167a577e8a4`) | U9 |
| `ubuntu-latest`, Python, Bash, pip, apt and ShellCheck | named by CI; runner/package versions and corresponding licence/notice records not established | U9 |
| `date`, `uname`, `mkdir`, `dirname`, `tr`, `lscpu`, `grep`, `lspci`, `stat`, `find`, `wc`, `virsh`, Bash | commands in `scripts/collect-hardware-report.sh`; versions, package mappings and licences not inventoried | U10 |

MIT redistributions require the applicable copyright and permission notice.
These candidate tool records do not license a runner image or dependency
closure. The collector was not run; its possible output still requires
manual privacy review before publication.

## 4. Installation delegated to the sibling repositories

`SETUP.md` delegates the Arch installation, Secure Boot, Ansible collections,
host packages, networks, images, guests and services to `arch-bootstrap`
and `hyperlab-ansible`. References to Sway, Hyprland, XDPH/PipeWire, libvirt,
QEMU, Whonix, Jellyfin, Nextcloud and Blender are software references, not
bundled bytes or grants to redistribute those products. Whonix is named
in boot-entry comments; no Whonix image is supplied here.

**U11 — delegated closure is outside this audit.** Packages, firmware,
fonts, themes, collections and image payloads need inventories of their
own actual inputs. This report neither substitutes for the sibling audits
nor admits anything to a future ISO. It supplies no image manifest, image
build, signature, distribution approval or hardware result.

**Looking Glass build.** The input guides identify
`B7-263-g0140a3f6fb`. At inspected sibling commit
`959afcfed1e74b510f1d1f07e8152582090a0695`,
`group_vars/all/looking-glass.yml` maps that label to
`0140a3f6fb616c5636d6c430eb71b8a7d5338e39`, and
`roles/looking_glass/defaults/main.yml` names the upstream repository.
These are contextual source records, not input files covered by this
inventory and not proof of an installed binary.

At that upstream commit, the root licence is GPL version 2;
[`module/kvmfr.c`](https://github.com/gnif/LookingGlass/blob/0140a3f6fb616c5636d6c430eb71b8a7d5338e39/module/kvmfr.c)
names the Looking Glass Authors (2017–2026), grants GPL version 2 or later
and declares the module GPL v2. Preserve the applicable notices and resolve
source obligations for actual binary distribution. The
[submodule record](https://github.com/gnif/LookingGlass/blob/0140a3f6fb616c5636d6c430eb71b8a7d5338e39/.gitmodules)
names LGMP, PureSpice, cimgui, nanosvg and wayland-protocols. Their licences,
patches and build/dependency closure remain U11, not an audited payload.

**U8 — optional host profiles.** The Nvidia boot entry names `nvidia-dkms`
or `nvidia`, without version/source/licence evidence. The Integrated entry
mentions a udev/bbswitch rule not supplied in the tree. No current package
substitution, source mapping or redistributable driver set is inferred from
those names. These are unresolved references, not installation changes.

## 5. Private Windows workshop dependencies

`SETUP.md`, the Looking Glass guide and the Windows display guide describe
manual guest operations. None of the media, installers, account data or
receipts is bundled. A signed or described-as-reviewed installer is not
redistribution permission.

| Case | What is identified | Missing evidence and affected distribution |
| --- | --- | --- |
| U3 | guide says reviewed signed Virtual Display Driver; historical GeForce note separately names VirtualDrivers/Virtual-Display-Driver | guide gives no vendor/product/release/source/licence. The note gives a product but no release/installer digest. Do not assume they are the same. Any image carrying either needs its own evidence. |
| U4 | Looking Glass host installer for the client build, with IVSHMEM and host service | actual binary source/build, digest, signer, matching source and bundled IVSHMEM origin/terms; any Windows image carrying it |
| U5 | reviewed virtio-win media and `vioinput` | exact media release, URL, digest and internal licence/notices; any image carrying its drivers |
| U6 | NVIDIA guest driver | package/release/source/licence and redistribution conditions; any guest image carrying it |
| U7 | Windows 11 guest | edition/media source and terms for the actual installation and any image redistribution; accounts and media stay private |
| U12 | Unigine Valley benchmark in the GeForce note; Valley workload name in SETUP | edition/version/source/terms if retained in an image; a benchmark result does not redistribute the benchmark |

Relevant primary records, retrieved on 2026-10-27 at 23:40 UTC:

- **VirtualDrivers:** [`LICENSE`](https://github.com/VirtualDrivers/Virtual-Display-Driver/blob/d7244969b2aa8bb38e76d79505eda217996cefea/LICENSE)
  is MIT, copyright 2024 Virtual Display. Its
  [README](https://github.com/VirtualDrivers/Virtual-Display-Driver/blob/d7244969b2aa8bb38e76d79505eda217996cefea/README.md)
  credits SignPath for signing. The tree also has a Windows Driver
  Frameworks submodule and separately licensed audio-driver material.
  The root MIT record is not an inventory of the unspecified installer.
- **Looking Glass installer:**
  [`installer.nsi`](https://github.com/gnif/LookingGlass/blob/0140a3f6fb616c5636d6c430eb71b8a7d5338e39/host/platform/Windows/installer.nsi)
  carries GPL version 2 or later wording. It installs a host executable
  and licence file and can include IVSHMEM catalog/INF/SYS files supplied
  to the build. The script does not establish the binary package's
  contents or the separately supplied driver's licence.
- **virtio-win:** the
  [driver-source licence](https://github.com/virtio-win/kvm-guest-drivers-windows/blob/f7c8beb249df12f52ba4b9dba95f1edb515c7aeb/LICENSE)
  has BSD three-clause conditions and names Red Hat, Google, Virtuozzo and
  IBM. Source copies retain notices, conditions and disclaimer; binary
  copies reproduce them in accompanying materials; endorsement is
  restricted. The packaging
  [COPYING](https://github.com/virtio-win/virtio-win-pkg-scripts/blob/b3c54dd86b0763bc8c137c0b874c52ca300a49cd/COPYING)
  is GPL version 2, a separate scope. The
  [README](https://github.com/virtio-win/virtio-win-pkg-scripts/blob/b3c54dd86b0763bc8c137c0b874c52ca300a49cd/README.md)
  describes several channels and signatures. Neither record identifies
  the workshop media or clears every binary on it.
- **NVIDIA, Windows and Valley:** no actual release/source is identified
  and no applicable product licence was retrieved. Their terms remain
  unknown here; source and signature evidence must not substitute for them.

## 6. Review cases and publication limits

Each unresolved input row has its own `Pnn` identifier, derived from its
ordinal in the sorted input path set (`LICENSE`, ordinal 3, has no pending
case). For **each** such path, obtain an origin account for its prose,
comments, data and examples; identify any upstream revision and terms, or
record independent creation with supporting evidence. Do not change a row
to cleared merely because the root declares MIT. U1/U2 concern possible
copied examples, U13 concerns forum-derived parameters/quotations, and U14
concerns the diagnostic excerpts and help text.

U3–U8 and U12 concern software obtained elsewhere. Resolving publication of
a configuration example does not grant permission to bundle its external
binary. U9/U10 concern external tool versions; U11 concerns the separate
installation and image closure. All remain open as described above.

A component case is attached to every input path that instructs obtaining
or installing that software, names it as part of a lab workload, or reports
it installed or running. A product name used only to identify hardware, a
VM name inside a captured log, a file name in a list or a compatibility
state key is not counted as a reference. The `unresolved` column of the
inventory is the authoritative path list for each case.

This is a reviewable audit result, including explicit unknowns, rather than
legal clearance or a release qualification. It changes no compatibility
state. Manual evidence review, separate same-input Nitro/Predator campaigns
and an actual audited, authentically verified ISO build remain separate
requirements. No Windows image distribution is authorized by this report.
