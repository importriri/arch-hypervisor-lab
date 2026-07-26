#!/usr/bin/env bash
set -euo pipefail

out="${1:-hardware-report.md}"
mkdir -p "$(dirname "$out")"

read_safe() {
    local path="$1"

    if [[ -r "$path" ]]; then
        tr -d '\0' < "$path"
    else
        printf 'unavailable'
    fi
}

{
    printf '# Sanitized hardware report\n\n'
    printf -- "- generated_utc: \`%s\`\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf -- "- system_vendor: \`%s\`\n" "$(read_safe /sys/class/dmi/id/sys_vendor)"
    printf -- "- product_name: \`%s\`\n" "$(read_safe /sys/class/dmi/id/product_name)"
    printf -- "- product_version: \`%s\`\n" "$(read_safe /sys/class/dmi/id/product_version)"
    printf -- "- bios_version: \`%s\`\n" "$(read_safe /sys/class/dmi/id/bios_version)"
    printf -- "- kernel: \`%s\`\n" "$(uname -srmo)"

    printf "\n## CPU\n\n\`\`\`text\n"
    lscpu 2>/dev/null \
        | grep -E '^(Architecture|Model name|Virtualization|CPU\(s\)):' \
        || true
    printf "\`\`\`\n\n"

    printf "## Display and audio PCI functions\n\n\`\`\`text\n"
    if command -v lspci >/dev/null; then
        lspci -Dnnk \
            | grep -A3 -Ei 'VGA compatible controller|3D controller|Audio device' \
            || true
    else
        printf 'lspci unavailable\n'
    fi
    printf "\`\`\`\n\n"

    printf "## Virtualization devices\n\n\`\`\`text\n"
    for node in /dev/kvm /dev/kvmfr0; do
        if [[ -e "$node" ]]; then
            stat -c '%F %A %U:%G %n' "$node"
        else
            printf 'missing %s\n' "$node"
        fi
    done

    groups=0
    if [[ -d /sys/kernel/iommu_groups ]]; then
        groups="$(find /sys/kernel/iommu_groups \
            -mindepth 1 -maxdepth 1 -type d -printf '.' | wc -c)"
    fi
    printf 'iommu_groups=%s\n' "$groups"
    printf "\`\`\`\n\n"

    printf "## Libvirt persistent networks\n\n\`\`\`text\n"
    if command -v virsh >/dev/null; then
        virsh net-list --all 2>&1 || true
    else
        printf 'virsh unavailable\n'
    fi
    printf "\`\`\`\n\n"

    printf '## Privacy\n\n'
    printf 'Serial numbers, MAC addresses and IP addresses are intentionally omitted.\n'
} > "$out"

printf 'wrote %s\n' "$out"
