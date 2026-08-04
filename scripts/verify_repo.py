#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
errors: list[str] = []

def fail(message: str) -> None:
    errors.append(message)

# Relative Markdown links.
link_re = re.compile(r"\[[^]]*\]\(([^)]+)\)")
for doc in root.rglob("*.md"):
    if ".git" in doc.parts:
        continue
    for target in link_re.findall(doc.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path = (doc.parent / target.split("#", 1)[0]).resolve()
        if not path.exists():
            fail(f"broken link: {doc.relative_to(root)} -> {target}")

compat = yaml.safe_load((root / "hardware/compatibility.yml").read_text())
expected = {"nitro-3060", "predator-3070"}
if set(compat["systems"]) != expected:
    fail("compatibility matrix must contain both target laptops")
for name, system in compat["systems"].items():
    if len(system["vfio_ids"]) != 2:
        fail(f"{name}: expected GPU and HDMI-audio PCI IDs")
    if system["components"].get("full_pipeline") not in {"pipeline-pending", "pipeline-verified"}:
        fail(f"{name}: invalid full_pipeline state")

network_doc = (root / "configs/network-domains.md").read_text()
for name in ("clean", "dirty", "dev", "lab", "services"):
    if name not in network_doc:
        fail(f"network document missing {name}")

lg_xml = (root / "configs/libvirt/looking-glass.xml").read_text()
if not re.search(r"<graphics\s+type=['\"]spice['\"][^>]*port=['\"]5900['\"][^>]*autoport=['\"]no['\"][^>]*listen=['\"]127\.0\.0\.1['\"]", lg_xml):
    fail("Looking Glass SPICE endpoint must be fixed at 127.0.0.1:5900")

for entry in (root / "configs/boot").glob("*.conf"):
    text = entry.read_text()
    if "cryptdevice=" in text:
        fail(f"legacy encrypt syntax in {entry.name}")
    if re.search(r"\\\s*$", text, re.MULTILINE):
        fail(f"backslash continuation in {entry.name}")

readme = (root / "README.md").read_text(encoding="utf-8")
setup = (root / "SETUP.md").read_text(encoding="utf-8")
canonical_lg_build = "B7-263-g0140a3f6fb"

for relative in ("SETUP.md", "configs/looking-glass.md"):
    text = (root / relative).read_text(encoding="utf-8")
    for line_number, line in enumerate(text.splitlines(), start=1):
        command = line.strip()
        if command.startswith("ansible-playbook ") and not command.startswith(
            "ansible-playbook -K "
        ):
            fail(
                f"{relative}:{line_number}: ansible-playbook command must use -K"
            )

if "./verify.sh" not in setup:
    fail("SETUP must verify the stage-2 checkout before host changes")
if "The Nitro\nbootstrap-to-stage-2 host path has been reproduced" not in readme:
    fail("README must record the verified Nitro host path without promoting it")
if "the normal laptop target adds Sway and the Looking Glass host transport" not in readme:
    fail("README must describe Sway and Looking Glass as part of the normal laptop target")
if "The `playbooks/lab.yml` run in step 2 already installed Sway" not in setup:
    fail("SETUP must not present the integrated cockpit as a separate installation")
for stale in (
    "host remains headless by default",
    "Add the optional cockpit",
    "from `pending` to `verified`",
):
    if stale in readme or stale in setup:
        fail(f"stale pipeline topology claim: {stale}")
for heading in (
    "## 4. Prepare and seal images",
    "## 5. Exercise explicit VM lifecycle",
    "## 8. Register services before creation",
):
    if heading not in setup:
        fail(f"SETUP missing current stage-2 boundary: {heading}")
for relative in (
    "configs/virtual-display-windows.md",
    "problems/geforce-passthrough-needs-a-display.md",
    "problems/looking-glass-shows-spice-and-calls-it-success.md",
):
    text = (root / relative).read_text(encoding="utf-8")
    if canonical_lg_build not in text:
        fail(f"{relative}: Looking Glass build identity drift")
if "sanitized Predator examples" not in (root / "configs/boot/boot-profiles.md").read_text(encoding="utf-8"):
    fail("boot profile guide must identify checked-in PCI IDs as examples")
for placeholder in root.rglob(".gitkeep"):
    if ".git" not in placeholder.parts:
        fail(f"dead placeholder file remains tracked: {placeholder.relative_to(root)}")

if errors:
    print("REPOSITORY VERIFICATION FAILED", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print("repository verification: OK")
