#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import subprocess
import sys
import re

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <nmap.xml>")
    sys.exit(1)

xml_file = sys.argv[1]
tree = ET.parse(xml_file)
root = tree.getroot()

seen = set()

def normalize_version(v):
    """
    Extract major.minor[.patch] when possible
    """
    match = re.search(r"\d+\.\d+(\.\d+)?", v)
    return match.group(0) if match else None

for service in root.findall(".//service"):
    product = service.get("product")
    version = service.get("version")

    if not product:
        continue

    searches = []

    # 1) Exact match
    if version:
        searches.append(f"{product} {version}")

        norm = normalize_version(version)
        if norm:
            searches.append(f"{product} {norm}")

    # 2) Product-only fallback
    searches.append(product)

    for q in searches:
        if q not in seen:
            seen.add(q)
            print(f"\n[+] Searching: {q}")
            subprocess.run(["searchsploit", q])
