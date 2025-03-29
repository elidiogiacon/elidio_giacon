# 🧪 Desafio Técnico – IntuitiveCare

Este projeto foi desenvolvido como parte de uma prova técnica para a empresa **IntuitiveCare**.

O objetivo principal é manipular e analisar dados de operadoras de saúde, estruturando-os em um banco de dados relacional (MySQL), com etapas automatizadas via Python, Docker e Makefile.

## 📚 Índice

- [📦 Infraestrutura Docker + MySQL](#-infraestrutura-docker--mysql)
- [🚀 Como rodar](#-como-rodar)
- [⚙️ Configuração](#-configuração)
- [📂 Estrutura do Projeto](#-estrutura-do-projeto)
- [🧩 Etapas do Desafio](#-etapas-do-desafio)
- [🛠️ Comandos disponíveis (Makefile)](#️-comandos-disponíveis-makefile)
- [✅ Teste de conexão](#-teste-de-conexão)
- [📄 Licença](#-licença)

## 📦 Infraestrutura Docker + MySQL

Este projeto utiliza um container MySQL configurado com Docker Compose:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8
    container_name: mysql_server
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: elidiogiacon
      MYSQL_DATABASE: banco_desafio
      MYSQL_USER: elidiogiacon
      MYSQL_PASSWORD: elidiogiacon
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

## 🚀 Como rodar

1. Suba o container MySQL:
```bash
docker-compose up -d
```

2. Instale as dependências do Python:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env` com suas variáveis de conexão ao banco de dados.

4. Execute os comandos via Makefile (ver abaixo).

## ⚙️ Configuração

Crie um arquivo `.env` na raiz com os seguintes campos:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=elidiogiacon
MYSQL_PASSWORD=elidiogiacon
MYSQL_DATABASE=intuitivecare_cadop
```

## 📂 Estrutura do Projeto

```bash
.
├── docker-compose.yml
├── .env
├── scripts/
│   ├── identify_fields.py
│   ├── create_database_and_tables.py
│   ├── etl_utils.py
│   ├── scripts.sql
│   ├── diff_log.txt
├── etapa3/
│   ├── Relatorio_cadop.csv
│   ├── dicionario_de_dados_das_operadoras_ativas.ods
├── Makefile
├── requirements.txt
└── README.md
```

## 🧩 Etapas do Desafio

### 🥇 Etapa 1
- Acessar um site e baixar 2 arquivos `.pdf`.
- Compactar ambos em um `.zip` com o nome do candidato.

### 🥈 Etapa 2
- Ler um dos PDFs baixados.
- Identificar e extrair tabelas.
- Salvar as tabelas em um arquivo `.csv`, corrigindo abreviações.

### 🥉 Etapa 3 (atual)
- Ler o dicionário de dados (`.ods`) e o relatório (`.csv`)
- Gerar um script `CREATE TABLE` conforme o dicionário
- Verificar divergências entre colunas
- Criar o banco e as tabelas automaticamente no MySQL

## 🛠️ Comandos disponíveis (Makefile)

| Comando        | Descrição                                     |
|----------------|-----------------------------------------------|
| `make run`     | Executa o script de geração do SQL            |
| `make db`      | Cria o banco e as tabelas no MySQL            |
| `make sql`     | Exibe o conteúdo do script SQL gerado         |
| `make diff`    | Mostra as diferenças entre CSV e dicionário   |
| `make clean`   | Remove arquivos temporários (`.sql`, `.txt`)  |

## ✅ Teste de conexão

- Acesse o container ou use um cliente MySQL para testar:
```bash
mysql -u elidiogiacon -p -h 127.0.0.1 -P 3306
```
- **Banco:** `intuitivecare_cadop`

## 📄 Licença

Uso exclusivo para fins de avaliação técnica.
