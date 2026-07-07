#!/usr/bin/env python3
"""Build clean URL entry pages for the static CaseBriefKit site.

GitHub Pages does not process the existing `_redirects` file, so paths like
`/case-brief-maker` only work when a real directory contains `index.html`.
This script keeps the flat `.html` files for compatibility, but makes the
canonical, sitemap, and internal links prefer clean SEO URLs.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_HTML = {"404.html"}


def source_html_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.glob("*.html")
        if path.name not in EXCLUDED_HTML
        and not path.name.startswith("google")
    )


def slug_for(path: Path) -> str:
    if path.name == "index.html":
        return ""
    return path.stem


def page_map() -> dict[str, str]:
    return {
        path.name: ("" if slug_for(path) == "" else f"{slug_for(path)}/")
        for path in source_html_files()
    }


def site_base_url() -> str:
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    loc = ET.parse(ROOT / "sitemap.xml").find(".//sm:loc", ns)
    if loc is None or not loc.text:
        raise RuntimeError("sitemap.xml does not contain a loc entry")
    return loc.text.rstrip("/")


def replace_absolute_page_urls(text: str, mapping: dict[str, str]) -> str:
    base = site_base_url()
    updated = text
    for filename, clean_path in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        if filename == "index.html":
            continue
        updated = updated.replace(f"{base}/{filename}", f"{base}/{clean_path}")
    return updated


def split_suffix(value: str) -> tuple[str, str]:
    parts = re.split(r"([?#].*)", value, maxsplit=1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def is_external_or_special(value: str) -> bool:
    return value.startswith((
        "http://",
        "https://",
        "mailto:",
        "tel:",
        "#",
        "data:",
        "javascript:",
    ))


def rewrite_local_reference(value: str, mapping: dict[str, str], prefix: str) -> str:
    if not value or is_external_or_special(value):
        return value
    target, suffix = split_suffix(value)
    if target in {"", "."}:
        return value
    if target == "index.html":
        if prefix:
            return f"{prefix}{suffix}"
        return value
    if target in mapping:
        return f"{prefix}{mapping[target]}{suffix}"
    if target in set(mapping.values()):
        return f"{prefix}{target}{suffix}" if prefix else value
    if target.startswith(("/", "../")):
        return value
    if prefix and (ROOT / target).exists():
        return f"{prefix}{target}{suffix}"
    return value


def rewrite_attrs(text: str, mapping: dict[str, str], prefix: str) -> str:
    attr_pattern = re.compile(r'(?P<attr>\b(?:href|src)=)"(?P<value>[^"]+)"')

    def replace(match: re.Match[str]) -> str:
        attr = match.group("attr")
        value = match.group("value")
        return f'{attr}"{rewrite_local_reference(value, mapping, prefix)}"'

    return attr_pattern.sub(replace, text)


def transform_html(text: str, mapping: dict[str, str], prefix: str) -> str:
    text = replace_absolute_page_urls(text, mapping)
    text = rewrite_attrs(text, mapping, prefix)
    return text


def write_if_changed(path: Path, text: str, changed: list[str]) -> None:
    original = path.read_text(encoding="utf-8") if path.exists() else None
    if original == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    changed.append(str(path.relative_to(ROOT)))


def update_html_files(mapping: dict[str, str], changed: list[str]) -> None:
    for path in source_html_files():
        source = path.read_text(encoding="utf-8")
        updated = transform_html(source, mapping, prefix="")
        write_if_changed(path, updated, changed)

    for path in source_html_files():
        slug = slug_for(path)
        if not slug:
            continue
        source = path.read_text(encoding="utf-8")
        nested = transform_html(source, mapping, prefix="../")
        write_if_changed(ROOT / slug / "index.html", nested, changed)


def update_sitemap(mapping: dict[str, str], changed: list[str]) -> None:
    base = site_base_url()
    sitemap = ROOT / "sitemap.xml"
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(sitemap)
    loc_nodes = tree.findall(".//sm:loc", ns)
    urls: list[str] = []
    for node in loc_nodes:
        loc = node.text or ""
        for filename, clean_path in mapping.items():
            if filename != "index.html":
                loc = loc.replace(f"{base}/{filename}", f"{base}/{clean_path}")
        if loc not in urls:
            urls.append(loc)

    lastmods = {
        (node.find("sm:loc", ns).text or ""): (node.find("sm:lastmod", ns).text or "2026-07-07")
        for node in tree.findall(".//sm:url", ns)
        if node.find("sm:loc", ns) is not None
    }
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lastmod = lastmods.get(url, "2026-07-07")
        body.append(f"  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod></url>")
    body.append("</urlset>")
    write_if_changed(sitemap, "\n".join(body) + "\n", changed)


def update_indexnow(mapping: dict[str, str], changed: list[str]) -> None:
    base = site_base_url()
    path = ROOT / "indexnow-submit.json"
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    urls: list[str] = []
    for url in data.get("urlList", []):
        for filename, clean_path in mapping.items():
            if filename != "index.html":
                url = url.replace(f"{base}/{filename}", f"{base}/{clean_path}")
        if url not in urls:
            urls.append(url)
    data["urlList"] = urls
    write_if_changed(path, json.dumps(data, indent=2) + "\n", changed)


def update_redirects(mapping: dict[str, str], changed: list[str]) -> None:
    lines = []
    for filename, clean_path in sorted(mapping.items()):
        if filename == "index.html":
            continue
        slug = clean_path.rstrip("/")
        lines.append(f"/{filename} /{clean_path} 301")
        lines.append(f"/{slug} /{clean_path} 301")
    lines.append("/* /404.html 404")
    write_if_changed(ROOT / "_redirects", "\n".join(lines) + "\n", changed)


def main() -> int:
    mapping = page_map()
    changed: list[str] = []
    update_html_files(mapping, changed)
    update_sitemap(mapping, changed)
    update_indexnow(mapping, changed)
    update_redirects(mapping, changed)
    print(f"clean_pages={len(mapping) - 1}")
    print("changed_files:")
    if changed:
        for item in changed:
            print(f"- {item}")
    else:
        print("- none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
