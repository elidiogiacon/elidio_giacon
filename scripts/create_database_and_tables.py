from pathlib import Path
from dotenv import load_dotenv
import os
import mysql.connector
from scripts.etl_utils import setup_logger

# === Configuração Inicial ===
load_dotenv()
logger = setup_logger("create_database_and_tables")

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
}
NOME_BANCO = os.getenv("MYSQL_DATABASE")

CAMINHO_SQL_CADASTRO = Path("output/sql/scripts.sql")
CAMINHO_SQL_FATOS = Path("output/sql/fatos_despesas.sql")


def executar_script_sql(caminho_sql: Path, conexao):
    """
    Executa um script SQL linha por linha.
    """
    if not caminho_sql.exists():
        logger.error(f"Arquivo SQL não encontrado: {caminho_sql}")
        return
    with open(caminho_sql, "r", encoding="utf-8") as f:
        script = f.read()
    cursor = conexao.cursor()
    for comando in script.split(";"):
        if comando.strip():
            try:
                cursor.execute(comando)
            except Exception as e:
                logger.error(f"Erro ao executar comando: {comando.strip()[:100]}...\n{e}")
    cursor.close()
    conexao.commit()
    logger.info(f"Script executado com sucesso: {caminho_sql.name}")


def main():
    try:
        logger.info("Conectando ao banco de dados MySQL...")
        conexao = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conexao.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {NOME_BANCO}")
        cursor.execute(f"USE {NOME_BANCO}")
        logger.info(f"Banco de dados '{NOME_BANCO}' pronto para uso.")

        executar_script_sql(CAMINHO_SQL_CADASTRO, conexao)
        executar_script_sql(CAMINHO_SQL_FATOS, conexao)

        conexao.close()
        logger.info("Conexão encerrada.")
    except Exception as e:
        logger.exception(f"Erro geral na criação do banco e tabelas: {e}")


if __name__ == "__main__":
    main()