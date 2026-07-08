#!/usr/bin/env python3
"""Prepare the static site for a purchased custom domain.

Usage:
  python3 scripts/apply_custom_domain.py casebriefkit.com --platform cloudflare-pages --dry-run
  python3 scripts/apply_custom_domain.py casebriefkit.com --platform cloudflare-pages --apply

Run this only after the domain is purchased and the target host is ready to use it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
OLD_BASE = "https://neu-zha.github.io/casebriefkit-maker"


def normalize_domain(raw: str) -> str:
    value = raw.strip().lower()
    if value.startswith(("http://", "https://")):
        parsed = urlparse(value)
        value = parsed.netloc or parsed.path
    value = value.strip("/")
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*[a-z0-9]", value):
        raise ValueError(f"Invalid domain: {raw!r}")
    if ".." in value or "." not in value:
        raise ValueError(f"Invalid domain: {raw!r}")
    return value


def text_files() -> list[Path]:
    suffixes = {".html", ".xml", ".json", ".txt", ".md"}
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and path.name != "CNAME"
        and path.suffix.lower() in suffixes
    )


def replace_base(path: Path, new_base: str, apply: bool) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = original.replace(OLD_BASE, new_base)
    if updated == original:
        return False
    if apply:
        path.write_text(updated, encoding="utf-8")
    return True


def write_cname(domain: str, apply: bool) -> bool:
    path = ROOT / "CNAME"
    current = path.read_text(encoding="utf-8").strip() if path.exists() else ""
    if current == domain:
        return False
    if apply:
        path.write_text(f"{domain}\n", encoding="utf-8")
    return True


def update_indexnow(domain: str, apply: bool) -> bool:
    path = ROOT / "indexnow-submit.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    if data.get("host") != domain:
        data["host"] = domain
        changed = True
    key = data.get("key", "")
    expected_key_location = f"https://{domain}/{key}.txt"
    if data.get("keyLocation") != expected_key_location:
        data["keyLocation"] = expected_key_location
        changed = True
    new_urls = []
    for url in data.get("urlList", []):
        new_url = url.replace(OLD_BASE, f"https://{domain}")
        new_urls.append(new_url)
        changed = changed or new_url != url
    data["urlList"] = new_urls
    if changed and apply:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return changed


def sitemap_url_count() -> int:
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return len(ET.parse(ROOT / "sitemap.xml").findall(".//sm:loc", ns))


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a custom domain to CaseBriefKit static files.")
    parser.add_argument("domain", help="Purchased domain, for example casebriefkit.com")
    parser.add_argument(
        "--platform",
        choices=("cloudflare-pages", "github-pages"),
        default="cloudflare-pages",
        help="Hosting target. Cloudflare Pages does not need a CNAME file in the repository.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Show files that would change.")
    mode.add_argument("--apply", action="store_true", help="Modify files.")
    args = parser.parse_args()

    try:
        domain = normalize_domain(args.domain)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    new_base = f"https://{domain}"
    changed: list[str] = []
    for path in text_files():
        if replace_base(path, new_base, args.apply):
            changed.append(str(path.relative_to(ROOT)))
    if update_indexnow(domain, args.apply):
        item = "indexnow-submit.json"
        if item not in changed:
            changed.append(item)
    if args.platform == "github-pages" and write_cname(domain, args.apply):
        changed.append("CNAME")

    print(f"mode={'apply' if args.apply else 'dry-run'}")
    print(f"platform={args.platform}")
    print(f"domain={domain}")
    print(f"new_base={new_base}")
    print(f"sitemap_urls={sitemap_url_count()}")
    print("changed_files:")
    for item in changed:
        print(f"- {item}")
    if not changed:
        print("- none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
