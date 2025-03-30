# 🩺 IntuitiveCare - Desafio Técnico

Este projeto é composto por **4 etapas principais**, com foco em scraping, transformação de dados, banco de dados e API.

---

## 🚦 Etapas do Projeto

### ✅ Etapa 1 - Web Scraping
- Acessa a URL oficial da ANS
- Realiza o download dos anexos I e II (PDF)
- Compacta os dois arquivos em um `.zip` com seu nome
- Armazena os arquivos em `output/anexos/` e `output/zips/`

```bash
make etapa1
```

---

### ✅ Etapa 2 - Transformação de Dados
- Extrai o `.zip` da etapa 1
- Lê o PDF do Anexo I (Rol de Procedimentos)
- Extrai todas as tabelas com detecção automática
- Substitui siglas por descrições completas
- Gera o `.csv` e um novo `.zip` com nome padronizado
- Salva logs de falhas de leitura

```bash
make etapa2
```

---

### ✅ Etapa 3 - Banco de Dados (MySQL 8 via Docker)

#### Parte 1 - Identificação de Campos
- Compara o CSV com o dicionário `.ods`
- Gera `scripts.sql` para criar a tabela
- Loga as diferenças entre CSV e Dicionário

```bash
make etapa3-identify
```

#### Parte 2 - Criação do Banco e da Tabela
- Cria banco MySQL e tabela com base no script SQL

```bash
make etapa3-db
```

#### Parte 3 - Importação dos Dados
- Importa o CSV diretamente para a tabela MySQL

```bash
make etapa3-import
```

#### Parte 4 - Queries analíticas
- (Em andamento)

---

### ⏳ Etapa 4 - API com Vue.js + Python
- Criar backend em Python com busca textual
- Desenvolver frontend com Vue.js
- Integrar com banco populado
- (Em andamento)

---

## 🔍 Extra - Scanner de Páginas do PDF
Detecta automaticamente quais páginas possuem tabelas válidas no PDF do Anexo I.

```bash
make scan
```

---

## 🐳 Docker

O projeto usa Docker para rodar o MySQL. Para iniciar o container:

```bash
docker-compose up -d
```

### 🔁 Resetar o container e volume do MySQL
Para reiniciar o banco (inclusive executando novamente o init.sql):

```bash
make db-reset
```

---

## 🧪 Executar todas as etapas de uma vez

```bash
make all
```

---

## 🧹 Limpar arquivos gerados

```bash
make clean
```

---

## 📁 Estrutura de Pastas

```
.
├── scripts/              # Scripts Python
├── output/
│   ├── anexos/           # PDFs extraídos
│   ├── csv/              # CSV da Etapa 2
│   ├── logs/             # Logs de falhas e diferenças
│   ├── zips/             # Arquivos compactados
│   └── sql/              # Scripts SQL gerados
├── docker/
│   └── mysql/
│       └── init.sql      # Script para permissões e banco via container
├── tests/                # Testes unitários e manuais
├── docker-compose.yml    # MySQL 8 container
├── Makefile              # Automatizador de tarefas
├── .env                  # Configurações locais
├── .env.example          # Modelo base de variáveis
```

---

## ⚙️ Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=elidiogiacon
MYSQL_PASSWORD=elidiogiacon
MYSQL_DATABASE=intuitivecare_cadop

URL_ANEXOS=https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos
USER_AGENT=Mozilla/5.0 (...)
LOG_LEVEL=INFO
```

---

## 👨‍💻 Autor

Desenvolvido por **Elidio Giacon Neto** com foco em organização, automação e qualidade industrial em projetos de dados.
