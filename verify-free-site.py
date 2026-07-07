#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
FORBIDDEN = [
    "Request checkout",
    "checkout",
    "$2.99",
    "$9",
    "template_pack_v0_5",
    "CaseBriefKit_LawSchool_TemplatePack",
    "CaseBriefKit_LawSchool_TemplatePack_v0.5.zip",
    "refund",
    "delivery",
    "8 DOCX",
    "9 PDF",
    "No Markdown",
    "Lemon",
    "Paddle",
    "PayPal",
    "KYC",
    "/Users/",
]
REQUIRED_APP_TOKENS = [
    "trackEvent",
    "copy_output",
    "template_switch",
    "output_switch",
    "load_sample",
]


def html_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.glob("*.html")
        if path.name != "404.html" and not path.name.startswith("google")
    )


def site_base_url() -> str:
    text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    match = re.search(r"<loc>(https?://[^<]+)</loc>", text)
    if not match:
        return ""
    parsed = urlparse(match.group(1).rstrip("/"))
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}".rstrip("/")


def url_to_file(url: str) -> Path:
    base = site_base_url()
    if url.rstrip("/") == base:
        return ROOT / "index.html"
    if url.startswith(base + "/"):
        path = url[len(base) + 1 :]
    else:
        path = url.strip("/")
    return ROOT / (path or "index.html")


def verify_html() -> list[str]:
    failures: list[str] = []
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        for label, pattern in [
            ("title", r"<title>(.*?)</title>"),
            ("description", r'<meta name="description" content="([^"]+)"'),
            ("h1", r"<h1[^>]*>(.*?)</h1>"),
            ("canonical", r'<link rel="canonical" href="([^"]+)"'),
        ]:
            if not re.search(pattern, text, flags=re.S | re.I):
                failures.append(f"{path.name}: missing {label}")
        for href in re.findall(r'href="([^"]+)"', text):
            clean = href.split("#", 1)[0]
            if not clean or clean.startswith(("http", "mailto:", "#")) or clean in {"styles.css"}:
                continue
            if not (ROOT / clean).exists():
                failures.append(f"{path.name}: missing local href {href}")
    return failures


def verify_sitemap() -> list[str]:
    failures: list[str] = []
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap = ROOT / "sitemap.xml"
    locs = [node.text or "" for node in ET.parse(sitemap).findall(".//sm:loc", ns)]
    canonicals = []
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        match = re.search(r'<link rel="canonical" href="([^"]+)"', text, flags=re.S | re.I)
        if match:
            canonicals.append(match.group(1))
    for loc in locs:
        if not url_to_file(loc).exists():
            failures.append(f"sitemap: {loc} does not map to a file")
    missing = sorted(set(canonicals) - set(locs))
    extra = sorted(set(locs) - set(canonicals))
    if missing:
        failures.append("sitemap missing canonical URLs: " + ", ".join(missing))
    if extra:
        failures.append("sitemap has non-canonical URLs: " + ", ".join(extra))
    return failures


def verify_assets() -> list[str]:
    failures: list[str] = []
    for required in ["styles.css", "app.js", "robots.txt", "sitemap.xml", "_headers", "_redirects", ".nojekyll"]:
        if not (ROOT / required).exists():
            failures.append(f"missing {required}")
    app = (ROOT / "app.js").read_text(encoding="utf-8")
    for token in REQUIRED_APP_TOKENS:
        if token not in app:
            failures.append(f"app.js missing {token}")
    if "template_pack_" in app or "template-pack" in app:
        failures.append("app.js still contains template-pack tracking")
    if not (ROOT / "ads.txt").exists():
        failures.append("missing ads.txt")
    if not (ROOT / "advertise.html").exists():
        failures.append("missing advertise.html")
    for required_script in ["scripts/apply_analytics.py", "scripts/check_analytics.py"]:
        if not (ROOT / required_script).exists():
            failures.append(f"missing {required_script}")
    return failures


