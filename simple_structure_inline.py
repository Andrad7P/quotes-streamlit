
from openai import OpenAI
from pathlib import Path
from datetime import datetime, timezone
import json

endpoint = "https://cdong1--azure-proxy-web-app.modal.run"
api_key  = "supersecretkey"  
deployment_name = "gpt-4o"   

client = OpenAI(base_url=endpoint, api_key=api_key)

DATA_DIR = Path("data")
RAW_BLOB = DATA_DIR / "raw_blob.txt"
OUT_JSON = DATA_DIR / "structured.json"
RAW_RESP = DATA_DIR / "last_raw_response.txt"

SYSTEM = "You convert text into clean JSON. Output only JSON—no explanations."
USER_TMPL = """Convert this newline-separated blob of "<quote> — <author>" into JSON.

Each entry becomes an object with:
- id: kebab-case slug using ~first 6 words of the quote (letters/numbers/hyphens only)
- title: the quote text trimmed to <= 80 chars
- summary: one short sentence paraphrasing the quote
- source_url: "https://quotes.toscrape.com/"
- extracted_at: "{now_iso}"

Return a JSON object with an "items" array. No prose, no markdown, ONLY JSON.

BLOB:
{blob}
"""

def main():
    raw = RAW_BLOB.read_text(encoding="utf-8").strip()
    if not raw:
        raise SystemExit("raw_blob.txt missing or empty. Run your scraper first.")

    now_iso = datetime.now(timezone.utc).isoformat()
    user_msg = USER_TMPL.format(blob=raw, now_iso=now_iso)

    resp = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    text = resp.choices[0].message.content or ""
    RAW_RESP.write_text(text, encoding="utf-8")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("Model did not return JSON. See data/last_raw_response.txt for details.")
        raise

    if not isinstance(data, dict) or "items" not in data or not isinstance(data["items"], list):
        raise ValueError("Expected a JSON object with 'items' array.")

    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {OUT_JSON.resolve()} ({len(data['items'])} items)")

if __name__ == "__main__":
    main()
