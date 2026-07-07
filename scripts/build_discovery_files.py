#!/usr/bin/env python3
"""Build machine-readable discovery files for CaseBriefKit."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPDATED = "2026-07-07"


@dataclass(frozen=True)
class Entry:
    path: str
    title: str
    description: str

    @property
    def url(self) -> str:
        return f"{site_base_url()}/{self.path}".rstrip("/") + "/"


ENTRIES = [
    Entry("", "CaseBriefKit", "Free case brief template and maker for law school reading notes."),
    Entry("case-brief-maker", "Case Brief Maker", "Generate FIRAC, IRAC, and CREAC case briefs in the browser."),
    Entry("law-school-case-brief-template", "Law School Case Brief Template", "Free law school case brief template with maker, PDF, DOCX, outline, and examples."),
    Entry("free-case-brief-template", "Free Case Brief Template", "Copy or download a free case brief template for law school."),
    Entry("case-brief-template-pdf", "Case Brief Template PDF", "Download a free printable case brief template PDF."),
    Entry("case-brief-template-docx", "Case Brief Template DOCX", "Download a free editable DOCX case brief template."),
    Entry("case-brief-format", "Case Brief Format", "Compare common case brief formats for class notes."),
    Entry("irac-case-brief-example", "IRAC Case Brief Example", "Review a short IRAC case brief example for law school notes."),
    Entry("sponsor-media-kit", "Sponsor Media Kit", "Sponsor placement information for relevant legal education resources."),
    Entry("advertise", "Advertise on CaseBriefKit", "Pilot sponsor placement details for law school study resources."),
]


def site_base_url() -> str:
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    loc = ET.parse(ROOT / "sitemap.xml").find(".//sm:loc", ns)
    if loc is None or not loc.text:
        raise RuntimeError("sitemap.xml does not contain a loc entry")
    return loc.text.rstrip("/")


def feed_url() -> str:
    return f"{site_base_url()}/feed.xml"


def write_if_changed(path: Path, text: str, changed: list[str]) -> None:
    original = path.read_text(encoding="utf-8") if path.exists() else None
    if original == text:
        return
    path.write_text(text, encoding="utf-8")
    changed.append(str(path.relative_to(ROOT)))


def build_feed(changed: list[str]) -> None:
    base = site_base_url()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        "    <title>CaseBriefKit</title>",
        f"    <link>{base}/</link>",
        "    <description>Free case brief template and maker updates for law school study notes.</description>",
        "    <language>en-us</language>",
        f'    <atom:link href="{feed_url()}" rel="self" type="application/rss+xml" />',
        f"    <lastBuildDate>{UPDATED}</lastBuildDate>",
    ]
    for entry in ENTRIES:
        lines.extend(
            [
                "    <item>",
                f"      <title>{html.escape(entry.title)}</title>",
                f"      <link>{entry.url}</link>",
                f"      <guid isPermaLink=\"true\">{entry.url}</guid>",
                f"      <description>{html.escape(entry.description)}</description>",
                f"      <pubDate>{UPDATED}</pubDate>",
                "    </item>",
            ]
        )
    lines.extend(["  </channel>", "</rss>"])
    write_if_changed(ROOT / "feed.xml", "\n".join(lines) + "\n", changed)


def build_llms(changed: list[str]) -> None:
    base = site_base_url()
    lines = [
        "# CaseBriefKit",
        "",
        "> Free case brief template and maker for law school reading notes.",
        "",
        "CaseBriefKit is an educational study aid for law students. It helps users organize case reading notes using FIRAC, IRAC, and CREAC formats. It is not legal advice.",
        "",
        "## Core Pages",
        "",
    ]
    for entry in ENTRIES[:8]:
        lines.append(f"- [{entry.title}]({entry.url}): {entry.description}")
    lines.extend(
        [
            "",
            "## Commercial / Sponsor Pages",
            "",
            f"- [Sponsor Media Kit]({base}/sponsor-media-kit/): pilot sponsor placement details.",
            f"- [Advertise]({base}/advertise/): sponsor inquiry information.",
            "",
            "## Files",
            "",
            f"- [Sitemap]({base}/sitemap.xml)",
            f"- [RSS Feed]({base}/feed.xml)",
            f"- [Free PDF Template]({base}/downloads/free-case-brief-template.pdf)",
            f"- [Free DOCX Template]({base}/downloads/free-case-brief-template.docx)",
            "",
            "## Safety",
            "",
            "- Educational study aid only.",
            "- Not legal advice.",
            "- No account is required.",
            "- Do not enter confidential, privileged, or sensitive information.",
        ]
    )
    write_if_changed(ROOT / "llms.txt", "\n".join(lines) + "\n", changed)


def html_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.html")
        if ".git" not in path.parts and not path.name.startswith("google")
    )


def add_feed_link(changed: list[str]) -> None:
    alternate = f'    <link rel="alternate" type="application/rss+xml" title="CaseBriefKit updates" href="{feed_url()}">'
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        if 'rel="alternate" type="application/rss+xml"' in text:
            updated = re.sub(
                r'    <link rel="alternate" type="application/rss\+xml" title="[^"]+" href="[^"]+">',
                alternate,
                text,
            )
        elif "    <link rel=\"icon\"" in text:
            updated = text.replace("    <link rel=\"icon\"", alternate + "\n    <link rel=\"icon\"", 1)
        else:
            updated = text.replace("  </head>", alternate + "\n  </head>", 1)
        write_if_changed(path, updated, changed)


def verify_sitemap_contains_core_pages() -> list[str]:
    failures: list[str] = []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = {node.text or "" for node in ET.parse(ROOT / "sitemap.xml").findall(".//sm:loc", ns)}
    for entry in ENTRIES[:8]:
        if entry.url not in locs:
            failures.append(f"sitemap missing {entry.url}")
    return failures


def main() -> int:
    failures = verify_sitemap_contains_core_pages()
    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    changed: list[str] = []
    build_feed(changed)
    build_llms(changed)
    add_feed_link(changed)
    print("changed_files:")
    if changed:
        for item in changed:
            print(f"- {item}")
    else:
        print("- none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
