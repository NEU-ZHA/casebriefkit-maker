#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIELDS = {
    "slot_id",
    "sponsor_name",
    "headline",
    "body",
    "cta_text",
    "url",
}


def load_config(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_FIELDS - set(data))
    if missing:
        raise SystemExit(f"config missing required fields: {', '.join(missing)}")
    if not str(data["url"]).startswith(("https://", "http://")):
        raise SystemExit("config url must start with https:// or http://")
    return {key: str(value) for key, value in data.items()}


def sponsored_aside(config: dict[str, str], original_class: str) -> str:
    slot_id = html.escape(config["slot_id"], quote=True)
    sponsor_name = html.escape(config["sponsor_name"], quote=True)
    headline = html.escape(config["headline"])
    body = html.escape(config["body"])
    cta_text = html.escape(config["cta_text"])
    url = html.escape(config["url"], quote=True)
    track_event = html.escape(
        config.get("track_event", f"sponsor_{config['slot_id'].replace('-', '_')}_click"),
        quote=True,
    )
    campaign = html.escape(config.get("campaign", "founding-sponsor-pilot"), quote=True)
    class_attr = html.escape(original_class, quote=True)
    return f'''<aside class="{class_attr}" data-ad-slot="{slot_id}" data-sponsored="true" data-sponsor-name="{sponsor_name}" data-sponsor-campaign="{campaign}">
          <span class="ad-label">Sponsored</span>
          <strong>{headline}</strong>
          <p>{body}</p>
          <div class="ad-slot-actions">
            <a data-track-event="{track_event}" href="{url}" rel="sponsored noopener" target="_blank">{cta_text}</a>
            <a class="sponsor-link" data-track-event="sponsor_slot_click" href="advertise.html">Advertise here</a>
          </div>
        </aside>'''


def replace_slot(text: str, config: dict[str, str]) -> tuple[str, int]:
    slot_id = re.escape(config["slot_id"])
    pattern = re.compile(
        r'<aside class="(?P<class>[^"]*\bad-slot\b[^"]*)" data-ad-slot="'
        + slot_id
        + r'"[^>]*>.*?</aside>',
        flags=re.S,
    )

    def repl(match: re.Match[str]) -> str:
        return sponsored_aside(config, match.group("class"))

    return pattern.subn(repl, text, count=1)


def apply(root: Path, config: dict[str, str], write: bool) -> list[tuple[Path, int]]:
    changed: list[tuple[Path, int]] = []
    for path in sorted(root.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        new_text, count = replace_slot(text, config)
        if count:
            changed.append((path, count))
            if write:
                path.write_text(new_text, encoding="utf-8")
            break
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply a reviewed sponsor placement to one ad slot.")
    parser.add_argument("--config", required=True, type=Path, help="Sponsor placement JSON config.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Site root. Defaults to repository root.")
    parser.add_argument("--apply", action="store_true", help="Write changes. Omit for dry-run.")
    args = parser.parse_args()

    config = load_config(args.config)
    changed = apply(args.root, config, args.apply)
    mode = "apply" if args.apply else "dry-run"
    print(f"mode={mode}")
    print(f"slot_id={config['slot_id']}")
    print(f"sponsor_name={config['sponsor_name']}")
    print(f"changed_files={len(changed)}")
    for path, count in changed:
        print(f"{path} replacements={count}")
    if not changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

