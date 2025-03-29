import pdfplumber
import pandas as pd
import os
import zipfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = BASE_DIR / "downloader" / "downloads" / "Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"
CSV_PATH = BASE_DIR / "downloader" / "rol_procedimentos.csv"
ZIP_PATH = BASE_DIR / "downloader" / "Teste_ElidioGiaconNeto.zip"


# Siglas para substituição
SIGLAS = {
    "OD": "Seg. Odontológica",
    "AMB": "Seg. Ambulatorial",
    "HCO": "Seg. Hospitalar Com Obstetrícia",
    "HSO": "Seg. Hospitalar Sem Obstetrícia",
    "REF": "Plano Referência",
    "PAC": "Procedimento de Alta Complexidade",
    "DUT": "Diretriz de Utilização"
}

def substituir_siglas(df, colunas=None):
    if colunas is None:
        colunas = df.columns
    for col in colunas:
        df[col] = df[col].replace(SIGLAS, regex=True)
    return df

def extrair_tabelas_por_lotes(pdf_path, lote=10):
    tabelas = []
    failed_pages = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i in range(total):
            try:
                page = pdf.pages[i]
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df["pagina"] = i + 1
                    tabelas.append(df)
                    print("Página", i + 1, "de", total, "extraída com sucesso")
            except Exception as e:
                failed_pages.append((i + 1, str(e)))
                print("Falha na página", i + 1, "de", total)
    return tabelas, failed_pages

def salvar_em_csv(dataframes, caminho_csv):
    df_concat = pd.concat(dataframes, ignore_index=True)
    df_limpo = substituir_siglas(df_concat)
    df_limpo.to_csv(caminho_csv, index=False, encoding="utf-8-sig")

def compactar_em_zip(arquivo_csv, caminho_zip):
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(arquivo_csv, os.path.basename(arquivo_csv))

def main():
    tabelas, falhas = extrair_tabelas_por_lotes(PDF_PATH)
    print(f"Tabelas extraídas: {len(tabelas)}")
    print(f"Páginas com falha: {len(falhas)}")
    salvar_em_csv(tabelas, CSV_PATH)
    compactar_em_zip(CSV_PATH, ZIP_PATH)
    print(f"Arquivo gerado: {ZIP_PATH}")

if __name__ == "__main__":
    main()
