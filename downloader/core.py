import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from zipfile import ZipFile

# Configurações
URL = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_DESTINO = os.path.join(BASE_DIR, "downloads")
ARQUIVO_ZIP = os.path.join(BASE_DIR, "anexos_comprimidos.zip")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def obter_soup(url):
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logging.error(f"Erro ao acessar a URL: {url} - {e}")
        raise

def extrair_links_anexos(soup):
    anexos = []
    for link in soup.find_all("a", href=True):
        texto = link.get_text().lower()
        href = link["href"]
        if "anexo i" in texto or "anexo ii" in texto:
            if href.lower().endswith(".pdf"):
                url_absoluta = urljoin(URL, href)
                nome_arquivo = os.path.basename(urlparse(url_absoluta).path)
                anexos.append((nome_arquivo, url_absoluta))
    return anexos

def baixar_arquivo(nome_arquivo, url, pasta_destino):
    os.makedirs(pasta_destino, exist_ok=True)
    caminho = os.path.join(pasta_destino, nome_arquivo)

    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        with open(caminho, "wb") as f:
            f.write(response.content)
        logging.info(f"Baixado: {nome_arquivo}")
    except Exception as e:
        logging.error(f"Erro ao baixar {url}: {e}")

def compactar_arquivos(pasta, nome_zip):
    with ZipFile(nome_zip, "w") as zipf:
        for root, _, files in os.walk(pasta):
            for file in files:
                caminho_completo = os.path.join(root, file)
                arcname = os.path.relpath(caminho_completo, start=pasta)
                zipf.write(caminho_completo, arcname)
    logging.info(f"Compactado em: {nome_zip}")

def baixar_anexos_pdf():
    soup = obter_soup(URL)
    anexos = extrair_links_anexos(soup)
    for nome, link in anexos:
        baixar_arquivo(nome, link, PASTA_DESTINO)
    compactar_arquivos(PASTA_DESTINO, ARQUIVO_ZIP)
