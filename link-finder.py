#!/usr/bin/env python3

import sys
import re
import requests
from bs4 import BeautifulSoup
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description="Find links and navigation points in a webpage.")
parser.add_argument("url", help="URL to fetch and scan")
parser.add_argument("--header", action='append', help="Custom header, format: Key: Value")
parser.add_argument("--cookie", action='append', help="Cookie, format: name=value")
args = parser.parse_args()

# Prepare headers and cookies
headers = {}
cookies = {}
if args.header:
    for h in args.header:
        if ':' in h:
            key, value = h.split(':', 1)
            headers[key.strip()] = value.strip()
if args.cookie:
    for c in args.cookie:
        if '=' in c:
            key, value = c.split('=', 1)
            cookies[key.strip()] = value.strip()

# Fetch the page
try:
    response = requests.get(args.url, headers=headers, cookies=cookies, timeout=15)
    response.raise_for_status()
    html = response.text
except Exception as e:
    print(f"Failed to fetch URL: {e}")
    sys.exit(1)

soup = BeautifulSoup(html, 'html.parser')
found = []

def add(category, desc, value):
    if not value:
        return
    found.append((category, desc, value))

# --- Extract content ---
# 1) normal anchor tags
for a in soup.find_all('a'):
    href = a.get('href')
    text = ' '.join(a.get_text(strip=True).split())
    add('Anchor tags', f'a: "{text}"', href)

# 2) any element with href attribute
for el in soup.find_all(attrs={"href": True}):
    add('Href attributes', f'{el.name} [href]', el.get('href'))

# 3) buttons or elements with data-page (SPA navigation)
for b in soup.find_all(attrs={"data-page": True}):
    add('SPA data-page', f'{b.name} [data-page={b["data-page"]}]', f"navigateTo('{b['data-page']}')")

# 4) onclick handlers that call navigateTo(...)
onclicks = soup.find_all(attrs={"onclick": True})
for el in onclicks:
    oc = el.get('onclick')
    m = re.search(r"navigateTo\(\s*['\"]([^'\"]+)['\"]\s*\)", oc)
    if m:
        add('Onclick navigateTo', f'{el.name} [onclick navigateTo]', m.group(1))
    else:
        add('Onclick', f'{el.name} [onclick]', oc)

# 5) scan inline scripts + whole page for common JS-generated endpoints & fetch()/post endpoints
scripts_text = ' '.join([s.get_text() for s in soup.find_all('script')]) + '\n' + html

# find fetch/post endpoints like '/report_bug', '/upload_image', etc.
endpoints = set(re.findall(r"""['"](/[-A-Za-z0-9_/.]+)['"]""", scripts_text))
for ep in sorted(endpoints):
    add('JS endpoints', 'js/string (possible endpoint/path)', ep)

# find navigateTo references inside JS
for m in re.finditer(r"navigateTo\(\s*['\"]([^'\"]+)['\"]\s*\)", scripts_text):
    add('JS navigateTo', 'js: navigateTo()', m.group(1))

# find DOM queries for id
for m in re.finditer(r"getElementById\(\s*['\"]([^'\"]+)['\"]\s*\)", scripts_text):
    add('JS DOM queries', 'js: document.getElementById()', m.group(1))

# --- Output grouped by category ---
if not found:
    print("No links found by heuristics.")
else:
    grouped = defaultdict(list)
    for category, desc, val in found:
        grouped[category].append((desc, val))

    for category in sorted(grouped.keys()):
        print(f"=== {category} ===")
        seen = set()
        for desc, val in grouped[category]:
            key = (desc, val)
            if key in seen:
                continue
            seen.add(key)
            print(f"- {desc:30} → {val}")
        print("\n")  # extra spacing between groups
