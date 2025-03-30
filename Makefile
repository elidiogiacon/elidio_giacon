# =========================
# Variáveis
# =========================
PYTHON = python
SCRIPTS_DIR = scripts
ROOT = $(shell pwd)
export PYTHONPATH = $(ROOT)

# =========================
# Etapa 1 - Web Scraping
# =========================
etapa1:
	@echo "🌐 Executando Etapa 1 - Download e Compactação de Anexos..."
	$(PYTHON) -m $(SCRIPTS_DIR).download_anexos

# =========================
# Etapa 2 - Transformação de Dados
# =========================
etapa2:
	@echo "📄 Executando Etapa 2 - Extração de Tabelas do PDF..."
	$(PYTHON) -m $(SCRIPTS_DIR).extract_tables

# =========================
# Etapa 3.1 - Identificação de Campos
# =========================
etapa3-identify:
	@echo "🧠 Executando Etapa 3.1 - Verificando estrutura de campos..."
	$(PYTHON) -m $(SCRIPTS_DIR).identify_fields

# =========================
# Etapa 3.2 - Criação do Banco e Tabela
# =========================
etapa3-db:
	@echo "🏗️ Executando Etapa 3.2 - Criando banco e tabela no MySQL..."
	$(PYTHON) -m $(SCRIPTS_DIR).create_database_and_tables

# =========================
# Etapa 3.3 - Importação do CSV para o MySQL
# =========================
etapa3-import:
	@echo "📥 Executando Etapa 3.3 - Importando CSV para o MySQL..."
	$(PYTHON) -m $(SCRIPTS_DIR).import_csv_to_mysql

# =========================
# Etapa 4 - API (placeholder)
# =========================
etapa4-api:
	@echo "🔧 Executando Etapa 4 - Backend/Frontend em desenvolvimento..."

# =========================
# Scanner de páginas com tabelas no PDF
# =========================
scan:
	@echo "🔎 Executando Scanner de Páginas com Tabelas no PDF..."
	$(PYTHON) -m $(SCRIPTS_DIR).scan_pdf_tables

# =========================
# Ver conteúdo SQL gerado
# =========================
sql:
	@echo "📜 Conteúdo do scripts.sql:"
	@cat output/sql/scripts.sql

# =========================
# Ver diferenças CSV vs Dicionário
# =========================
diff:
	@echo "🔍 Diferenças detectadas entre CSV e Dicionário:"
	@cat output/logs/diff_log.txt

# =========================
# Limpar arquivos gerados
# =========================
clean:
	@echo "🧹 Limpando arquivos gerados..."
	@rm -f output/sql/scripts.sql
	@rm -f output/logs/diff_log.txt
	@rm -f output/logs/etapa2_failures.log
	@rm -f output/csv/*.csv
	@rm -f output/zips/*.zip
	@rm -f output/anexos/*.pdf

# =========================
# Resetar o banco de dados (MySQL)
# =========================
db-reset:
	@echo "🔁 Resetando o banco de dados e volume do MySQL..."
	docker-compose down -v
	docker-compose up -d

# =========================
# Rodar todas as etapas
# =========================
all: etapa1 etapa2 etapa3-identify etapa3-db etapa3-import

# =========================
# Ajuda
# =========================
help:
	@echo "🛠️ Comandos disponíveis:"
	@echo "  make etapa1           → Baixa PDFs e gera ZIP (Etapa 1)"
	@echo "  make etapa2           → Extrai tabelas do PDF, gera CSV e ZIP (Etapa 2)"
	@echo "  make etapa3-identify  → Verifica campos e gera scripts.sql (Etapa 3.1)"
	@echo "  make etapa3-db        → Cria banco e tabelas no MySQL (Etapa 3.2)"
	@echo "  make etapa3-import    → Importa dados do CSV para o MySQL (Etapa 3.3)"
	@echo "  make etapa4-api       → (placeholder) Rota de API com busca textual (Etapa 4)"
	@echo "  make scan             → Detecta páginas com tabelas no PDF"
	@echo "  make sql              → Mostra conteúdo do SQL"
	@echo "  make diff             → Mostra diferenças entre CSV e Dicionário"
	@echo "  make clean            → Remove arquivos temporários"
	@echo "  make all              → Executa todas as etapas anteriores"
	@echo "  make db-reset         → Remove volume do MySQL e reinicia container"
