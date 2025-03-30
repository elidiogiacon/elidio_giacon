
import pdfplumber
from pathlib import Path
import logging

def detectar_paginas_com_tabelas(pdf_path: Path) -> list[int]:
    paginas_validas = []
    if not pdf_path.exists():
        logging.warning(f"Arquivo não encontrado: {pdf_path}")
        return []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            try:
                table = page.extract_table()
                if table and len(table) > 1 and len(table[0]) > 2:
                    paginas_validas.append(i + 1)
            except Exception as e:
                logging.warning(f"Erro na página {i + 1}: {e}")
    return paginas_validas

def main():
    pdf_path = Path("output/anexos/Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf")
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    paginas = detectar_paginas_com_tabelas(pdf_path)

    if not paginas:
        logging.warning("⚠️ Nenhuma tabela válida foi detectada.")
        return

    logging.info(f"✅ Tabelas detectadas de {paginas[0]} até {paginas[-1]} ({len(paginas)} páginas)")
    log_path = Path("output/logs/scan_pdf_pages.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Detectadas tabelas nas páginas:\n{paginas}\n")
        f.write(f"\nPrimeira página com tabela: {paginas[0]}")
        f.write(f"\nÚltima página com tabela: {paginas[-1]}")

if __name__ == "__main__":
    main()
