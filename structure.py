# simple_structurer.py
# Works with a custom proxy endpoint (professor-provided).

import os, json
from pathlib import Path
from datetime import datetime, timezone
from openai import OpenAI

DATA_DIR = Path(__file__).parent / "data"
RAW_BLOB = DATA_DIR / "raw_blob.txt"
OUT_JSON = DATA_DIR / "structured.json"

API_KEY  = os.getenv("API_KEY")  # professor's proxy key
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://cdong1--azure-proxy-web-app.modal.run")
MODEL    = os.getenv("OPENAI_MODEL", "gpt-4o")  # proxy's deployment name

if not API_KEY:
    raise SystemExit("Missing API_KEY env var for the proxy.")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SYSTEM = "You turn text into clean JSON. Output only JSON—no explanations."
USER_TEMPLATE = """\
Convert this newline-separated blob of entries “<quote> — <author>”
into JSON. Each entry -> object with:
- id (kebab-case slug from first few words of the quote)
- title (quote, <=80 chars)
- summary (1 short sentence)
- source_url (https://quotes.toscrape.com/)
- extracted_at ({now_iso})

Return either a JSON array OR an object with "items": [].

BLOB:
{blob}
"""

def main():
    raw = RAW_BLOB.read_text(encoding="utf-8").strip()
    if not raw:
        raise SystemExit("raw_blob.txt is missing or empty. Run your scraper first.")

    now_iso = datetime.now(timezone.utc).isoformat()
    user_msg = USER_TEMPLATE.format(blob=raw, now_iso=now_iso)

    resp = client.chat.completions.create(
        model=MODEL,  # this is the proxy's deployment name
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        temperature=0
    )

    text = resp.choices[0].message.content

    # Validate: must be JSON and be an object or array
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("Model response was not valid JSON:\n", text)
        raise

    if isinstance(data, list):
        data = {"items": data}
    elif not isinstance(data, dict):
        raise TypeError(f"Expected JSON array or object, got {type(data).__name__}")

    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_JSON.resolve()}")

if __name__ == "__main__":
    main()
