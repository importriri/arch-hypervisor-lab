# Network Architecture — The Four Domains

> Planning document — updated as the project progresses.

## Overview

```
HOST (Arch Linux)
│
├── virbr-clean    10.10.1.0/24   🟢 Clean Gaming
│   └── NAT → internet (official stores only)
│
├── virbr-dirty    10.10.2.0/24   🟠 Dirty Gaming
│   └── NAT → internet (full access)
│
├── virbr-dev      10.10.3.0/24   🔴 Dev / 3D
│   └── NAT → internet + shared folder with host
│
└── virbr-lab      10.10.4.0/24   🟡 Malware Lab
    └── ISOLATED — no internet access
        (traffic routed to host for analysis only)
```

## Isolation rules

| Domain | Internet | Host access | Cross-domain |
|---|---|---|---|
| 🟢 Clean | Yes (restricted) | No | No |
| 🟠 Dirty | Yes (full) | No | No |
| 🔴 Dev | Yes | Shared folder | No |
| 🟡 Lab | No | Traffic dump only | No |

## GPU handoff protocol

```
Golden rule: the GPU never passes directly
             from a low-trust domain to a high-trust one.

Safe path:
  Any domain → FULL VM SHUTDOWN → Host → New domain

Forbidden paths:
  🟠 Dirty → 🟢 Clean    (contamination risk)
  🟡 Lab   → any domain  (always via host with full reset)
```

## Implementation checklist

- [ ] Virtual bridges created with libvirt
- [ ] nftables isolation rules applied
- [ ] Cross-domain isolation verified
- [ ] GPU switch protocol implemented and tested
