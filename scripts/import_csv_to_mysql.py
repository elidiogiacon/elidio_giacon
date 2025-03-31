
import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from scripts.etl_utils import setup_logger, carregar_truncamentos_do_arquivo
from pathlib import Path
from tqdm import tqdm

# Carrega variáveis de ambiente e logger
load_dotenv()
logger = setup_logger("import_csv_to_mysql")

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

CSV_PATH = Path("input/Relatorio_cadop.csv")

def importar_csv_para_mysql():
    if not CSV_PATH.exists():
        logger.error(f"Arquivo não encontrado: {CSV_PATH}")
        return

    logger.info("🚀 Iniciando importação do CSV para o MySQL...")

    # Importar o CSV com todos os campos como texto
    df = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8", dtype=str)
    logger.info(f"CSV lido com {df.shape[0]} linhas e {df.shape[1]} colunas.")

    # Normalizar colunas
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

    # Renomear registro_ans para registro_operadora para manter padronização
    if "registro_ans" in df.columns:
        df = df.rename(columns={"registro_ans": "registro_operadora"})

    # Garantir que todos os campos estejam como string e sem espaços
    df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else x)

    # Carregar truncamentos do arquivo JSON
    try:
        truncamentos = carregar_truncamentos_do_arquivo()
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível carregar truncamentos: {e}")
        truncamentos = {}

    for coluna, tamanho in truncamentos.items():
        if coluna in df.columns:
            df[coluna] = df[coluna].astype(str).str.slice(0, tamanho)
            logger.info(f"✂️ Truncando coluna '{coluna}' para {tamanho} caracteres.")

    engine_str = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    engine = create_engine(engine_str)

    chunksize = 10000
    total_rows = len(df)
    total_chunks = (total_rows // chunksize) + int(total_rows % chunksize > 0)

    for i in tqdm(range(total_chunks), desc="📤 Inserindo chunks"):
        start = i * chunksize
        end = min((i + 1) * chunksize, total_rows)
        chunk = df.iloc[start:end]
        logger.info(f"📦 Inserindo chunk {i + 1}/{total_chunks} ({start}:{end})")
        chunk.to_sql(
            "cadastro_operadoras",
            con=engine,
            if_exists="append" if i > 0 else "replace",
            index=False,
            method="multi"
        )

    logger.info("✅ CSV importado com sucesso para a tabela 'cadastro_operadoras'!")

def main():
    importar_csv_para_mysql()

if __name__ == "__main__":
    main()
