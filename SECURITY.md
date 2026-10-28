# Security policy

## Reporting privately

Report a security problem in `arch-hypervisor-lab` privately, through
GitHub's private vulnerability reporting for this repository: the
**Report a vulnerability** button on
<https://github.com/importriri/arch-hypervisor-lab/security/advisories>,
which opens the form at
<https://github.com/importriri/arch-hypervisor-lab/security/advisories/new>.
A report goes to the repository's maintainer, named in
[`AUTHORS.md`](AUTHORS.md). Do not open a public issue, pull request or
discussion about it.

This repository holds documentation, configuration examples, two scripts
and sanitized hardware evidence. The code that installs and configures the
lab lives in two other repositories, each with its own policy:

- the encrypted base installer:
  [`arch-bootstrap` security policy](https://github.com/importriri/arch-bootstrap/blob/main/SECURITY.md);
- the host, networks, VFIO, Machines and services:
  [`hyperlab-ansible` security policy](https://github.com/importriri/hyperlab-ansible/blob/main/SECURITY.md).

Report a flaw to the repository whose code has it. Report it here when
something in this repository is the problem: a guide or example here that
weakens a boundary when followed, evidence here that claims more than it
shows, or private data published here.

There is one maintainer. There is no security team, no response-time
commitment and no bounty.

### When the form is not there

GitHub shows the button only after a repository administrator has enabled
private vulnerability reporting in the repository settings. This file does
not enable it, and its presence is not proof that the form works. If the
button is missing or the form does not open:

- keep every detail private: do not put it in an issue, a pull request, a
  discussion, a commit, a fork or a public paste;
- you may open a public issue that says only that you have a security report
  and asks for the private form to be enabled, without naming the file, the
  commit or the kind of problem;
- do not send the report to an address found elsewhere: this project
  publishes no security mailbox, team or encryption key.

## Three kinds of report

**A vulnerability.** Something in this repository makes a user less safe
than it says: a script that writes or exposes more than it states, the CI
workflow running untrusted input with the repository's permissions, a
configuration example or guide that, followed as written, opens a display,
network or device path the stage-2 policy closes, or a document stating a
protection the automation does not deliver. Use the private form.

**Private evidence published by mistake.** A tracked file, a commit in the
history or an image contains something that should never have been public:
an account, user or group name, a host name, a serial number, a MAC or IP
address, a disk UUID, a home or runtime path, a key, a token, a password or
a fingerprint. Use the private form. Give the path, the commit and the kind
of value, never the value itself. See
[`EVIDENCE-THREAT-MODEL.md`](EVIDENCE-THREAT-MODEL.md#a-leak-that-is-already-public)
for what happens next, and for why a later commit cannot make it private
again.

**A compatibility failure.** A step that does not work on a laptop, a
profile that does not match its hardware, or a result that does not
reproduce is not a security problem. Open a normal public issue, with
sanitized output only, as [`CONTRIBUTING.md`](CONTRIBUTING.md) describes.
If the failure also crosses a security boundary (for example a guest
reaching another network), it is a vulnerability: use the private form.

## What to send

- what you found, in a few sentences;
- the exact commit you read or ran (`git rev-parse HEAD`) and the path;
- the smallest reproduction you have: the commands, and whether it came
  from reading the files, running `python scripts/verify_repo.py`, running
  the collector, or following a guide on a machine (bare metal or VM);
- what an attacker gains, and what they must already have.

## What never to send

- passphrases, private keys, tokens, Secure Boot keys or any other secret;
- disk images, LUKS headers, guest images or copies of partitions;
- unreviewed logs, collector reports or screenshots: remove user and group
  names, host names, serial numbers, MAC and IP addresses, UUIDs and
  private paths first;
- the leaked value itself, when you report a disclosure.

Replace each private value with a placeholder and say that you did. A
reproduction on a throwaway VM is always preferable to data from a real
machine.

## Scope

In scope: `scripts/`, `.github/workflows/ci.yml`, the examples under
`configs/`, the guides and policies (`README.md`, `SETUP.md`,
`hardware/README.md` and the rest), the evidence under `hardware/` and
`problems/`, and the Git history of all of them.

Out of scope: vulnerabilities in KVM, QEMU, libvirt, Looking Glass, the
NVIDIA driver, Arch Linux packages, firmware, hardware or GitHub itself.
Report those upstream, and tell us if the way these documents use them
makes things worse.

What this repository's evidence can and cannot show, and what it trusts,
is in [`EVIDENCE-THREAT-MODEL.md`](EVIDENCE-THREAT-MODEL.md). The
protections of the lab itself are in the
[stage-2 threat model](https://github.com/importriri/hyperlab-ansible/blob/main/docs/threat-model.md).

## Supported versions

There is no release yet. Only the latest commit on `main` is supported;
reproduce on it before you report.
