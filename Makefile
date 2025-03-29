# Variáveis
PYTHON=python
SCRIPTS_DIR=scripts

# Comando para rodar o identify_fields.py
run:
	@echo "▶️ Executando script de verificação de campos..."
	$(PYTHON) $(SCRIPTS_DIR)/identify_fields.py

# Comando para criar banco + tabelas
db:
	@echo "🏗️ Criando banco de dados e tabelas..."
	$(PYTHON) $(SCRIPTS_DIR)/create_database_and_tables.py

# Exibir o conteúdo do script SQL
sql:
	@echo "📜 Conteúdo do scripts.sql:"
	@cat $(SCRIPTS_DIR)/scripts.sql

# Exibir diferenças encontradas
diff:
	@echo "🔍 Diferenças entre CSV e Dicionário:"
	@cat $(SCRIPTS_DIR)/diff_log.txt

# Limpa os arquivos gerados
clean:
	@echo "🧹 Limpando arquivos gerados..."
	@rm -f $(SCRIPTS_DIR)/scripts.sql
	@rm -f $(SCRIPTS_DIR)/diff_log.txt

# Ajuda
help:
	@echo "🛠️  Comandos disponíveis:"
	@echo "  make run     → Executa identify_fields.py"
	@echo "  make db      → Cria o banco e as tabelas no MySQL"
	@echo "  make sql     → Mostra o conteúdo do SQL gerado"
	@echo "  make diff    → Mostra diferenças CSV vs Dicionário"
	@echo "  make clean   → Remove arquivos temporários"
