# streamlit_modal.py
import shlex
import subprocess
from pathlib import Path
import os
import modal  

streamlit_script_local = Path(__file__).parent / "streamlit_run.py"
streamlit_script_remote = "/root/streamlit_run.py"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("streamlit", "pandas", "plotly", "supabase")
    .add_local_file(streamlit_script_local, streamlit_script_remote)
)

secret = modal.Secret.from_name("my-secret")

app = modal.App(name="usage-dashboard", image=image)

if not streamlit_script_local.exists():
    raise RuntimeError("streamlit_run.py not found next to streamlit_modal.py")

@app.function(secrets=[secret]) 
@modal.web_server(8000)
def run():
    target = shlex.quote(streamlit_script_remote)
    cmd = (
        f"streamlit run {target} "
        f"--server.port 8000 "
        f"--server.enableCORS=false "
        f"--server.enableXsrfProtection=false"
    )


    env_vars = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        **os.environ,  
    }

    subprocess.Popen(cmd, shell=True, env=env_vars)
