#!/usr/bin/env bash
set -euo pipefail

out="${1:-hardware-report.md}"
mkdir -p "$(dirname "$out")"

read_safe() {
    local path="$1"
    [[ -r "$path" ]] && tr -d '\0' < "$path" || printf 'unavailable'
}

{
    printf '# Sanitized hardware report

'
    printf -- '- generated_utc: `%s`
' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf -- '- system_vendor: `%s`
' "$(read_safe /sys/class/dmi/id/sys_vendor)"
    printf -- '- product_name: `%s`
' "$(read_safe /sys/class/dmi/id/product_name)"
    printf -- '- product_version: `%s`
' "$(read_safe /sys/class/dmi/id/product_version)"
    printf -- '- bios_version: `%s`
' "$(read_safe /sys/class/dmi/id/bios_version)"
    printf -- '- kernel: `%s`
' "$(uname -srmo)"
    printf '
## CPU

```text
'
    lscpu 2>/dev/null | grep -E '^(Architecture|Model name|Virtualization|CPU\(s\)):' || true
    printf '```

## Display and audio PCI functions

```text
'
    if command -v lspci >/dev/null; then
        lspci -Dnnk | grep -A3 -Ei 'VGA compatible controller|3D controller|Audio device' || true
    else
        printf 'lspci unavailable
'
    fi
    printf '```

## Virtualization devices

```text
'
    for node in /dev/kvm /dev/kvmfr0; do
        [[ -e "$node" ]] && stat -c '%F %A %U:%G %n' "$node" || printf 'missing %s
' "$node"
    done
    groups=0
    [[ -d /sys/kernel/iommu_groups ]] && groups="$(find /sys/kernel/iommu_groups -mindepth 1 -maxdepth 1 -type d | wc -l)"
    printf 'iommu_groups=%s
' "$groups"
    printf '```

## Libvirt persistent networks

```text
'
    if command -v virsh >/dev/null; then
        virsh net-list --all 2>&1 || true
    else
        printf 'virsh unavailable
'
    fi
    printf '```

## Privacy

'
    printf 'Serial numbers, MAC addresses and IP addresses are intentionally omitted.
'
} > "$out"

printf 'wrote %s
' "$out"
