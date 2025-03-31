import os
import requests
from dotenv import load_dotenv
from scripts.etl_utils import setup_logger
logger = setup_logger(__name__, console=True)

logger.info('🚀 Iniciando script...')


load_dotenv()

URL_CADOP = os.getenv("URL_CADOP")
OUTPUT_DIR = os.path.join("input")
FILENAME = "Relatorio_cadop.csv"
DEST_PATH = os.path.join(OUTPUT_DIR, FILENAME)

def baixar_csv_cadop():
    print("📥 Baixando arquivo CADOP da ANS...")
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        response = requests.get(URL_CADOP, timeout=30)
        response.raise_for_status()
        with open(DEST_PATH, "wb") as f:
            f.write(response.content)
        print(f"✅ Download finalizado: {DEST_PATH}")
    except Exception as e:
        print(f"❌ Erro ao baixar arquivo CADOP: {e}")

if __name__ == "__main__":
    baixar_csv_cadop()
