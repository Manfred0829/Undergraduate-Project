from pyngrok import ngrok
from config import Config

def start_ngrok(port):
    ngrok.set_auth_token(Config.NGROK_AUTH_TOKEN)
    public_url = ngrok.connect(port).public_url
    print(f"ngrok 隧道已啟動: {public_url}")
    return public_url 