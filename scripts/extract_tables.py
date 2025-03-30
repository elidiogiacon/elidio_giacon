import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import logging
import zipfile
import pdfplumber
import pandas as pd

from dotenv import load_dotenv
from pathlib import Path
from scripts.etl_utils import substituir_siglas
from scripts.scan_pdf_tables import detectar_paginas_com_tabelas



# === CONFIGURAÇÕES GERAIS ===
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
ANEXO_DIR = BASE_DIR / "output" / "anexos"
ZIP_PATH = BASE_DIR / "output" / "zips" / "Teste_{elidio_giacon_neto}.zip"  # Arquivo ZIP de entrada (conforme padrão solicitado)

# === PDF fixado conforme especificação do desafio técnico ===
# O desafio solicita a extração apenas do Anexo I.
PDF_FILENAME = "Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"
PDF_PATH = ANEXO_DIR / PDF_FILENAME

# === Caminhos de saída ===
CSV_PATH = BASE_DIR / "output" / "csv" / "rol_procedimentos.csv"
ZIP_OUT = BASE_DIR / "output" / "zips" / "Teste_ElidioGiaconNeto.zip"  # Arquivo ZIP de saída
LOG_PATH = BASE_DIR / "output" / "logs" / "etapa2_failures.log"

# Criar diretórios de saída se necessário
for d in [CSV_PATH.parent, LOG_PATH.parent, ZIP_OUT.parent]:
    d.mkdir(parents=True, exist_ok=True)

# === LOG CONFIG ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")

def extrair_zip_anexos(zip_path: Path, destino: Path) -> None:
    """
    Extrai os arquivos de um ZIP para o diretório de destino.

    Args:
        zip_path (Path): Caminho do arquivo ZIP a ser extraído.
        destino (Path): Diretório onde os arquivos serão extraídos.
    """
    if not destino.exists():
        destino.mkdir(parents=True)
    with zipfile.ZipFile(zip_path, "r") as zipf:
        zipf.extractall(destino)
    logging.info(f"📂 Arquivos extraídos de {zip_path.name} para {destino}")

def extrair_tabelas_do_pdf(pdf_path: Path, paginas_validas: list[int]) -> tuple[list[pd.DataFrame], list[int]]:
    """
    Extrai tabelas de um PDF das páginas especificadas.

    Args:
        pdf_path (Path): Caminho do arquivo PDF.
        paginas_validas (list[int]): Lista de números de páginas que contêm tabelas.

    Returns:
        tuple: Uma tupla contendo:
            - Uma lista de DataFrames com as tabelas extraídas.
            - Uma lista de páginas que falharam na extração.
    """
    tabelas: list[pd.DataFrame] = []
    falhas: list[int] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i in paginas_validas:
            try:
                table = pdf.pages[i - 1].extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    # Deduplicação segura de colunas
                    seen: dict[str, int] = {}
                    new_cols: list[str] = []
                    for col in df.columns:
                        if col not in seen:
                            seen[col] = 1
                            new_cols.append(col)
                        else:
                            seen[col] += 1
                            new_cols.append(f"{col}_{seen[col]}")
                    df.columns = [col.replace('\n', ' ').strip() for col in new_cols]
                    df["pagina"] = i
                    tabelas.append(df)
                    logging.debug(f"✅ Página {i} extraída")
            except Exception as e:
                falhas.append(i)
                logging.warning(f"❌ Falha na página {i}: {e}")
    return tabelas, falhas

def exportar_csv_e_zip(tabelas: list[pd.DataFrame]) -> None:
    """
    Concatena as tabelas extraídas, aplica substituição de siglas, exporta para CSV e compacta em ZIP.

    Args:
        tabelas (list[pd.DataFrame]): Lista de DataFrames das tabelas extraídas.
    """
    if not tabelas:
        logging.warning("⚠️ Nenhuma tabela válida para exportar.")
        return
    df_final = pd.concat(tabelas, ignore_index=True)
    df_final = substituir_siglas(df_final)
    df_final.to_csv(CSV_PATH, index=False)
    with zipfile.ZipFile(ZIP_OUT, "w") as zipf:
        zipf.write(CSV_PATH, arcname=CSV_PATH.name)
    logging.info(f"📦 CSV exportado para: {CSV_PATH}")
    logging.info(f"🗜️ ZIP gerado em: {ZIP_OUT}")

def salvar_log_falhas(falhas: list[int]) -> None:
    """
    Salva as páginas que falharam na extração em um arquivo de log.

    Args:
        falhas (list[int]): Lista de números de páginas que apresentaram falhas.
    """
    if falhas:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            for page in falhas:
                f.write(f"Falha na página {page}\n")
        logging.warning(f"📝 Falhas salvas em: {LOG_PATH}")

def main() -> None:
    """
    Função principal que orquestra o processo de extração e exportação.
    """
    extrair_zip_anexos(ZIP_PATH, ANEXO_DIR)
    if not PDF_PATH.exists():
        logging.error(f"❌ PDF não encontrado: {PDF_PATH}")
        return
    paginas_validas = detectar_paginas_com_tabelas(PDF_PATH)
    if not paginas_validas:
        logging.warning("❌ Nenhuma tabela detectada. Encerrando.")
        return
    logging.info(f"📖 Detectadas {len(paginas_validas)} páginas com tabelas.")
    tabelas, falhas = extrair_tabelas_do_pdf(PDF_PATH, paginas_validas)
    exportar_csv_e_zip(tabelas)
    salvar_log_falhas(falhas)
    logging.info(f"✅ Tabelas extraídas: {len(tabelas)} / Falhas: {len(falhas)}")

if __name__ == "__main__":
    main()
