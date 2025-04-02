from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import pandas as pd
import unicodedata
import json
import numpy as np

app = FastAPI()

# === CORS para testes locais com front ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Carrega o CSV uma vez ===
CADASTRO_PATH = Path(__file__).resolve().parent.parent / "input" / "Relatorio_cadop.csv"

CAMPO_BUSCA = "razao_social"
df_operadoras = pd.read_csv(CADASTRO_PATH, sep=";", encoding="utf-8")
df_operadoras.columns = [col.strip().lower().replace(" ", "_") for col in df_operadoras.columns]

print(f"✅ CSV carregado com encoding: utf-8")
print(f"📦 CSV de operadoras carregado com {len(df_operadoras)} registros")


def normalizar(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()


@app.get("/operadoras", summary="Busca textual nas operadoras")
def buscar_operadoras(q: str = Query(..., description="Termo de busca textual")):
    termo = normalizar(q)
    df_filtrado = df_operadoras[df_operadoras[CAMPO_BUSCA].apply(lambda x: termo in normalizar(x))]

    # 👇 Substitui NaN por None para ser JSON-safe
    df_filtrado = df_filtrado.replace({np.nan: None})

    resultados = df_filtrado.head(10).to_dict(orient="records")

    return {
        "query": q,
        "total": len(resultados),
        "resultados": resultados
    }