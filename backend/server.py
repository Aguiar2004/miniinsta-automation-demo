from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from pathlib import Path
import os

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

if __name__ == "__main__":
    os.chdir(FRONTEND_DIR)

    # Isso ajuda a não dar erro de "porta ocupada" ao reiniciar rápido
    TCPServer.allow_reuse_address = True

    with TCPServer(("127.0.0.1", 8000), Handler) as httpd:
        print("Site rodando em: http://127.0.0.1:8000/index.html")
        httpd.serve_forever()