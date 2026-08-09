# Network architecture: five security domains

The source of truth consumed by automation is
`hyperlab-ansible/group_vars/all/networks.yml`. This document explains the
security meaning of those values.

```text
HOST
├── virbr-clean     10.10.1.0/24  NAT
├── virbr-dirty     10.10.2.0/24  NAT
├── virbr-dev       10.10.3.0/24  NAT
├── virbr-lab       10.10.4.0/24  no forward/uplink
└── virbr-services  10.10.5.0/24  NAT; inbound allowlist only
```

## Domain intent

| Domain | Typical guests | Internet | Host/shared data | GPU |
|---|---|---:|---|---:|
| clean | verified gaming/account VM | NAT | none by default | yes |
| dirty | mods and untrusted gaming tools | NAT | none by default | yes |
| dev | development/3D workstation | NAT | deliberate shares only | yes |
| lab | malware and isolated OT targets | no | capture/analysis paths only | yes |
| services | Jellyfin/Nextcloud/etc. VMs | NAT | explicit DNAT allowlist | never |

`services` is a network domain, not one monolithic service VM. Each service can
remain an independent guest while sharing the same exposure policy.

## Isolation invariants

1. No forwarding between any two domain bridges.
2. Any packet entering or leaving `virbr-lab` is dropped by the host isolation
   table; the bridge can still connect lab guests to one another.
3. NAT does not imply host trust. It only permits outbound connectivity.
4. Service ingress exists only as a named `services_exposed` entry.
5. The dGPU rotates only through `clean`, `dev`, `dirty`, and `lab`.

## GPU trust ladder

```text
clean (3) -> dev (2) -> dirty (1) -> lab (0)
```

Within one host boot, the GPU may move only down this ladder. Moving upward
requires a complete host reboot, which clears the runtime handoff state. The
service domain is absent from the ladder by design.

## Persistent versus live network state

A network can have updated persistent XML while an old active instance remains
running. Verification therefore checks `virsh net-dumpxml --inactive NAME` and
then restarts only changed networks in a maintenance window. The Ansible role
fails closed instead of disconnecting guests without explicit consent.

## Validation checklist

- [ ] all five persistent definitions match this table
- [ ] only `lab` lacks a `<forward>` element
- [ ] all five networks autostart
- [ ] cross-bridge probes fail in both directions
- [ ] lab-to-internet probe fails
- [ ] NAT domains retain outbound connectivity
- [ ] no service is exposed without a matching reviewed allowlist entry
- [ ] `services` is absent from GPU rotation
