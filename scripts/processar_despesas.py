import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
from scripts.etl_utils import normalizar_texto, setup_logger, salvar_truncamentos_em_arquivo

load_dotenv()
logger = setup_logger("processar_despesas", console=True)

ANOS_RETROATIVOS = int(os.getenv("DEMO_ANOS_RETROATIVOS", 2))
BASE_PATH = Path(os.getenv("DEMO_CSV_PATH", "temp"))
CSV_SAIDA = Path("output/csv/despesas_consolidadas.csv")


def ler_csv_com_fallback(caminho):
    try:
        return pd.read_csv(caminho, sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        logger.warning(f"🔁 Encoding 'utf-8' falhou para {caminho.name}, tentando 'latin1'...")
        return pd.read_csv(caminho, sep=';', encoding='latin1')


def normalizar_colunas(df):
    df.columns = [col.strip().upper() for col in df.columns]
    if "REG_ANS" in df.columns:
        df.rename(columns={"REG_ANS": "registro_operadora"}, inplace=True)
    return df


def normalizar_textos(df):
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).apply(lambda x: normalizar_texto(x.strip()))
    return df


def processar():
    logger.info("🚀 Iniciando processamento das despesas contábeis...")
    arquivos = list(BASE_PATH.glob("*.csv"))
    if not arquivos:
        logger.warning("⚠️ Nenhum arquivo CSV encontrado para processar.")
        return

    dfs = []
    for arquivo in tqdm(arquivos, desc="📅 Lendo arquivos"):
        logger.info(f"📄 Lendo: {arquivo.name}")
        df = ler_csv_com_fallback(arquivo)
        df = normalizar_colunas(df)
        df = normalizar_textos(df)
        dfs.append(df)

    df_consolidado = pd.concat(dfs, ignore_index=True)
    logger.info(f"📊 Registros consolidados: {len(df_consolidado)}")
    df_consolidado.to_csv(CSV_SAIDA, sep=';', index=False, encoding='utf-8')
    logger.info(f"💾 Exportado para: {CSV_SAIDA}")


def main():
    processar()
    logger.info("✅ Processamento finalizado.")


if __name__ == "__main__":
    main()
