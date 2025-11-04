"""
scripts/fetch_contracts.py

Safe downloader to fetch public contract/terms text from URLs and save clause-sized chunks
into data/raw/. Designed to be run locally by you (so you control which URLs to fetch).

Requirements:
    pip install requests beautifulsoup4 tldextract

Usage examples:
    # read URLs from data/urls.txt
    python scripts/fetch_contracts.py --input data/urls.txt --limit 10

    # fetch single URL (dry-run: don't write files)
    python scripts/fetch_contracts.py --url "https://example.com/terms" --dry-run

Notes:
 - Only fetch URLs you have permission to crawl. Avoid paywalled/copyrighted content without permission.
 - Script will save files to data/raw/<domain>-<n>.txt and log mappings to data/fetch_log.json
"""

import argparse
import json
import os
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup
import tldextract

OUT_DIR = Path("data/raw")
LOG_FILE = Path("data/fetch_log.json")

# Keywords to focus extraction (common clause keywords)
DEFAULT_KEYWORDS = [
    "liability", "data protection", "data", "privacy", "termination", "payment",
    "confidential", "indemnity", "warranty", "deliver", "delivery", "services",
]

HEADERS = {"User-Agent": "DatasetFetcher/1.0 (+https://example)"}


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # prefer <article>
    article = soup.find("article")
    if article:
        text = "\n".join(p.get_text(separator=" ").strip() for p in article.find_all("p"))
        if text.strip():
            return text

    # fallback: collect paragraph text from body
    body = soup.body
    if not body:
        return ""

    paragraphs = [p.get_text(separator=" ").strip() for p in body.find_all("p")]
    # filter empty paragraphs
    paragraphs = [p for p in paragraphs if p]
    return "\n\n".join(paragraphs)


def split_into_chunks(text: str, max_chars: int = 800) -> List[str]:
    # split by paragraphs, aggregate until max_chars reached
    paras = [p.strip() for p in text.split('\n') if p.strip()]
    chunks = []
    current = []
    cur_len = 0
    for p in paras:
        if cur_len + len(p) + 1 <= max_chars:
            current.append(p)
            cur_len += len(p) + 1
        else:
            if current:
                chunks.append("\n\n".join(current))
            current = [p]
            cur_len = len(p) + 1
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def contains_keyword(text: str, keywords: List[str]) -> bool:
    lower = text.lower()
    return any(k.lower() in lower for k in keywords)


def domain_for_url(url: str) -> str:
    ext = tldextract.extract(url)
    domain = ext.domain
    suffix = ext.suffix
    if domain and suffix:
        return f"{domain}.{suffix}"
    # fallback
    from urllib.parse import urlparse
    u = urlparse(url)
    return (u.hostname or "unknown").replace(":", "-")


def fetch_and_save(url: str, out_dir: Path, keywords: List[str], max_chars: int, dry_run: bool, limit_per_url: int):
    print(f"Fetching: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

    text = extract_text_from_html(resp.text)
    if not text:
        print(f"No textual content extracted from {url}")
        return []

    # split and filter
    chunks = split_into_chunks(text, max_chars=max_chars)
    saved = []
    domain = domain_for_url(url)
    n = 0
    for i, c in enumerate(chunks):
        if limit_per_url and n >= limit_per_url:
            break
        # keep chunk if contains keywords (or if no keywords provided)
        if keywords and not contains_keyword(c, keywords):
            continue
        n += 1
        name = f"{domain}-{i+1}.txt"
        out_path = out_dir / name
        if not dry_run:
            out_dir.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as fh:
                fh.write(c)
        saved.append(str(out_path))
    print(f"Saved {len(saved)} chunks from {url}")
    return saved


def main():
    parser = argparse.ArgumentParser(description="Fetch contract/terms text from URLs into data/raw/")
    parser.add_argument("--input", "-i", help="Path to file with URLs (one per line)")
    parser.add_argument("--url", "-u", help="Single URL to fetch")
    parser.add_argument("--limit", type=int, default=0, help="Max number of URLs to process from input (0 = no limit)")
    parser.add_argument("--max-chars", type=int, default=800, help="Approx max chars per saved chunk")
    parser.add_argument("--keywords", "-k", help="Comma-separated keywords to filter chunks (optional)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files; just show what would be saved")
    parser.add_argument("--per-url", type=int, default=5, help="Max chunks per URL to save (0 = no limit)")
    args = parser.parse_args()

    urls = []
    if args.url:
        urls = [args.url]
    elif args.input:
        p = Path(args.input)
        if not p.exists():
            print(f"Input file not found: {p}")
            return
        with p.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    urls.append(line)
    else:
        print("Provide --url or --input file with URLs.")
        return

    if args.limit and args.limit > 0:
        urls = urls[: args.limit]

    keywords = []
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    saved_map = {}
    for url in urls:
        saved = fetch_and_save(url, OUT_DIR, keywords, args.max_chars, args.dry_run, args.per_url)
        saved_map[url] = saved

    # write log (only when not dry-run)
    if not args.dry_run:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        existing = {}
        if LOG_FILE.exists():
            try:
                existing = json.loads(LOG_FILE.read_text(encoding="utf-8"))
            except Exception:
                existing = {}
        existing.update(saved_map)
        LOG_FILE.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Fetch log written to {LOG_FILE}")


if __name__ == "__main__":
    main()
