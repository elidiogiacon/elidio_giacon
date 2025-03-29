from dotenv import load_dotenv
import os
import mysql.connector

# === CARREGA VARIÁVEIS DO .env ===
load_dotenv()

MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "port": int(os.getenv("MYSQL_PORT")),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
}

NOME_BANCO = os.getenv("MYSQL_DATABASE")
CAMINHO_SQL = os.path.join(os.path.dirname(__file__), "scripts.sql")


def criar_banco(cursor, nome_banco):
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{nome_banco}`;")
    print(f"✅ Banco de dados '{nome_banco}' verificado/criado.")


def executar_script_sql(caminho_sql, conexao, nome_banco):
    with open(caminho_sql, "r", encoding="utf-8") as file:
        script = file.read()

    cursor = conexao.cursor()
    cursor.execute(f"USE `{nome_banco}`;")

    comandos = [cmd.strip() for cmd in script.split(";") if cmd.strip()]
    for comando in comandos:
        try:
            cursor.execute(comando)
            print(f"✅ Comando executado:\n{comando[:80]}...")
        except mysql.connector.Error as err:
            print(f"❌ Erro ao executar comando:\n{comando}\n→ {err}")
    conexao.commit()
    cursor.close()


def main():
    if not all(MYSQL_CONFIG.values()) or not NOME_BANCO:
        print("❌ Variáveis de ambiente não definidas corretamente. Verifique seu .env.")
        return

    print("🔌 Conectando ao MySQL Docker...")
    try:
        conexao = mysql.connector.connect(**MYSQL_CONFIG)
    except mysql.connector.Error as err:
        print(f"❌ Falha na conexão com MySQL: {err}")
        return

    cursor = conexao.cursor()
    criar_banco(cursor, NOME_BANCO)
    cursor.close()

    executar_script_sql(CAMINHO_SQL, conexao, NOME_BANCO)

    conexao.close()
    print("✅ Processo finalizado com sucesso.")


if __name__ == "__main__":
    main()
