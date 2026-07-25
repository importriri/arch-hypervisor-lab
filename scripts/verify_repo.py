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

if errors:
    print("REPOSITORY VERIFICATION FAILED", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print("repository verification: OK")
