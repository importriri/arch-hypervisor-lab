# Bug: Looking Glass B7 rejects a generated `client.ini` on line 1

## Symptom

The client prints the build banner, loads the expected path, then exits:

```text
Loading config from: /home/sid/.config/looking-glass/client.ini
Syntax error on line 1, module not specified for option
```

The first line looks harmless:

```ini
# Managed by hyperlab-ansible
```

## Root cause

For the pinned B7 build, `#` is not accepted as an INI comment marker. Before
any `[module]` section has been seen, the parser treats that line as an option
and correctly reports that no module was specified. `;` is the compatible
comment marker.

## Fix

Use semicolons in the generated file:

```ini
; Managed by hyperlab-ansible

[app]
shmFile=/dev/kvmfr0
```

The Ansible template now enforces that format and the static contract test
rejects any line beginning with `#`.

## Two command-line traps seen at the same time

The installed binary is `looking-glass-client`, not `looking-glass`. Also, `-C`
accepts the configuration file; adding `~/.config` as a second positional path
produces a separate directory error. The normal path is loaded automatically:

```bash
looking-glass-client
# or explicitly
looking-glass-client -C ~/.config/looking-glass/client.ini
```

## Verification

```bash
looking-glass-client --help 2>&1 | grep -E 'shmFile|escapeKey|spice'
looking-glass-client
```

The parser error must be absent before debugging kvmfr, SPICE or the Windows
host application.
