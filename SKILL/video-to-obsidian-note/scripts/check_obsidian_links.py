#!/usr/bin/env python3
"""Check local image embeds in an Obsidian markdown note."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


OBSIDIAN_EMBED_RE = re.compile(r"!\[\[([^\]#|]+)(?:[#|][^\]]*)?\]\]")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def normalize_link(raw: str) -> str | None:
    link = raw.strip()
    if not link or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", link):
        return None
    if link.startswith("<") and link.endswith(">"):
        link = link[1:-1]
    return link


def extract_links(markdown: str) -> list[str]:
    links: list[str] = []
    for match in OBSIDIAN_EMBED_RE.finditer(markdown):
        link = normalize_link(match.group(1))
        if link:
            links.append(link)
    for match in MARKDOWN_IMAGE_RE.finditer(markdown):
        link = normalize_link(match.group(1))
        if link:
            links.append(link)
    return links


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("note", type=Path)
    parser.add_argument("--vault-root", type=Path)
    args = parser.parse_args()

    note = args.note.resolve()
    vault_root = (args.vault_root or note.parent).resolve()
    markdown = note.read_text(encoding="utf-8")
    links = extract_links(markdown)

    missing: list[Path] = []
    for link in links:
        path = (vault_root / link).resolve()
        exists = path.exists()
        print(f"{'OK' if exists else 'MISSING'}\t{link}")
        if not exists:
            missing.append(path)

    print(f"checked={len(links)} missing={len(missing)}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
