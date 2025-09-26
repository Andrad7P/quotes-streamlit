
# Quote_Site.py
from __future__ import annotations
import json, requests
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup, FeatureNotFound

BASE_URL = "https://quotes.toscrape.com"
HEADERS  = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Always save beside this script
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

def soup_of(html: str) -> BeautifulSoup:
    try:    return BeautifulSoup(html, "lxml")
    except FeatureNotFound:
        return BeautifulSoup(html, "html.parser")

def scrape_page(page: int) -> list[dict]:
    url = f"{BASE_URL}/page/{page}/"
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code == 404: return []
    r.raise_for_status()
    s = soup_of(r.text)
    items = []
    for q in s.select("div.quote"):
        items.append({
            "text": q.select_one("span.text").get_text(strip=True),
            "author": q.select_one("small.author").get_text(strip=True),
            "tags": [t.get_text(strip=True) for t in q.select("div.tags a.tag")],
            "source_url": url,
            "extracted_at": datetime.now(timezone.utc).isoformat()
        })
    return items

def main(pages: int = 1) -> None:
    all_items: list[dict] = []
    for p in range(1, pages + 1):
        part = scrape_page(p)
        if not part: break
        all_items.extend(part)

    if not all_items:
        print("No quotes found."); return

    # Pretty sample (also verifies JSON)
    sample = json.dumps(all_items[:3], indent=2, ensure_ascii=False)
    json.loads(sample)
    print(sample)

    # Write files
    (DATA_DIR / "raw_blob.txt").write_text(
        "\n\n".join(f"{i['text']} — {i['author']}" for i in all_items),
        encoding="utf-8"
    )
    (DATA_DIR / "quotes.json").write_text(
        json.dumps(all_items, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("RAW :", (DATA_DIR / "raw_blob.txt").resolve())
    print("JSON:", (DATA_DIR / "quotes.json").resolve())
    print("BASE:", BASE_DIR.resolve())

if __name__ == "__main__":
    # set PAGES=5 in your shell if you want more pages
    import os
    pages = int(os.environ.get("PAGES", "1"))
    main(pages)
