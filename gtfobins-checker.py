#!/usr/bin/env python3
import sys
import re
import requests
from pathlib import Path


def check(base_url, binaries, mode):
    response = requests.get(f"{base_url}{binaries}")
    #print(response.url)
    if response.status_code != 200:
        return

    if mode == "all":
        print(f"[!] Found {binaries}!!")
        print(f"Check it here: {response.url}")
        print("")
    elif f'id="{mode}"' in response.text:
        print(f"[!] Found {binaries}!!")
        print(f"Check it here: {response.url}")
        print("")



def main():
    if len(sys.argv) != 3:
        print("Usage: gtfobins-checker.py <sudo/suid/all> <binary/binaries.txt>")
        sys.exit(1)

    mode = sys.argv[1].lower()
    binaries = Path(sys.argv[2])

    if mode not in ['sudo', 'suid', 'all']:
        print("First argument must be 'sudo', 'suid', or 'all'.")
        sys.exit(1)

    print(f"[+] Mode: {mode}")
    print(f"[+] Binaries: {binaries}")
    print("")

    base_url = "https://gtfobins.github.io/gtfobins/"

    try:
        with binaries.open('r', encoding='utf-8') as f:
            # print(f"{binaries} opened as a list of binaries")
            for line in f:
                binary = Path(line.strip())
                check(base_url, binary.name, mode)
    except (UnicodeDecodeError, FileNotFoundError):
        # print(f"{binaries} is not a text file, treating as single binary")
        check(base_url, binaries.name, mode)


if __name__ == "__main__":
    main()
