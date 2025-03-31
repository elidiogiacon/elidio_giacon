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
	@echo "🌐 Etapa 1 - Download e Compactação de Anexos da ANS"
	$(PYTHON) -m $(SCRIPTS_DIR).download_anexos

# =========================
# Etapa 2 - Transformação de Dados
# =========================
etapa2:
	@echo "📄 Etapa 2 - Extração e Limpeza de Tabelas do PDF"
	$(PYTHON) -m $(SCRIPTS_DIR).extract_tables

# =========================
# Etapa 3.0 - Coleta de Dados Complementares
# =========================
etapa3-downloader:
	@echo "📥 Etapa 3.0 - Download de Dados da ANS (CADOP + Demonstrativos Contábeis)"
	$(PYTHON) -m $(SCRIPTS_DIR).download_dados_operadoras
	$(PYTHON) -m $(SCRIPTS_DIR).download_demonstracoes_contabeis

# =========================
# Etapa 3.1 - Validação e Identificação de Campos
# =========================
etapa3-identify:
	@echo "🧠 Etapa 3.1 - Análise do Dicionário e CSV de Operadoras"
	$(PYTHON) -m $(SCRIPTS_DIR).identify_fields

# =========================
# Etapa 3.2 - Criação do Banco de Dados e Tabelas
# =========================
etapa3-db:
	@echo "🏗️ Etapa 3.2 - Criação de banco e execução do script SQL"
	$(PYTHON) -m $(SCRIPTS_DIR).create_database_and_tables

# =========================
# Etapa 3.3 - Importação de Dados no MySQL
# =========================
etapa3-import:
	@echo "📤 Etapa 3.3 - Importação do CSV para a tabela MySQL"
	$(PYTHON) -m $(SCRIPTS_DIR).import_csv_to_mysql

# =========================
# Etapa 3.4 - Processamento de Despesas Contábeis
# =========================
etapa3-despesas:
	@echo "📊 Etapa 3.4 - Processamento das Despesas Contábeis"
	$(PYTHON) -m $(SCRIPTS_DIR).processar_despesas
	$(PYTHON) -m $(SCRIPTS_DIR).import_despesas_to_mysql

# =========================
# Etapa 4 - Visualização (API + Frontend)
# =========================

etapa4-api:
	@echo "🚀 Iniciando API com FastAPI (localhost:8000)"
	cd api && uvicorn main:app --reload

etapa4-frontend:
	@echo "🎨 Iniciando Frontend Vue (localhost:5173)"
	cd frontend && npm run dev

etapa4:
	@echo "🌐 Etapa 4 - Executando API e Frontend (paralelamente)"
	(cd api && uvicorn main:app --reload) & \
	(cd frontend && npm run dev) & \
	wait

# =========================
# Scanner de Páginas com Tabelas (PDF)
# =========================
scan:
	@echo "🔎 Scanner de Tabelas no PDF (Etapa Extra)"
	$(PYTHON) -m $(SCRIPTS_DIR).scan_pdf_tables

# =========================
# Visualização
# =========================
sql:
	@echo "📜 Visualizando conteúdo do scripts.sql"
	@cat output/sql/scripts.sql

diff:
	@echo "📋 Diferenças entre o dicionário de dados e o CSV"
	@cat output/logs/diff_log.txt

# =========================
# Limpeza
# =========================
clean:
	@echo "🧹 Limpando arquivos gerados durante a execução"
	@rm -f output/sql/scripts.sql
	@rm -f output/logs/*.log
	@rm -f output/csv/*.csv
	@rm -f output/zips/*.zip
	@rm -f output/anexos/*.pdf

# =========================
# Banco de Dados - Reset Total
# =========================
db-reset:
	@echo "🔁 Resetando container e volume do banco MySQL (Docker)"
	docker-compose down -v
	docker-compose up -d

# =========================
# Geração Automática do init.sql a partir do .env
# =========================
init-sql:
	@echo "⚙️ Gerando docker/mysql/init.sql baseado no .env..."
	$(PYTHON) generate_init_sql.py

# =========================
# Execução Total
# =========================
all: etapa1 etapa2 etapa3-downloader etapa3-identify etapa3-db etapa3-import etapa3-despesas

all-clean: clean db-reset init-sql all

# =========================
# Verificação de Pré-Requisitos
# =========================
check:
	@echo "🔍 Verificando pré-requisitos do ambiente..."
	@test -f .env || (echo '❌ Arquivo .env não encontrado!' && exit 1)
	@test -f docker-compose.yml || (echo '❌ docker-compose.yml não encontrado!' && exit 1)
	@mkdir -p output/logs output/csv output/sql output/zips output/anexos || true
	@echo '✅ Ambiente verificado com sucesso.'

# =========================
# Ajuda
# =========================
help:
	@echo "🛠️ Comandos disponíveis:"
	@echo "  make check              → Verifica estrutura mínima do projeto"
	@echo "  make init-sql           → Gera docker/mysql/init.sql a partir do .env"
	@echo "  make etapa1             → Baixa PDFs da ANS e gera ZIP"
	@echo "  make etapa2             → Extrai e transforma tabelas do PDF"
	@echo "  make etapa3-downloader  → Baixa arquivos CADOP e .zip da ANS"
	@echo "  make etapa3-identify    → Valida estrutura CSV com dicionário"
	@echo "  make etapa3-db          → Cria banco de dados com base no .sql"
	@echo "  make etapa3-import      → Importa dados do CSV para MySQL"
	@echo "  make etapa3-despesas    → Processa e importa despesas contábeis"
	@echo "  make etapa4-api         → Inicia construção da API + Frontend"
	@echo "  make scan               → Escaneia PDF para detectar páginas com tabelas"
	@echo "  make sql                → Exibe o script SQL gerado"
	@echo "  make diff               → Mostra diferenças entre CSV e Dicionário"
	@echo "  make clean              → Remove arquivos temporários"
	@echo "  make db-reset           → Reseta o volume Docker e reinicia o MySQL"
	@echo "  make all                → Executa todas as etapas do projeto"
	@echo "  make all-clean          → Limpa tudo e executa o pipeline completo"