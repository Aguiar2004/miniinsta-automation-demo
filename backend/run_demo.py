import subprocess
import time
import socket
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent

INDEX_URL = "http://127.0.0.1:8000/index.html"
PROFILE_URL = "http://127.0.0.1:8000/profile.html"

def start_server():
    return subprocess.Popen(
        ["python", str(BASE / "server.py")],
        cwd=str(PROJECT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

def wait_port(host="127.0.0.1", port=8000, timeout=10):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False

def main():
    print("Iniciando servidor...")
    proc = start_server()

    if not wait_port(timeout=10):
        print("Servidor não abriu a porta 8000. Saída do servidor:")
        if proc.stdout:
            try:
                print(proc.stdout.read())
            except Exception:
                pass
        proc.terminate()
        return

    print("Servidor online:", INDEX_URL)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # 1) Abre login
            page.goto(INDEX_URL)

            # 2) Preenche campos do seu index.html (ids: user e pass)
            page.fill("#user", "teste")
            page.fill("#pass", "123")

            # 3) Clica em Entrar
            page.click("text=Entrar")

            # 4) Espera um pouco a navegação
            page.wait_for_timeout(800)

            # 5) Pega targets.json e coloca no localStorage
            #    (se tiver 1 item, já roda 1 vez)
            data = page.evaluate("""async () => {
              const r = await fetch("targets.json", { cache: "no-store" });
              return await r.json();
            }""")

            perfis = data.get("perfis", [])
            if not perfis:
                print("targets.json sem perfis.")
                return

            # coloca fila + perfil selecionado
            page.evaluate(
                """(perfis) => {
                  localStorage.setItem("filaPerfis", JSON.stringify(perfis));
                  localStorage.setItem("modoAuto", "1");
                  localStorage.setItem("perfilSelecionado", perfis[0]);
                }""",
                perfis,
            )

            # 6) Vai direto pro profile
            page.goto(PROFILE_URL)
            page.wait_for_timeout(800)

            # 7) Executa o fluxo usando suas funções do script.js
            page.evaluate("""() => {
              if (typeof openMenu === "function") openMenu();
            }""")
            page.wait_for_timeout(400)

            page.evaluate("""() => {
              if (typeof openReport === "function") openReport();
            }""")
            page.wait_for_timeout(400)

            page.evaluate("""() => {
              if (typeof fakeReport === "function") fakeReport("Spam");
            }""")

            # Espera o ✅ aparecer e sumir
            page.wait_for_timeout(2600)

            print("Demo concluída (simulada). Pode fechar o navegador.")
            # browser.close()

    finally:
        try:
            proc.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    main()