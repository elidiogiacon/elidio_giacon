-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS intuitivecare;

-- Criação do usuário
CREATE USER IF NOT EXISTS 'elidiogiacon'@'%' IDENTIFIED BY 'elidiogiacon';

-- Permissões para o banco
GRANT ALL PRIVILEGES ON intuitivecare.* TO 'elidiogiacon'@'%';

-- Aplica as permissões
FLUSH PRIVILEGES;