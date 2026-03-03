import json
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
LINKS_XLSX = BASE / "links.xlsx"
OUT_JSON = BASE.parent / "frontend" / "targets.json"

def extrair_username(url: str) -> str:
    u = str(url).strip().split("?")[0].rstrip("/")
    # suporta /p/xxx, /reel/xxx etc. -> nesses casos cai no "xxx" também
    return u.split("/")[-1]

def main():
    df = pd.read_excel(LINKS_XLSX)

    if "Link" not in df.columns:
        raise ValueError("A planilha links.xlsx precisa ter a coluna 'Link'.")

    links = df["Link"].dropna().astype(str).tolist()

    # Gera perfis a partir dos links (último trecho da URL)
    perfis = []
    for link in links:
        user = extrair_username(link)
        if user:
            perfis.append(user)

    data = {
        "perfis": perfis,
        "links": links
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ targets.json gerado em: {OUT_JSON}")
    print(f"   perfis: {len(perfis)} | links: {len(links)}")

if __name__ == "__main__":
    main()