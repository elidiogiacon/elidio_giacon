import unicodedata
import pandas as pd


def normalizar_texto(texto: str) -> str:
    """Remove acentos, espaços e converte para lowercase."""
    if not isinstance(texto, str):
        return texto
    texto = unicodedata.normalize("NFKD", texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().lower()


def mapear_tipo(tipo: str, tamanho) -> str:
    """Mapeia tipos do dicionário para tipos SQL padrão."""
    tipo = normalizar_texto(tipo)
    if tipo == "texto":
        return f"VARCHAR({int(tamanho) if not pd.isna(tamanho) else 255})"
    elif tipo == "numero":
        return "INT"
    elif tipo == "data":
        return "DATE"
    return "VARCHAR(255)"


def gerar_create_table(df: pd.DataFrame, nome_tabela: str) -> str:
    """Gera instrução SQL de criação de tabela com base no dicionário."""
    colunas_sql = []
    for _, row in df.iterrows():
        nome_coluna = normalizar_texto(str(row["nome_do_campo"])).replace(" ", "_")
        tipo = str(row["tipo"])
        tamanho = row.get("tamanho", None)
        tipo_sql = mapear_tipo(tipo, tamanho)
        colunas_sql.append(f"  `{nome_coluna}` {tipo_sql}")
    colunas_sql_str = ",\n".join(colunas_sql)
    return f"CREATE TABLE `{nome_tabela}` (\n{colunas_sql_str}\n);"


def verificar_diferencas(colunas_dic: set, colunas_csv: set) -> tuple[set, set]:
    """Compara colunas normalizadas do CSV e dicionário."""
    faltando_no_csv = colunas_dic - colunas_csv
    extras_no_csv = colunas_csv - colunas_dic
    return faltando_no_csv, extras_no_csv


def exportar_log_diferencas(path: str, faltando, extras, alias_map):
    """Gera um log detalhado de diferenças entre dicionário e CSV."""
    with open(path, "w", encoding="utf-8") as log:
        log.write("📌 Diferenças detectadas entre CSV e Dicionário de Dados:\n\n")

        if faltando:
            log.write("⚠️  Colunas no dicionário mas ausentes no CSV:\n")
            for col in sorted(faltando):
                log.write(f"  - {col}\n")
        else:
            log.write("✅ Todas as colunas do dicionário estão presentes no CSV.\n")

        if extras:
            log.write("\n⚠️  Colunas no CSV mas que não existem no dicionário:\n")
            for col in sorted(extras):
                log.write(f"  - {col}\n")
        else:
            log.write("✅ Nenhuma coluna extra no CSV.\n")

        if alias_map:
            log.write("\n🔁 Substituições manuais (alias aplicados):\n")
            for original, substituto in alias_map.items():
                log.write(f"  - '{original}' foi considerado equivalente a '{substituto}'\n")
