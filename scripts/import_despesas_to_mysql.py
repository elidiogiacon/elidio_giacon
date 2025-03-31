import os
import psutil
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from dotenv import load_dotenv
from scripts.etl_utils import normalizar_texto, setup_logger
from tqdm import tqdm

# === Carrega variáveis de ambiente e logger ===
load_dotenv()
logger = setup_logger("import_despesas_to_mysql", console=True)

MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

CSV_CAMINHO = Path("output/csv/despesas_consolidadas.csv")


def calcular_chunksize():
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)
    cpu_cores = psutil.cpu_count(logical=True)

    if total_ram_gb < 4 or cpu_cores <= 2:
        return 1000
    elif total_ram_gb < 8:
        return 5000
    elif total_ram_gb < 16:
        return 10000
    else:
        return 20000


CHUNKSIZE = int(os.getenv("CHUNKSIZE_IMPORT") or calcular_chunksize())


def tentar_leitura_csv(caminho: Path, sep=";", encodings=("utf-8", "latin1", "cp1252")) -> pd.DataFrame:
    for enc in encodings:
        try:
            df = pd.read_csv(caminho, sep=sep, encoding=enc)
            logger.info(f"📥 CSV lido com encoding: {enc}")
            return df
        except Exception as e:
            logger.warning(f"⚠️  Falha com encoding {enc}: {e}")
    raise ValueError(f"❌ Não foi possível ler o CSV {caminho} com os encodings testados.")


def importar_para_mysql():
    if not CSV_CAMINHO.exists():
        logger.error(f"❌ Arquivo CSV não encontrado: {CSV_CAMINHO}")
        return

    try:
        df = tentar_leitura_csv(CSV_CAMINHO)
        logger.info(f"📊 Lido CSV com {df.shape[0]} linhas e {df.shape[1]} colunas.")
        df.columns = [normalizar_texto(col) for col in df.columns]

        engine_str = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        engine = create_engine(engine_str)

        total_rows = len(df)
        total_chunks = (total_rows // CHUNKSIZE) + int(total_rows % CHUNKSIZE > 0)
        logger.info(f"🚚 Iniciando envio em {total_chunks} chunk(s) de {CHUNKSIZE} linhas...")

        for i in tqdm(range(total_chunks), desc="💾 Inserindo chunks"):
            start = i * CHUNKSIZE
            end = min((i + 1) * CHUNKSIZE, total_rows)
            chunk = df.iloc[start:end]
            logger.info(f"📦 Inserindo chunk {i + 1}/{total_chunks} ({start}:{end})")
            chunk.to_sql(
                "fato_despesas_contabeis",
                con=engine,
                if_exists="append" if i > 0 else "replace",
                index=False,
                method="multi"
            )

        logger.info("✅ Dados inseridos com sucesso na tabela 'fato_despesas_contabeis'.")
    except Exception as e:
        logger.exception(f"❌ Erro ao importar despesas para o MySQL: {e}")
        try:
            engine.dispose()
        except Exception:
            logger.warning("⚠️ Erro ao encerrar engine SQL após falha.")
    finally:
        logger.info("🏁 Importação finalizada.")


def main():
    logger.info("🚀 Iniciando importação de despesas para MySQL...")
    importar_para_mysql()


if __name__ == "__main__":
    main()
