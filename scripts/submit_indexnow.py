#!/usr/bin/env python3
"""Submit the current CaseBriefKit URL list to IndexNow.

The script defaults to dry-run mode. Use `--apply` only after the key file and
URLs are live.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENDPOINT = "https://api.indexnow.org/indexnow"


def load_payload(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = ["host", "key", "keyLocation", "urlList"]
    missing = [name for name in required if not data.get(name)]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")
    if not isinstance(data["urlList"], list) or not data["urlList"]:
        raise ValueError("urlList must be a non-empty list")
    return data


def validate_payload(data: dict[str, object]) -> None:
    host = str(data["host"])
    key_location = str(data["keyLocation"])
    parsed_key = urlparse(key_location)
    if parsed_key.netloc != host:
        raise ValueError(f"keyLocation host {parsed_key.netloc!r} does not match host {host!r}")
    for url in data["urlList"]:  # type: ignore[index]
        parsed = urlparse(str(url))
        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"URL must be http or https: {url}")
        if parsed.netloc != host:
            raise ValueError(f"URL host {parsed.netloc!r} does not match host {host!r}: {url}")


def ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore[import-not-found]

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def submit(endpoint: str, data: dict[str, object], timeout: int) -> tuple[int, str]:
    body = json.dumps(data).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ssl_context()) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, f"transport_error: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit CaseBriefKit URLs to IndexNow.")
    parser.add_argument("--payload", default=str(ROOT / "indexnow-submit.json"))
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--apply", action="store_true", help="Actually submit the URLs.")
    args = parser.parse_args()

    payload_path = Path(args.payload)
    try:
        data = load_payload(payload_path)
        validate_payload(data)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error={exc}", file=sys.stderr)
        return 2

    urls = data["urlList"]  # type: ignore[index]
    print(f"mode={'apply' if args.apply else 'dry-run'}")
    print(f"endpoint={args.endpoint}")
    print(f"host={data['host']}")
    print(f"keyLocation={data['keyLocation']}")
    print(f"url_count={len(urls)}")
    print(f"first_url={urls[0]}")
    print(f"last_url={urls[-1]}")

    if not args.apply:
        return 0

    status, response_body = submit(args.endpoint, data, args.timeout)
    print(f"http_status={status}")
    if response_body.strip():
        print("response_body:")
        print(response_body.strip())
    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    raise SystemExit(main())
