import os
from contextlib import contextmanager
import pyodbc

def montar_connection_string():
    """Cria a string de conexão priorizando variáveis de ambiente com fallback para desenvolvimento local."""
    driver = os.environ.get("PETVIDA_DRIVER", "SQL Server")
    servidor = os.environ.get("PETVIDA_SERVER", r"localhost\SQLEXPRESS")
    banco = os.environ.get("PETVIDA_DATABASE", "PetVida")
    usuario = os.environ.get("PETVIDA_USER")
    senha = os.environ.get("PETVIDA_PASSWORD")

    conn_str = (
        f"Driver={{{driver}}};"
        f"Server={servidor};"
        f"Database={banco};"
        "TrustServerCertificate=yes;"
    )
    if usuario:
        conn_str += f"UID={usuario};PWD={senha or ''};"
    else:
        conn_str += "Trusted_Connection=yes;"
    return conn_str

def conectar():
    """Abre e retorna uma nova conexão com autocommit desativado para gerenciamento transacional explícito."""
    return pyodbc.connect(montar_connection_string(), autocommit=False)

def testar_conexao():
    """Consulta informações essenciais do ambiente SQL Server para validação de conectividade."""
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT @@SERVERNAME, DB_NAME(), @@VERSION")
        linha = cursor.fetchone()
        return {
            "servidor": linha[0],
            "banco": linha[1],
            "versao": linha[2].split("\n")[0],
        }
    finally:
        cursor.close()
        conn.close()

@contextmanager
def transacao():
    """Gerenciador de contexto que gerencia o ciclo de vida do cursor e da transação no banco.
    
    Efetua commit automaticamente ao concluir com sucesso ou rollback em caso de falha.
    """
    conn = conectar()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()