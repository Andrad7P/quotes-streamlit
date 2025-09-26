
from supabase import create_client
from pathlib import Path
import pandas as pd
import json
from datetime import datetime, timezone

SUPABASE_URL = "https://zpmmwnshgttfiozrdyup.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpwbW13bnNoZ3R0ZmlvenJkeXVwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjM1MDY1OCwiZXhwIjoyMDcxOTI2NjU4fQ.xythux6X65ldIYMv99wz50oUglP8YOhK5KTQWtZ3S9w"  # best for server-side upserts

TABLE = "quotes"
DATA_FILE = Path("data/structured.json")

def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    items = data["items"] if isinstance(data, dict) else data
    if not isinstance(items, list) or not items:
        raise SystemExit("No items to load.")

    df = pd.DataFrame(items, columns=["id", "title", "summary", "source_url", "extracted_at"])
    df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce").dt.tz_convert("UTC").dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    df["extracted_at"] = df["extracted_at"].fillna(datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z"))

    sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    rows = df.to_dict(orient="records")
    resp = sb.table(TABLE).upsert(rows, on_conflict="id").execute()
    if getattr(resp, "error", None):
        raise RuntimeError(resp.error)
    print(f"Upserted {len(rows)} rows into '{TABLE}'.")

if __name__ == "__main__":
    main()

