#!/usr/bin/env python3
"""Build the Cloudflare Pages Direct Upload package."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path("/Users/zhatong/Documents/Codex/output/casebrieftemplate-cloudflare-pages-upload.zip")
EXCLUDE_DIRS = {".git", ".github", "docs", "scripts", "__pycache__"}
EXCLUDE_FILES = {
    "README.md",
    "LICENSE",
    "verify-free-site.py",
}
INCLUDE_SUFFIXES = {
    ".html",
    ".css",
    ".js",
    ".xml",
    ".txt",
    ".json",
    ".png",
    ".pdf",
    ".docx",
    "",
}


def should_include(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDE_FILES:
        return False
    if path.name.startswith(".DS_Store"):
        return False
    return path.suffix.lower() in INCLUDE_SUFFIXES


def iter_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*") if path.is_file() and should_include(path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Cloudflare Pages Direct Upload zip.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Zip file to write.")
    args = parser.parse_args()

    files = iter_files()
    if not (ROOT / "index.html").exists():
        raise SystemExit("index.html missing")
    if len(files) > 1000:
        raise SystemExit(f"too many files for drag-and-drop upload: {len(files)}")

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())

    size = output.stat().st_size
    print(f"output={output}")
    print(f"files={len(files)}")
    print(f"bytes={size}")
    print(f"size_mb={size / (1024 * 1024):.3f}")
    if size > 25 * 1024 * 1024:
        raise SystemExit("zip exceeds Cloudflare drag-and-drop 25 MiB limit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
