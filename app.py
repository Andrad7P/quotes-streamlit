import os, pandas as pd, streamlit as st
from supabase import create_client

st.set_page_config(page_title="Quotes Browser", layout="wide")
st.title("Quotes (from Supabase)")

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not (URL and KEY):
    st.error("Set SUPABASE_URL and SUPABASE_ANON_KEY (or SERVICE_ROLE).")
    st.stop()

sb = create_client(URL, KEY)
res = sb.table("quotes").select("*").order("updated_at", desc=True).limit(500).execute()
df = pd.DataFrame(res.data or [])
if df.empty:
    st.info("No data yet.")
else:
    st.subheader("Latest records")
    st.dataframe(df, use_container_width=True)
    st.subheader("Records per source_url")
    st.bar_chart(df.groupby("source_url").size())
