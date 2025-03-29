import os
import pandas as pd
from etl_utils import (
    normalizar_texto,
    gerar_create_table,
    verificar_diferencas,
    exportar_log_diferencas
)

# === CONFIGURAÇÕES ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_SAIDA = os.path.join(BASE_DIR, "..", "scripts")
os.makedirs(DIR_SAIDA, exist_ok=True)

CAMINHO_DICIONARIO = os.path.join(BASE_DIR, "..", "etapa3", "dicionario_de_dados_das_operadoras_ativas.ods")
CAMINHO_CSV = os.path.join(BASE_DIR, "..", "etapa3", "Relatorio_cadop.csv")
ARQUIVO_SQL_SAIDA = os.path.join(DIR_SAIDA, "scripts.sql")
LOG_PATH = os.path.join(DIR_SAIDA, "diff_log.txt")
NOME_TABELA = "operadoras_ativas"

# Substituições manuais: assumimos que essas colunas são equivalentes
ALIAS_MAP = {
    "registro_ans": "registro_operadora"
}

def main():
    # === LEITURA DO DICIONÁRIO ===
    dicionario_df = pd.read_excel(CAMINHO_DICIONARIO, engine="odf", skiprows=6)
    dicionario_df.dropna(how="all", inplace=True)

    dicionario_df.columns = (
        dicionario_df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )

    if "nome_do_campo" not in dicionario_df.columns:
        print("❌ Coluna 'nome_do_campo' não encontrada. Colunas disponíveis:")
        print(dicionario_df.columns.tolist())
        return

    # === LEITURA E AJUSTE DO CSV ===
    csv_df = pd.read_csv(CAMINHO_CSV, sep=None, engine="python")
    csv_df.rename(columns=ALIAS_MAP, inplace=True)

    csv_columns = set(normalizar_texto(col) for col in csv_df.columns)
    dic_columns = set(normalizar_texto(col) for col in dicionario_df["nome_do_campo"])

    # === VERIFICA DIFERENÇAS ===
    faltando, extras = verificar_diferencas(dic_columns, csv_columns)

    # === GERA E EXPORTA SQL ===
    ddl = gerar_create_table(dicionario_df, NOME_TABELA)
    with open(ARQUIVO_SQL_SAIDA, "w", encoding="utf-8") as f:
        f.write(f"-- Script gerado automaticamente\n\n{ddl}\n")
    print("\n✅ CREATE TABLE exportado para:", ARQUIVO_SQL_SAIDA)

    # === LOG NO CONSOLE ===
    print("\n📌 Diferenças detectadas entre CSV e Dicionário de Dados:\n")
    if faltando:
        print("⚠️  Colunas no dicionário mas ausentes no CSV:")
        for col in sorted(faltando):
            print(f"  - {col}")
    else:
        print("✅ Todas as colunas do dicionário estão presentes no CSV.")

    if extras:
        print("\n⚠️  Colunas no CSV mas que não existem no dicionário:")
        for col in sorted(extras):
            print(f"  - {col}")
    else:
        print("✅ Nenhuma coluna extra no CSV.")

    # === LOG EM ARQUIVO ===
    exportar_log_diferencas(LOG_PATH, faltando, extras, ALIAS_MAP)
    print("\n📝 Log de diferenças salvo em:", LOG_PATH)


if __name__ == "__main__":
    main()
