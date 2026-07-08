#!/usr/bin/env python3
"""Check whether a custom domain is serving the site on the selected host."""

from __future__ import annotations

import argparse
import re
import socket
import ssl
import subprocess
from datetime import datetime, timezone
from urllib.parse import urlparse


GITHUB_PAGES_A = {
    "185.199.108.153",
    "185.199.109.153",
    "185.199.110.153",
    "185.199.111.153",
}
EXPECTED_WWW_CNAME = "NEU-ZHA.github.io"
REQUIRED_BODY_TOKEN = "CaseBriefKit"


def normalize_domain(raw: str) -> str:
    value = raw.strip().lower()
    if value.startswith(("http://", "https://")):
        parsed = urlparse(value)
        value = parsed.netloc or parsed.path
    value = value.strip("/")
    if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*[a-z0-9]", value):
        raise ValueError(f"Invalid domain: {raw!r}")
    return value


def run(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd, text=True, capture_output=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def dig_values(name: str, record_type: str) -> list[str]:
    code, stdout, _ = run(["/usr/bin/dig", "+short", name, record_type])
    if code != 0:
        return []
    return [line.rstrip(".") for line in stdout.splitlines() if line.strip()]


def curl_status(url: str) -> str:
    code, stdout, stderr = run([
        "/usr/bin/curl",
        "-L",
        "--connect-timeout",
        "15",
        "--max-time",
        "40",
        "-s",
        "-o",
        "/dev/null",
        "-w",
        "%{http_code}",
        url,
    ])
    if code != 0:
        return f"NETWORK_ERROR: {stderr or stdout}"
    return stdout or "UNKNOWN"


def curl_body_token(url: str, token: str) -> str:
    code, stdout, stderr = run([
        "/usr/bin/curl",
        "-L",
        "--connect-timeout",
        "15",
        "--max-time",
        "40",
        "-s",
        url,
    ])
    if code != 0:
        return f"NETWORK_ERROR: {stderr or stdout}"
    return "yes" if token in stdout else "no"


def tls_summary(domain: str) -> str:
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=12) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        not_after = cert.get("notAfter", "")
        san = cert.get("subjectAltName", [])
        names = [value for key, value in san if key == "DNS"]
        return f"ok; notAfter={not_after}; names={','.join(names[:6])}"
    except Exception as exc:  # noqa: BLE001 - this is a diagnostic script.
        return f"TLS_ERROR: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check custom-domain DNS and HTTPS readiness.")
    parser.add_argument("domain", help="Domain to check, for example casebriefkit.com")
    parser.add_argument(
        "--platform",
        choices=("cloudflare-pages", "github-pages"),
        default="cloudflare-pages",
        help="Expected host. Cloudflare Pages apex domains should use Cloudflare nameservers.",
    )
    args = parser.parse_args()
    domain = normalize_domain(args.domain)

    a_records = set(dig_values(domain, "A"))
    ns_records = dig_values(domain, "NS")
    www_cname = dig_values(f"www.{domain}", "CNAME")
    https_status = curl_status(f"https://{domain}/")
    www_https_status = curl_status(f"https://www.{domain}/")
    sitemap_status = curl_status(f"https://{domain}/sitemap.xml")
    robots_status = curl_status(f"https://{domain}/robots.txt")
    home_contains_token = curl_body_token(f"https://{domain}/", REQUIRED_BODY_TOKEN)
    uses_cloudflare_ns = all("cloudflare.com" in ns.lower() for ns in ns_records) if ns_records else False

    print(f"generated_at={datetime.now(timezone.utc).isoformat()}")
    print(f"domain={domain}")
    print(f"platform={args.platform}")
    print(f"ns_records={','.join(ns_records) or 'none'}")
    print(f"cloudflare_nameservers={uses_cloudflare_ns}")
    print(f"a_records={','.join(sorted(a_records)) or 'none'}")
    print(f"a_records_match_github={a_records == GITHUB_PAGES_A}")
    print(f"www_cname={','.join(www_cname) or 'none'}")
    print(f"www_cname_expected={EXPECTED_WWW_CNAME}")
    print(f"https_home={https_status}")
    print(f"https_www_home={www_https_status}")
    print(f"https_sitemap={sitemap_status}")
    print(f"https_robots={robots_status}")
    print(f"home_contains_{REQUIRED_BODY_TOKEN}={home_contains_token}")
    print(f"tls={tls_summary(domain)}")

    if args.platform == "github-pages":
        hard_fail = (
            a_records != GITHUB_PAGES_A
            or https_status != "200"
            or sitemap_status != "200"
            or robots_status != "200"
            or home_contains_token != "yes"
            or not (www_cname and www_cname[0].lower() == EXPECTED_WWW_CNAME.lower())
        )
    else:
        hard_fail = (
            not uses_cloudflare_ns
            or https_status != "200"
            or sitemap_status != "200"
            or robots_status != "200"
            or home_contains_token != "yes"
        )
    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
