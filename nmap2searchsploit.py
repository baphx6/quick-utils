#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import subprocess
import sys
import re
import argparse

HIGH_VALUE_KEYWORDS = [
    "rce", "remote", "command", "execution",
    "auth", "authentication", "bypass",
    "upload", "web", "http",
    "apache", "iis", "tomcat", "struts",
    "jenkins", "drupal", "joomla", "wordpress",
    "sql", "database"
]

def normalize_version(version):
    match = re.search(r"\d+\.\d+(\.\d+)?", version)
    return match.group(0) if match else None

def is_high_value(query):
    q = query.lower()
    return any(k in q for k in HIGH_VALUE_KEYWORDS)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Parse Nmap XML and generate high-signal SearchSploit queries"
    )
    parser.add_argument("xml", help="Nmap XML output file")
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="Enable ranked fallback searches"
    )
    parser.add_argument(
        "--high-value-only",
        action="store_true",
        help="Only run searches likely to lead to RCE/auth/web exploitation"
    )
    parser.add_argument(
        "--no-run",
        action="store_true",
        help="Print queries only, do not execute searchsploit"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    tree = ET.parse(args.xml)
    root = tree.getroot()

    seen = set()

    for service in root.findall(".//service"):
        product = service.get("product")
        version = service.get("version")

        if not product or not version:
            continue

        searches = [f"{product} {version}"]

        if args.fallback:
            norm = normalize_version(version)
            if norm:
                searches.append(f"{product} {norm}")
            searches.append(product)

        for query in searches:
            if query in seen:
                continue
            seen.add(query)

            if args.high_value_only and not is_high_value(query):
                continue

            tag = "[HIGH VALUE]" if args.high_value_only else "[+]"
            print(f"\n{tag} Searching: {query}")

            if not args.no_run:
                subprocess.run([
                    "searchsploit",
                    "--exclude=dos",
                    "--exclude=local",
                    query
                ])

if __name__ == "__main__":
    main()
