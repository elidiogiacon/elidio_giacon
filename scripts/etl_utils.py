import os
import json
import unicodedata
import difflib
import pandas as pd
import logging
from pathlib import Path
from typing import Any


def setup_logger(name: str, console: bool = False) -> logging.Logger:
    """
    Cria e configura um logger com nome único, com saída para arquivo e opcionalmente console.

    Args:
        name (str): Nome do logger.
        console (bool): Se True, adiciona também saída para o console.

    Returns:
        logging.Logger: Logger configurado.
    """
    logs_dir = Path("output") / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fh = logging.FileHandler(logs_dir / f"{name}.log", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        if console:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

    return logger


def normalizar_texto(texto: str) -> str:
    """
    Remove acentuação e converte para ASCII plano.

    Args:
        texto (str): Texto original.

    Returns:
        str: Texto normalizado.
    """
    if not isinstance(texto, str):
        return texto
    texto = unicodedata.normalize("NFKD", texto)
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return texto.encode("ascii", "ignore").decode("utf-8").strip().lower()


def normalizar_nome_coluna(nome: str) -> str:
    """
    Normaliza nome de coluna para fins de comparação:
    remove acentos, espaços e underscores.

    Exemplo:
        "Nome do_Campo" -> "nomedocampo"
    """
    if not isinstance(nome, str):
        return nome
    nome = normalizar_texto(nome)
    return nome.replace(" ", "").replace("_", "")


def localizar_coluna(df: pd.DataFrame, alvo: str) -> str:
    """
    Localiza o nome real de uma coluna em um DataFrame com base em variações leves.

    Args:
        df (pd.DataFrame): DataFrame com colunas reais.
        alvo (str): Nome da coluna desejada.

    Returns:
        str: Nome original da coluna encontrada.
    """
    alvo_normalizado = normalizar_nome_coluna(alvo)

    for col in df.columns:
        if normalizar_nome_coluna(col) == alvo_normalizado:
            return col

    # Tenta encontrar correspondência aproximada se não houver exata
    opcoes = {col: normalizar_nome_coluna(col) for col in df.columns}
    possivel = difflib.get_close_matches(alvo_normalizado, opcoes.values(), n=1, cutoff=0.8)
    if possivel:
        for col, norm in opcoes.items():
            if norm == possivel[0]:
                return col

    raise KeyError(f"❌ Coluna esperada '{alvo}' não encontrada no DataFrame.")


def mapear_tipo(tipo: str, tamanho) -> str:
    """
    Mapeia tipo do dicionário para tipo SQL.

    Args:
        tipo (str): Tipo vindo do dicionário.
        tamanho (Any): Tamanho do campo, se aplicável.

    Returns:
        str: Tipo SQL formatado.
    """
    tipo = normalizar_texto(tipo)
    if tipo == "texto":
        valor_tamanho = int(tamanho) if (tamanho and not pd.isna(tamanho)) else 255
        return f"VARCHAR({valor_tamanho})"
    elif tipo == "numero":
        return "INT"
    elif tipo == "data":
        return "DATE"
    return "VARCHAR(255)"


def gerar_create_table(df: pd.DataFrame, nome_tabela: str) -> str:
    """
    Gera a instrução SQL para criação de uma tabela com base no dicionário de dados.

    As colunas do dicionário são localizadas automaticamente, considerando variações.

    Args:
        df (pd.DataFrame): Dicionário.
        nome_tabela (str): Nome da tabela.

    Returns:
        str: Comando SQL completo.
    """
    coluna_nome = localizar_coluna(df, "nome_do_campo")
    coluna_tipo = localizar_coluna(df, "tipo")
    coluna_tamanho = localizar_coluna(df, "tamanho")

    colunas_sql = []
    for _, row in df.iterrows():
        # Normaliza o nome da coluna para uso no SQL (mantendo underscores para separação)
        nome_coluna = normalizar_texto(str(row[coluna_nome])).replace(" ", "_")
        tipo_str = str(row[coluna_tipo])
        tamanho = row.get(coluna_tamanho, None)
        tipo_sql = mapear_tipo(tipo_str, tamanho)
        colunas_sql.append(f"  `{nome_coluna}` {tipo_sql}")
    colunas_sql_str = ",\n".join(colunas_sql)
    return f"CREATE TABLE `{nome_tabela}` (\n{colunas_sql_str}\n);"


def verificar_diferencas(colunas_dic: set, colunas_csv: set) -> tuple[set, set]:
    """
    Compara as colunas (normalizadas) do dicionário e do CSV.

    Retorna duas tuplas:
      - Colunas presentes no dicionário, mas ausentes no CSV.
      - Colunas extras presentes no CSV que não constam no dicionário.
    """
    # Normaliza os nomes para comparação
    norm_dic = {normalizar_nome_coluna(col) for col in colunas_dic}
    norm_csv = {normalizar_nome_coluna(col) for col in colunas_csv}
    faltando_no_csv = norm_dic - norm_csv
    extras_no_csv = norm_csv - norm_dic
    return faltando_no_csv, extras_no_csv


def substituir_siglas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Substitui as siglas 'OD' e 'AMB' pelas descrições completas
    em todas as colunas que contenham esses valores.
    """
    SIGLAS_OD_AMB = {
        "OD": "Seg. Odontológica",
        "AMB": "Seg. Ambulatorial"
    }
    # Para cada coluna do DataFrame, se for do tipo objeto (texto), realiza a substituição
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].replace(SIGLAS_OD_AMB, regex=True)
    return df


def exportar_log_diferencas(path: str, faltando: set, extras: set, alias_map: dict):
    """
    Gera um log detalhado das diferenças entre o dicionário e o CSV.

    - 'faltando': conjunto de colunas esperadas (normalizadas) que não foram encontradas no CSV.
    - 'extras': conjunto de colunas extras (normalizadas) encontradas no CSV.
    - 'alias_map': mapeamento de substituições manuais (se houver).
    """
    with open(path, "w", encoding="utf-8") as log:
        log.write("📌 Diferenças detectadas entre CSV e Dicionário de Dados:\n\n")

        if faltando:
            log.write("⚠️  Colunas no dicionário mas ausentes no CSV:\n")
            for col in sorted(faltando):
                log.write(f"  - {col}\n")
        else:
            log.write("✅ Todas as colunas do dicionário estão presentes no CSV.\n")

        if extras:
            log.write("\n⚠️  Colunas no CSV que não existem no dicionário:\n")
            for col in sorted(extras):
                log.write(f"  - {col}\n")
        else:
            log.write("✅ Nenhuma coluna extra no CSV.\n")

        if alias_map:
            log.write("\n🔁 Substituições manuais (alias aplicados):\n")
            for original, substituto in alias_map.items():
                log.write(f"  - '{original}' foi considerado equivalente a '{substituto}'\n")

def salvar_truncamentos_em_arquivo(truncamentos: list[dict], nome_arquivo: str):
    """
    Salva os dados de truncamentos em um arquivo JSON.

    Parâmetros:
    - truncamentos: Lista de dicionários com colunas e valores truncados.
    - nome_arquivo: Caminho do arquivo onde será salvo o JSON.
    """
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(truncamentos, f, ensure_ascii=False, indent=2)
        print(f"✅ Truncamentos salvos em: {nome_arquivo}")
    except Exception as e:
        print(f"❌ Erro ao salvar truncamentos em JSON: {e}")

def carregar_truncamentos_do_arquivo(path="output/sql/truncamentos.json") -> dict:
    """
    Carrega o arquivo JSON de truncamentos.

    Args:
        path (str): Caminho até o arquivo JSON.

    Returns:
        dict: Dados carregados do JSON.
    """
    trunc_path = Path(path)
    if not trunc_path.exists():
        raise FileNotFoundError(f"Arquivo de truncamentos não encontrado: {trunc_path}")
    with open(trunc_path, "r", encoding="utf-8") as f:
        return json.load(f)
