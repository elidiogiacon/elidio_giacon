import logging
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile
from dotenv import load_dotenv

# === CONFIGURAÇÕES ===
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
ANEXO_DIR = BASE_DIR / "output" / "anexos"
ZIP_PATH = BASE_DIR / "output" / "zips" / "Teste_{elidio_giacon_neto}.zip"
URL = os.getenv("URL_ANEXOS")
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")

# === VALIDAÇÃO DE VARIÁVEL OBRIGATÓRIA ===
if not URL:
    raise ValueError("❌ Variável de ambiente 'URL_ANEXOS' não encontrada no .env")

# === CONFIGURAÇÃO DE LOG DINÂMICA ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")

# === GARANTE ESTRUTURA DE PASTAS ===
ANEXO_DIR.mkdir(parents=True, exist_ok=True)
ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)

def obter_soup(url: str) -> BeautifulSoup:
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logging.error(f"Erro ao acessar a URL: {url} - {e}")
        raise

def extrair_links_anexos(soup: BeautifulSoup):
    anexos = []
    for link in soup.find_all("a", href=True):
        texto = link.get_text().strip().lower()
        href = link["href"]
        if ("anexo i" in texto or "anexo ii" in texto) and href.lower().endswith(".pdf"):
            nome_arquivo = os.path.basename(urlparse(href).path)
            url_absoluta = urljoin(URL, href)
            anexos.append((nome_arquivo, url_absoluta))
    return anexos

def baixar_arquivo(nome_arquivo: str, url: str, pasta_destino: Path):
    caminho = pasta_destino / nome_arquivo
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        with open(caminho, "wb") as f:
            f.write(response.content)
        logging.info(f"✅ Baixado: {nome_arquivo}")
    except Exception as e:
        logging.error(f"❌ Erro ao baixar {url}: {e}")

def compactar_arquivos(pasta: Path, destino_zip: Path):
    with ZipFile(destino_zip, "w") as zipf:
        for file in pasta.glob("*.pdf"):
            zipf.write(file, arcname=file.name)
    logging.info(f"📦 Compactado em: {destino_zip}")

def executar_download_anexos():
    logging.info("🌐 Acessando a página da ANS...")
    soup = obter_soup(URL)
    anexos = extrair_links_anexos(soup)
    if not anexos:
        logging.warning("⚠️ Nenhum anexo encontrado.")
        return

    for nome, link in anexos:
        baixar_arquivo(nome, link, ANEXO_DIR)

    compactar_arquivos(ANEXO_DIR, ZIP_PATH)

    # === Limpeza dos PDFs após compactação ===
    for file in ANEXO_DIR.glob("*.pdf"):
        try:
            file.unlink()
            logging.info(f"🧹 PDF removido: {file.name}")
        except Exception as e:
            logging.warning(f"⚠️ Falha ao remover {file.name}: {e}")

    logging.info("✅ Download e compactação finalizados.")

if __name__ == "__main__":
    executar_download_anexos()