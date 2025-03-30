import unicodedata
import pandas as pd


def normalizar_texto(texto: str) -> str:
    """Remove acentos, espaços e converte para lowercase."""
    if not isinstance(texto, str):
        return texto
    texto = unicodedata.normalize("NFKD", texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().lower()


def localizar_coluna(df: pd.DataFrame, alvo: str) -> str:
    """
    Localiza o nome real de uma coluna no DataFrame, mesmo com variações em acentuação,
    espaços, underscores e capitalização.

    Exemplo: "nome_do_campo" encontrará "Nome  do Campo".
    """
    def _normalize(s):
        if not isinstance(s, str):
            return s
        s = unicodedata.normalize("NFKD", s)
        s = ''.join(c for c in s if not unicodedata.combining(c))
        return s.strip().lower().replace(" ", "").replace("_", "")

    alvo_normalizado = _normalize(alvo)

    for col in df.columns:
        if _normalize(col) == alvo_normalizado:
            return col

    raise KeyError(f"❌ Coluna esperada '{alvo}' não encontrada no dicionário.")


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

    coluna_nome = localizar_coluna(df, "nome_do_campo")
    coluna_tipo = localizar_coluna(df, "tipo")
    coluna_tamanho = localizar_coluna(df, "tamanho")

    colunas_sql = []
    for _, row in df.iterrows():
        nome_coluna = normalizar_texto(str(row[coluna_nome])).replace(" ", "_")
        tipo = str(row[coluna_tipo])
        tamanho = row.get(coluna_tamanho, None)
        tipo_sql = mapear_tipo(tipo, tamanho)
        colunas_sql.append(f"  `{nome_coluna}` {tipo_sql}")
    colunas_sql_str = ",\n".join(colunas_sql)
    return f"CREATE TABLE `{nome_tabela}` (\n{colunas_sql_str}\n);"


def verificar_diferencas(colunas_dic: set, colunas_csv: set) -> tuple[set, set]:
    """Compara colunas normalizadas do CSV e dicionário."""
    faltando_no_csv = colunas_dic - colunas_csv
    extras_no_csv = colunas_csv - colunas_dic
    return faltando_no_csv, extras_no_csv


def substituir_siglas(df: pd.DataFrame) -> pd.DataFrame:
    """Substitui apenas as siglas OD e AMB pelas descrições completas."""
    SIGLAS_OD_AMB = {
        "OD": "Seg. Odontológica",
        "AMB": "Seg. Ambulatorial"
    }
    for col in df.columns:
        if col.strip().upper() in {"OD", "AMB"}:
            df[col] = df[col].replace(SIGLAS_OD_AMB, regex=True)
    return df


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