def verify_ad_readiness() -> list[str]:
    failures: list[str] = []
    combined_html = "\n".join(path.read_text(encoding="utf-8") for path in html_files())
    if combined_html.count('data-ad-slot="') < 3:
        failures.append("fewer than 3 ad-ready slots")
    ad_slots = combined_html.count('data-ad-slot="')
    sponsor_slot_links = combined_html.count('data-track-event="sponsor_slot_click"')
    if sponsor_slot_links < ad_slots:
        failures.append(f"only {sponsor_slot_links} sponsor links for {ad_slots} ad slots")
    if 'href="advertise.html"' not in combined_html:
        failures.append("missing internal advertise.html sponsor links")
    if "ads.txt" not in (ROOT / "privacy.html").read_text(encoding="utf-8"):
        failures.append("privacy.html does not mention ads.txt")
    sponsor_template = ROOT / ".github/ISSUE_TEMPLATE/sponsor-inquiry.yml"
    if not sponsor_template.exists():
        failures.append("missing sponsor inquiry template")
    else:
        sponsor_text = sponsor_template.read_text(encoding="utf-8")
        if "sponsorship" not in sponsor_text or "Sponsor inquiry" not in sponsor_text:
            failures.append("sponsor inquiry template mismatch")
    return failures


def verify_measurable_downloads() -> list[str]:
    failures: list[str] = []
    release_prefix = "https://github.com/NEU-ZHA/casebriefkit-maker/releases/download/free-printable-v0.1/"
    high_intent_pages = [
        ROOT / "free-case-brief-template.html",
        ROOT / "case-brief-template-pdf.html",
        ROOT / "case-brief-template-docx.html",
        ROOT / "printable-case-brief-template.html",
    ]
    for path in high_intent_pages:
        text = path.read_text(encoding="utf-8")
        if "free-case-brief-template.pdf" in text and f"{release_prefix}free-case-brief-template.pdf" not in text:
            failures.append(f"{path.name}: PDF download does not use measurable release asset")
        if "free-case-brief-template.docx" in text and f"{release_prefix}free-case-brief-template.docx" not in text:
            failures.append(f"{path.name}: DOCX download does not use measurable release asset")
    return failures


def verify_structured_data() -> list[str]:
    failures: list[str] = []
    html_type_requirements = {
        "free-case-brief-template.html": ["FAQPage", "DownloadAction"],
        "free-case-brief-maker.html": ["FAQPage", "WebApplication"],
        "law-school-case-brief-template.html": ["FAQPage", "WebApplication"],
    }
    for path in html_files():
        text = path.read_text(encoding="utf-8")
        scripts = re.findall(
            r'<script\s+type="application/ld\+json"\s*>(.*?)</script>',
            text,
            flags=re.S | re.I,
        )
        for index, raw in enumerate(scripts, start=1):
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                failures.append(f"{path.name}: invalid JSON-LD script {index}: {exc}")
        for required in html_type_requirements.get(path.name, []):
            if f'"@type": "{required}"' not in text:
                failures.append(f"{path.name}: missing {required} structured data")
        if path.name in html_type_requirements and " FAQ</h2>" not in text:
            failures.append(f"{path.name}: missing visible FAQ section")
        if path.name == "law-school-case-brief-template.html":
            for token in [
                "External discovery entry",
                "law_school_entry_maker_click",
                "law_school_entry_template_click",
                "law_school_entry_request_click",
            ]:
                if token not in text:
                    failures.append(f"{path.name}: missing external entry token {token}")
    return failures


def verify_forbidden_tokens() -> list[str]:
    failures: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_dir() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".html", ".js", ".css", ".xml", ".txt", ".md", ""}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN:
            if token.lower() in text.lower():
                failures.append(f"{path.relative_to(ROOT)}: forbidden token {token!r}")
    return failures


def main() -> int:
    failures = (
        verify_html()
        + verify_sitemap()
        + verify_assets()
        + verify_ad_readiness()
        + verify_measurable_downloads()
        + verify_structured_data()
        + verify_forbidden_tokens()
    )
    print(f"html_files={len(html_files())}")
    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
