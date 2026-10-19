# Projeto PetVida — Camada de Acesso a Dados (Python & SQL Server)

Este repositório contém a implementação da camada de acesso a dados (DAO / Repositório) para o sistema da clínica veterinária PetVida, desenvolvida como parte da avaliação da disciplina de Banco de Dados / Engenharia de Software.

O projeto estabelece a comunicação entre uma aplicação Python e o SGBD Microsoft SQL Server utilizando a biblioteca `pyodbc`, respeitando integralmente o esquema relacional fornecido no script `01_estrutura_petvida.sql`.

---

## 📁 Estrutura do Projeto

- **`db.py`**: Módulo responsável pelo gerenciamento de conexões com o banco de dados (`montar_connection_string()`, `conectar()`, `testar_conexao()`) e pelo controle transacional atômico via `@contextmanager` (`transacao()`).
- **`repositorio.py`**: Concentra todas as operações de persistência e consulta (CRUD de Tutores, associação 1:N com Pets, mapeamento N:M de Consultas/Procedimentos e suporte a Views para histórico).
- **`main.py`**: Interface em linha de comando (CLI) para navegação interativa e testes operacionais do sistema.
- **`requirements.txt`**: Relação de dependências externas do projeto (`pyodbc`).
- **`01_estrutura_petvida.sql`**: Script DDL/DML para criação e povoamento inicial do banco de dados PetVida.

---

## 🛠️ Instruções de Instalação e Execução

### 1. Inicialização do Banco de Dados
Abra o SQL Server Management Studio (SSMS) e execute o arquivo `01_estrutura_petvida.sql`. Ao término da execução, confirme se a view de verificação retornou os 5 registros de consultas iniciais.

### 2. Configuração do Ambiente Python
No terminal na raiz do projeto, configure o ambiente virtual e instale as dependências:

```bash
# Criação e ativação do ambiente virtual
python -m venv venv
venv\Scripts\activate        # Linux/Mac: source venv/bin/activate

# Instalação das dependências
pip install -r requirements.txt

```

### 3. Configuração de Conexão

Por padrão, a aplicação utiliza a Autenticação Integrada do Windows apontando para a instância local `localhost\SQLEXPRESS` e banco `PetVida`.

Caso deseje personalizar o ambiente via variáveis de sistema, as seguintes chaves são suportadas:

* `PETVIDA_SERVER`: Endereço/instância do servidor SQL Server (Padrão: `localhost\SQLEXPRESS`).
* `PETVIDA_DATABASE`: Nome da base de dados (Padrão: `PetVida`).
* `PETVIDA_DRIVER`: Driver ODBC instalado (Padrão: `SQL Server` ou `ODBC Driver 18 for SQL Server`).
* `PETVIDA_USER` / `PETVIDA_PASSWORD`: Credenciais para Autenticação SQL (se não informadas, utiliza Autenticação Windows).

### 4. Execução da Aplicação

Inicie o menu interativo com o comando:

```bash
python main.py

```

---

## 🔒 Conformidade com os Requisitos Técnicos

* **Prevenção contra SQL Injection:** Todas as instruções SQL executadas utilizam consultas parametrizadas com marcadores `?`. Atualizações dinâmicas utilizam controle estrito por lista branca de colunas permitidas (`nome`, `email`, `telefone`).
* **Gerenciamento de Recursos e Transações:** Abertura, fechamento de cursores/conexões e confirmação de operações são garantidos pelo gerenciador de contexto `with transacao() as cur:`. O parâmetro `autocommit=False` assegura o controle atômico via `commit()` automático no sucesso e `rollback()` em caso de falhas/exceções.
* **Recuperação de Chaves Primárias:** Inserções utilizam a cláusula `OUTPUT INSERTED` para retornar o identificador numérico gerado automaticamente pelo campo `IDENTITY`.
* **Integridade do Esquema:** O código interage com o banco respeitando todas as chaves estrangeiras, restrições de unicidade (ex: CPF) e regras de integridade referencial configuradas no banco original.


