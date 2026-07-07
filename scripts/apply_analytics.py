#!/usr/bin/env python3
"""Add or remove optional analytics snippets for the static site.

Examples:
  python3 scripts/apply_analytics.py --cloudflare-token TOKEN --dry-run
  python3 scripts/apply_analytics.py --cloudflare-token TOKEN --apply
  python3 scripts/apply_analytics.py --clarity-id PROJECT_ID --apply
  python3 scripts/apply_analytics.py --remove --apply

The script is intentionally explicit because analytics should not be silently
enabled without a project token owned by the site operator.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
START = "<!-- casebriefkit-analytics:start -->"
END = "<!-- casebriefkit-analytics:end -->"
BLOCK_RE = re.compile(rf"\n?\s*{re.escape(START)}.*?{re.escape(END)}\n?", re.S)


def html_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.glob("*.html")
        if not path.name.startswith("google")
    )


def validate_cloudflare_token(token: str) -> str:
    value = token.strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", value):
        raise ValueError("Cloudflare token should be 16-128 URL-safe characters.")
    return value


def validate_clarity_id(project_id: str) -> str:
    value = project_id.strip()
    if not re.fullmatch(r"[A-Za-z0-9]{4,64}", value):
        raise ValueError("Clarity project id should be 4-64 alphanumeric characters.")
    return value


def analytics_block(cloudflare_token: str | None, clarity_id: str | None) -> str:
    lines = [f"    {START}"]
    if cloudflare_token:
        lines.append(
            "    <script defer src=\"https://static.cloudflareinsights.com/beacon.min.js\" "
            f"data-cf-beacon='{{\"token\":\"{cloudflare_token}\"}}'></script>"
        )
    if clarity_id:
        lines.extend(
            [
                "    <script>",
                "    (function(c,l,a,r,i,t,y){",
                "      c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};",
                "      t=l.createElement(r);t.async=1;t.src=\"https://www.clarity.ms/tag/\"+i;",
                "      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);",
                f"    }})(window, document, \"clarity\", \"script\", \"{clarity_id}\");",
                "    </script>",
            ]
        )
    lines.append(f"    {END}")
    return "\n".join(lines) + "\n"


def update_html(path: Path, block: str, remove: bool, apply: bool) -> bool:
    original = path.read_text(encoding="utf-8")
    without_old = BLOCK_RE.sub("\n", original)
    if remove:
        updated = without_old
    else:
        if "</head>" not in without_old:
            raise ValueError(f"{path.name}: missing </head>")
        updated = without_old.replace("</head>", f"{block}  </head>", 1)
    if updated == original:
        return False
    if apply:
        path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply optional analytics snippets.")
    parser.add_argument("--cloudflare-token", help="Cloudflare Web Analytics site token.")
    parser.add_argument("--clarity-id", help="Microsoft Clarity project id.")
    parser.add_argument("--remove", action="store_true", help="Remove existing analytics snippets.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Show files that would change.")
    mode.add_argument("--apply", action="store_true", help="Modify HTML files.")
    args = parser.parse_args()

    try:
        cloudflare_token = validate_cloudflare_token(args.cloudflare_token) if args.cloudflare_token else None
        clarity_id = validate_clarity_id(args.clarity_id) if args.clarity_id else None
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not args.remove and not (cloudflare_token or clarity_id):
        print("Provide --cloudflare-token, --clarity-id, or --remove.", file=sys.stderr)
        return 2

    block = analytics_block(cloudflare_token, clarity_id)
    changed: list[str] = []
    for path in html_files():
        if update_html(path, block, args.remove, args.apply):
            changed.append(path.name)

    print(f"mode={'apply' if args.apply else 'dry-run'}")
    print(f"cloudflare_configured={bool(cloudflare_token) and not args.remove}")
    print(f"clarity_configured={bool(clarity_id) and not args.remove}")
    print(f"remove={args.remove}")
    print("changed_files:")
    for item in changed:
        print(f"- {item}")
    if not changed:
        print("- none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
