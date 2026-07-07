#!/usr/bin/env python3
"""Report whether optional analytics snippets are configured."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def html_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.glob("*.html")
        if not path.name.startswith("google")
    )


def main() -> int:
    cloudflare_pages: list[str] = []
    clarity_pages: list[str] = []
    marker_pages: list[str] = []
    for path in html_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "static.cloudflareinsights.com/beacon.min.js" in text and "data-cf-beacon=" in text:
            cloudflare_pages.append(path.name)
        if "https://www.clarity.ms/tag/" in text:
            clarity_pages.append(path.name)
        if "casebriefkit-analytics:start" in text:
            marker_pages.append(path.name)

    print(f"html_files={len(html_files())}")
    print(f"analytics_marker_pages={len(marker_pages)}")
    print(f"cloudflare_configured={len(cloudflare_pages) == len(html_files())}")
    print(f"cloudflare_pages={len(cloudflare_pages)}")
    print(f"clarity_configured={len(clarity_pages) == len(html_files())}")
    print(f"clarity_pages={len(clarity_pages)}")
    if marker_pages and not (cloudflare_pages or clarity_pages):
        print("warning=analytics markers exist without provider snippets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
