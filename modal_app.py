from modal import App, Image, asgi_app

image = Image.debian_slim().pip_install("streamlit","supabase","pandas")

app = App("quotes-streamlit")
@app.function(image=image, secrets=[])  
@asgi_app()
def web():
    import os, subprocess
    port = int(os.environ.get("PORT", "8000"))
    return subprocess.Popen(
        ["streamlit","run","app.py","--server.port",str(port),"--server.address","0.0.0.0"]
    )
