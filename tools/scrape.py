# tools/scrape.py
from __future__ import annotations

import re
import time
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    )
}


def _clean(txt: str) -> str:
    return re.sub(r"\s+", " ", (txt or "").strip())


def fetch_html(url: str, timeout: int = 20) -> str:
    last: Optional[Exception] = None
    for _ in range(2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(0.8)
    raise RuntimeError(f"Failed to fetch {url}: {last}")


def scrape(url: str) -> Dict[str, str]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    main = soup.find("main") or soup.body or soup
    for bad in main.select("script, style, nav, header, footer, noscript"):
        bad.decompose()

    title = _clean(soup.title.string if soup.title and soup.title.string else "")
    text = _clean(main.get_text(" "))
    return {"url": url, "title": title, "text": text}
