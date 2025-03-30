import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": os.getenv("MYSQL_PORT"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE"),
}

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "input", "Relatorio_cadop.csv")
TABLE_NAME = "cadastro_operadoras"


def importar_csv_para_mysql():
    print(f"📥 Lendo CSV: {CSV_PATH}")
    try:
        df = pd.read_csv(CSV_PATH, sep=";", encoding="latin1")
    except Exception as e:
        print(f"❌ Erro ao ler o CSV: {e}")
        return

    # Altere os nomes das colunas para que coincidam com os da tabela.
    # Exemplo: se a tabela foi criada com todas as colunas em minúsculas:
    df.columns = [col.strip().lower() for col in df.columns]

    # Se houver diferenças específicas, crie um mapeamento:
    # mapping = {"registro_ans": "registro_ans", "cnpj": "cnpj", ...}
    # df = df.rename(columns=mapping)

    # Cria a conexão usando SQLAlchemy
    engine = create_engine(
        f"mysql+mysqlconnector://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}"
        f"@{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}"
    )

    try:
        df.to_sql(
            name=TABLE_NAME,
            con=engine,
            if_exists='append',  # Insere os dados na tabela existente
            index=False,
            chunksize=5000  # Útil para arquivos grandes
        )
        print("✅ Dados inseridos com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao inserir dados: {e}")


if __name__ == "__main__":
    importar_csv_para_mysql()
