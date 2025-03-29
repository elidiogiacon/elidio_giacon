# 📦 MySQL com Docker

Este projeto configura um container MySQL 8 utilizando Docker Compose, com credenciais e banco de dados já definidos para facilitar testes locais e provas técnicas.

---

## 🚀 Como rodar

### Pré-requisitos
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/install/) (já incluído no Docker Desktop)

### Passos

1. Clone ou baixe este repositório.
2. Navegue até a pasta do projeto:
   ```bash
   cd desafio-mysql
   ```

3. Inicie o container:
   ```bash
   docker-compose up -d
   ```

4. Pronto! O MySQL estará rodando localmente na porta `3306`.

---

## ⚙️ Configuração

O container é configurado através do arquivo `docker-compose.yml`. As principais variáveis de ambiente utilizadas são:

| Variável             | Descrição                              | Valor configurado          |
|----------------------|----------------------------------------|----------------------------|
| `MYSQL_ROOT_PASSWORD`| Senha do usuário root do MySQL         | `elidiogiacon`             |
| `MYSQL_DATABASE`     | Nome do banco de dados padrão criado   | `banco_desafio`            |
| `MYSQL_USER`         | Usuário padrão criado                  | `elidiogiacon`             |
| `MYSQL_PASSWORD`     | Senha do usuário padrão                | `elidiogiacon`             |

---

## 🗃️ Persistência de dados

Os dados do banco são persistidos através de um volume Docker chamado `mysql_data`, que armazena os arquivos em:

```
/var/lib/mysql
```

Isso garante que os dados não sejam perdidos ao reiniciar o container.

---

## 🧹 Como parar e remover

Para parar e remover o container:

```bash
docker-compose down
```

Para remover também os dados (volume):

```bash
docker-compose down -v
```

---

## ✅ Teste de conexão

Você pode testar a conexão com ferramentas como:
- DBeaver
- MySQL Workbench
- MySQL CLI

Utilize as seguintes informações:

- **Host:** `localhost`
- **Porta:** `3306`
- **Usuário:** `elidiogiacon`
- **Senha:** `elidiogiacon`
- **Banco:** `banco_desafio`

---

## 📄 Licença

Este projeto é livre para uso em testes, entrevistas e aprendizado.
