# 🩺 IntuitiveCare - Desafio Técnico

Projeto dividido em **4 grandes etapas**, com foco em scraping, transformação, banco de dados e API. Modularizado, automatizado e com padrão de qualidade industrial.

---

## 🚦 Etapas do Projeto

### ✅ Etapa 1 - Web Scraping de Anexos
- Baixa os arquivos Anexo I e II da ANS (.pdf)
- Compacta em `.zip` nomeado
- Armazena em `output/anexos/` e `output/zips/`

```bash
make etapa1
```

---

### ✅ Etapa 2 - Extração e Transformação de Tabelas
- Extrai os `.pdf` da Etapa 1
- Detecta páginas com tabelas automaticamente
- Extrai conteúdo com `pdfplumber`
- Substitui siglas e exporta para `.csv` e `.zip`
- Loga falhas de leitura

```bash
make etapa2
```

---

### ✅ Etapa 3 - Banco de Dados com MySQL 8 (Docker)

#### 📥 Etapa 3.0 - Download de Dados Complementares
- Baixa arquivos da ANS: `Relatorio_cadop.csv` e `.zip` contábeis
- Armazena em `input/`

```bash
make etapa3-downloader
```

#### 🧠 Etapa 3.1 - Identificação de Campos
- Compara CSV e dicionário `.ods`
- Gera `scripts.sql` com estrutura da tabela
- Loga divergências de colunas

```bash
make etapa3-identify
```

#### 🏗️ Etapa 3.2 - Criação do Banco e Tabela
- Usa `.env` e Docker para conectar no MySQL
- Executa script SQL

```bash
make etapa3-db
```

#### 📤 Etapa 3.3 - Importação do CSV no MySQL
- Importa o `Relatorio_cadop.csv` para o banco criado

```bash
make etapa3-import
```

### 🚧 Etapa 3.5 - Query Analítica

Por limitação de tempo (semana de provas na faculdade + jornada atual de trabalho de 40h), **não consegui concluir a query analítica solicitada**.

No entanto, a estrutura de banco e o dataset estão prontos para que ela seja desenvolvida com facilidade, conforme o enunciado do desafio.

Caso seja relevante para a avaliação, fico à disposição para desenvolver a consulta caso me concedam prazo adicional de 1 dia.

Agradeço pela compreensão.

---

### ⏳ Etapa 4 - API com Vue.js + Python
- Backend com busca textual (Python)
- Frontend em Vue.js

```bash
make etapa4-api     # Inicia a API FastAPI (porta 8000)
make etapa4-front   # Abre a interface Vue no navegador (porta 5173)
```

---

## 🔍 Extra - Scanner de Tabelas no PDF
Detecta automaticamente páginas com tabelas no PDF.

```bash
make scan
```

---

## 🐳 Docker

Iniciar banco de dados:

```bash
docker-compose up -d
```

### 🔁 Resetar banco e volume Docker

```bash
make db-reset
```

---

## ✅ Executar tudo de uma vez

```bash
make all
```

---

## 🧹 Limpeza de arquivos gerados

```bash
make clean
```

---

## 🧭 Organização do Projeto

```
├── scripts/                # Scripts Python (ETL)
├── api/                   # FastAPI backend
│   ├── main.py            # Ponto de entrada da API
│   ├── routes/            # Rotas da API
│   ├── services/          # Lógicas de negócio
│   └── models/            # Estruturas de dados
├── frontend/              # Aplicação Vue.js (Vite)
│   ├── index.html         # Entrada do app
│   ├── src/               # Código-fonte Vue (composables, views, etc.)
│   └── vite.config.js     # Configuração do Vite
├── output/
│   ├── anexos/            # PDFs extraídos
│   ├── csv/               # Arquivos gerados
│   ├── logs/              # Logs da execução
│   ├── zips/              # ZIPs nomeados
│   └── sql/               # Scripts .sql gerados
├── input/                 # Arquivos CADOP, ODS e .zip externos
├── docker/
│   └── mysql/init.sql     # Script inicial do banco
├── docker-compose.yml     # Docker MySQL 8
├── tests/                 # Testes com Pytest
├── Makefile               # Automação das etapas
├── .env                   # Configurações locais (não versionado)
├── .env.example           # Modelo base
└── README.md              # Este arquivo
```

---

## ⚙️ Variáveis de Ambiente

Crie um `.env` com base no `.env.example`. Exemplo:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=usuario
MYSQL_PASSWORD=senha
MYSQL_DATABASE=banco

URL_ANEXOS=https://www.gov.br/ans/pt-br/acesso-a-informacao/...
URL_CADOP=https://dadosabertos.ans.gov.br/FTP/PDA/...
URL_DEMONSTRATIVOS=https://dadosabertos.ans.gov.br/FTP/PDA/...

DEMO_ANOS_RETROATIVOS=2
USER_AGENT=Mozilla/5.0 (...)
LOG_LEVEL=INFO
```

---

## ⚠️ Nota técnica:

A API atual carrega o CSV em memória, o que é adequado para testes e protótipos locais. Estou ciente de que essa abordagem pode não escalar bem em produção.

Optei por essa implementação por conta da concorrência com atual trabalho, semana de provas na faculdade e prazo reduzido.

Se tivesse mais um dia, faria a migração para uma busca via banco de dados com consultas otimizadas, chunked reads ou Redis.

Ainda assim, todas as decisões foram conscientes e justificadas dentro do escopo e tempo proposto.


## 👨‍💻 Autor

Desenvolvido por **Elidio Giacon Neto** com foco em automação, clareza e excelência técnica.