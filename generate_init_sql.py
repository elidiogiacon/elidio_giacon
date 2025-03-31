from dotenv import load_dotenv
import os
from pathlib import Path

def gerar_init_sql():
    load_dotenv()
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

    template_path = Path("docker/mysql/init.sql.template")
    output_path = Path("docker/mysql/init.sql")

    if not template_path.exists():
        print(f"❌ Template não encontrado: {template_path}")
        return

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    sql_final = template.format(
        MYSQL_DATABASE=MYSQL_DATABASE,
        MYSQL_USER=MYSQL_USER,
        MYSQL_PASSWORD=MYSQL_PASSWORD
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sql_final)

    print(f"✅ init.sql gerado com sucesso em: {output_path}")

if __name__ == "__main__":
    gerar_init_sql()