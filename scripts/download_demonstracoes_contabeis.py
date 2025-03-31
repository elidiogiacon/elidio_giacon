import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

# === CONFIGURAÇÕES ===
load_dotenv()
BASE_URL = os.getenv("DEMO_BASE_URL")
ANOS_RETROATIVOS = int(os.getenv("DEMO_ANOS_RETROATIVOS"))
DESTINO = "input"


def baixar_arquivo(url: str, destino: str) -> None:
    """Faz o download de um arquivo ZIP se ainda não existir localmente."""
    nome_arquivo = url.split("/")[-1]
    caminho_arquivo = os.path.join(destino, nome_arquivo)
    if os.path.exists(caminho_arquivo):
        print(f"⚠️  Arquivo já existe: {nome_arquivo}, pulando download.")
        return

    try:
        resposta = requests.get(url, timeout=30)
        resposta.raise_for_status()
        with open(caminho_arquivo, "wb") as f:
            f.write(resposta.content)
        print(f"✅ Baixado com sucesso: {nome_arquivo}")
    except Exception as e:
        print(f"❌ Erro ao baixar {nome_arquivo} → {e}")


def encontrar_arquivos_zip() -> list[str]:
    """Acessa o índice do FTP da ANS e retorna os arquivos ZIP dos anos alvo."""
    print("🌐 Acessando diretório de demonstrações contábeis...")
    try:
        resposta = requests.get(BASE_URL, timeout=15)
        resposta.raise_for_status()
    except Exception as e:
        print(f"❌ Erro ao acessar {BASE_URL} → {e}")
        return []

    soup = BeautifulSoup(resposta.text, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]

    ano_atual = datetime.now().year
    #anos_alvo = [str(ano) for ano in range(ano_atual - ANOS_RETROATIVOS + 1, ano_atual + 1)] # Caso seja interessante pegar do ano atual, mesmo sendo algo não usual.
    anos_alvo = [str(ano) for ano in range(ano_atual - ANOS_RETROATIVOS, ano_atual)]

    arquivos = []

    for link in links:
        if link.strip("/").isdigit() and link.strip("/") in anos_alvo:
            ano_url = BASE_URL + link
            try:
                resposta_ano = requests.get(ano_url, timeout=15)
                resposta_ano.raise_for_status()
                soup_ano = BeautifulSoup(resposta_ano.text, "html.parser")
                zips = [a["href"] for a in soup_ano.find_all("a", href=True) if a["href"].endswith(".zip")]
                arquivos += [ano_url + zipfile for zipfile in zips]
            except Exception as e:
                print(f"❌ Erro ao acessar {ano_url} → {e}")

    print(f"🔎 Encontrados {len(arquivos)} arquivos dos anos: {', '.join(anos_alvo)}")
    return arquivos


def main():
    """Executa o download dos arquivos de demonstrações contábeis."""
    os.makedirs(DESTINO, exist_ok=True)
    arquivos = encontrar_arquivos_zip()
    for url in arquivos:
        baixar_arquivo(url, DESTINO)


if __name__ == "__main__":
    main()
