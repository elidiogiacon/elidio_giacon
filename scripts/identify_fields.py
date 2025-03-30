import os
import sys
import logging
from pathlib import Path
import pandas as pd

from scripts.etl_utils import (
    normalizar_texto,
    gerar_create_table,
    verificar_diferencas,
    exportar_log_diferencas
)

def detectar_inicio_tabela(path: Path) -> pd.DataFrame:
    """Tenta identificar automaticamente a primeira linha da tabela no dicionário de dados."""
    logging.info(f"🔍 Detectando início da tabela no dicionário: {path.name}")
    preview = pd.read_excel(path, engine="odf", header=None, nrows=20)
    for i, row in preview.iterrows():
        valores = [str(v).strip() for v in row if pd.notna(v)]
        if any("campo" in normalizar_texto(val) for val in valores):
            logging.info(f"✅ Cabeçalho detectado na linha {i}: {valores}")
            df = pd.read_excel(path, engine="odf", header=i)
            return df
    raise ValueError("❌ Cabeçalho da tabela não encontrado no dicionário.")

# === LOG CONFIG ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === CAMINHOS PADRÃO ===
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
INPUT_DIR = ROOT_DIR / "input"
OUTPUT_DIR = ROOT_DIR / "output"
LOG_DIR = OUTPUT_DIR / "logs"
SQL_DIR = OUTPUT_DIR / "sql"

CAMINHO_DICIONARIO = INPUT_DIR / "dicionario_de_dados_das_operadoras_ativas.ods"
CAMINHO_CSV = INPUT_DIR / "Relatorio_cadop.csv"

LOG_PATH = LOG_DIR / "diff_log.txt"
ARQUIVO_SQL_SAIDA = SQL_DIR / "scripts.sql"

# === GARANTIR DIRETÓRIOS DE SAÍDA ===
for d in [LOG_DIR, SQL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# === CONFIGURAÇÕES DE ALIAS DE COLUNAS ===
ALIASES = {
    "registro_ans": "registro_operadora",
    "numero": "número"
}

def main():
    logging.info("🚀 Iniciando identificação de campos...")

    df_dic = detectar_inicio_tabela(CAMINHO_DICIONARIO)
    df_csv = pd.read_csv(CAMINHO_CSV, encoding="latin1", sep=";")

    # === DETECÇÃO ROBUSTA DA COLUNA PRINCIPAL ===
    coluna_nome = next(
        (col for col in df_dic.columns if "nome" in col.lower() and "campo" in col.lower()),
        None
    )

    if not coluna_nome:
        raise ValueError("❌ Coluna com nome do campo não encontrada no dicionário de dados.")

    colunas_dic = set(normalizar_texto(col) for col in df_dic[coluna_nome])
    colunas_csv = set(normalizar_texto(col) for col in df_csv.columns)

    colunas_csv_ajustadas = {ALIASES.get(col, col) for col in colunas_csv}

    faltando, extras = verificar_diferencas(colunas_dic, colunas_csv_ajustadas)
    exportar_log_diferencas(LOG_PATH, faltando, extras, ALIASES)

    logging.info(f"📄 Log de diferenças salvo em: {LOG_PATH}")

    nome_tabela = "cadastro_operadoras"
    sql = gerar_create_table(df_dic, nome_tabela)

    with open(ARQUIVO_SQL_SAIDA, "w", encoding="utf-8") as f:
        f.write(sql)

    logging.info(f"📜 Script SQL salvo em: {ARQUIVO_SQL_SAIDA}")
    logging.info("✅ Etapa 3.1 finalizada com sucesso.")

if __name__ == "__main__":
    main()
