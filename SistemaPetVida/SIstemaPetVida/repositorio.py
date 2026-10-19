from db import transacao

class ErroNegocio(Exception):
    """Exceção para erros de validação de regras de negócio ou de integridade do banco."""
    pass

CAMPOS_TUTOR_PERMITIDOS = ("nome", "email", "telefone")
STATUS_CONSULTA_VALIDOS = ("AGENDADA", "REALIZADA", "CANCELADA")

def criar_tutor(nome, cpf, email=None, telefone=None):
    """Cadastra um novo tutor validando o formato do CPF e retorna o ID gerado."""
    if not cpf.isdigit() or len(cpf) != 11:
        raise ErroNegocio("CPF inválido: certifique-se de informar 11 dígitos numéricos.")
    
    with transacao() as cur:
        try:
            cur.execute(
                "INSERT INTO dbo.tutor (nome, cpf, email, telefone) "
                "OUTPUT INSERTED.id_tutor VALUES (?, ?, ?, ?)",
                (nome, cpf, email, telefone)
            )
            return cur.fetchone()[0]
        except Exception as e:
            raise ErroNegocio(f"Falha ao cadastrar tutor: {e}")

def buscar_tutor(id_tutor):
    """Retorna o cadastro completo do tutor correspondente ao ID informado."""
    with transacao() as cur:
        cur.execute(
            "SELECT id_tutor, nome, cpf, email, telefone, data_cadastro "
            "FROM dbo.tutor WHERE id_tutor = ?", 
            (id_tutor,)
        )
        return cur.fetchone()

def listar_tutores(filtro_nome=""):
    """Lista tutores ordenados por nome utilizando busca parcial parametrizada."""
    with transacao() as cur:
        cur.execute(
            "SELECT id_tutor, nome, cpf, email, telefone "
            "FROM dbo.tutor WHERE nome LIKE ? ORDER BY nome",
            (f"%{filtro_nome}%",)
        )
        return cur.fetchall()

def atualizar_tutor(id_tutor, **campos):
    """Atualiza atributos do tutor controlados por uma lista branca de colunas permitidas."""
    if not campos:
        raise ErroNegocio("Pelo menos um campo deve ser fornecido para atualização.")
    
    for campo in campos:
        if campo not in CAMPOS_TUTOR_PERMITIDOS:
            raise ErroNegocio(f"O campo '{campo}' não é permitido para alteração.")

    clausula_set = ", ".join(f"{campo} = ?" for campo in campos)
    parametros = list(campos.values()) + [id_tutor]
    
    with transacao() as cur:
        cur.execute(f"UPDATE dbo.tutor SET {clausula_set} WHERE id_tutor = ?", parametros)
        if cur.rowcount == 0:
            raise ErroNegocio("Tutor não encontrado para atualização.")

def excluir_tutor(id_tutor):
    """Remove o cadastro do tutor se não houver impedimentos de integridade referencial."""
    with transacao() as cur:
        try:
            cur.execute("DELETE FROM dbo.tutor WHERE id_tutor = ?", (id_tutor,))
            if cur.rowcount == 0:
                raise ErroNegocio("Tutor não encontrado.")
        except Exception as e:
            raise ErroNegocio(f"Não foi possível excluir o tutor: {e}")

def criar_pet(id_tutor, nome, especie, raca=None, data_nascimento=None, peso_kg=None):
    """Registra um novo pet associado a um tutor existente."""
    with transacao() as cur:
        try:
            cur.execute(
                "INSERT INTO dbo.pet (id_tutor, nome, especie, raca, data_nascimento, peso_kg) "
                "OUTPUT INSERTED.id_pet VALUES (?, ?, ?, ?, ?, ?)",
                (id_tutor, nome, especie, raca, data_nascimento, peso_kg)
            )
            return cur.fetchone()[0]
        except Exception as e:
            raise ErroNegocio(f"Falha ao registrar pet: {e}")

def atualizar_peso_pet(id_pet, peso_kg):
    """Atualiza a informação de peso do pet."""
    with transacao() as cur:
        cur.execute("UPDATE dbo.pet SET peso_kg = ? WHERE id_pet = ?", (peso_kg, id_pet))
        if cur.rowcount == 0:
            raise ErroNegocio("Pet não localizado.")

def transferir_pet(id_pet, novo_id_tutor):
    """Altera o tutor responsável pelo pet."""
    with transacao() as cur:
        try:
            cur.execute("UPDATE dbo.pet SET id_tutor = ? WHERE id_pet = ?", (novo_id_tutor, id_pet))
            if cur.rowcount == 0:
                raise ErroNegocio("Pet não localizado.")
        except Exception as e:
            raise ErroNegocio(f"Erro ao transferir responsabilidade do pet: {e}")

def excluir_pet(id_pet):
    """Remove o registro do pet."""
    with transacao() as cur:
        try:
            cur.execute("DELETE FROM dbo.pet WHERE id_pet = ?", (id_pet,))
            if cur.rowcount == 0:
                raise ErroNegocio("Pet não localizado.")
        except Exception as e:
            raise ErroNegocio(f"Erro ao excluir pet: {e}")

def listar_pets_do_tutor(id_tutor):
    """Navegação 1:N — Lista todos os pets vinculados ao ID de um tutor."""
    with transacao() as cur:
        cur.execute(
            "SELECT id_pet, nome, especie, raca, data_nascimento, peso_kg "
            "FROM dbo.pet WHERE id_tutor = ? ORDER BY nome", 
            (id_tutor,)
        )
        return cur.fetchall()

def buscar_pet_com_tutor(id_pet):
    """Navegação N:1 — Retorna dados do pet acompanhados dos dados do seu tutor via JOIN."""
    with transacao() as cur:
        cur.execute(
            "SELECT p.id_pet, p.nome AS pet, p.especie, p.raca, p.peso_kg, "
            "       t.id_tutor, t.nome AS tutor, t.telefone "
            "FROM dbo.pet p "
            "JOIN dbo.tutor t ON t.id_tutor = p.id_tutor "
            "WHERE p.id_pet = ?", 
            (id_pet,)
        )
        return cur.fetchone()

def agendar_consulta(id_pet, id_vet, data_hora, motivo, procedimentos):
    """Realiza o agendamento de uma consulta e vincula os procedimentos em bloco atômico."""
    with transacao() as cur:
        try:
            cur.execute(
                "INSERT INTO dbo.consulta (id_pet, id_veterinario, data_hora, motivo) "
                "OUTPUT INSERTED.id_consulta VALUES (?, ?, ?, ?)",
                (id_pet, id_vet, data_hora, motivo)
            )
            id_consulta = cur.fetchone()[0]

            for item in procedimentos:
                id_proc, qtd = (item if isinstance(item, tuple) else (item, 1))
                cur.execute(
                    "INSERT INTO dbo.consulta_procedimento (id_consulta, id_procedimento, quantidade, valor_cobrado) "
                    "SELECT ?, id_procedimento, ?, preco_base "
                    "FROM dbo.procedimento WHERE id_procedimento = ?",
                    (id_consulta, qtd, id_proc)
                )
            return id_consulta
        except Exception as e:
            raise ErroNegocio(f"Erro no agendamento da consulta: {e}")

def adicionar_procedimento(id_consulta, id_procedimento, quantidade=1):
    """Adiciona um procedimento extra a uma consulta agendada."""
    with transacao() as cur:
        try:
            cur.execute(
                "INSERT INTO dbo.consulta_procedimento (id_consulta, id_procedimento, quantidade, valor_cobrado) "
                "SELECT ?, id_procedimento, ?, preco_base "
                "FROM dbo.procedimento WHERE id_procedimento = ?",
                (id_consulta, quantidade, id_procedimento)
            )
        except Exception as e:
            raise ErroNegocio(f"Não foi possível incluir o procedimento: {e}")

def remover_procedimento(id_consulta, id_procedimento):
    """Desvincula um procedimento de uma consulta."""
    with transacao() as cur:
        cur.execute(
            "DELETE FROM dbo.consulta_procedimento WHERE id_consulta = ? AND id_procedimento = ?",
            (id_consulta, id_procedimento)
        )
        if cur.rowcount == 0:
            raise ErroNegocio("Procedimento não encontrado na consulta especificada.")

def listar_procedimentos_da_consulta(id_consulta):
    """Lista todos os procedimentos associados a uma determinada consulta."""
    with transacao() as cur:
        cur.execute(
            "SELECT pr.id_procedimento, pr.descricao, cp.quantidade, cp.valor_cobrado "
            "FROM dbo.consulta_procedimento cp "
            "JOIN dbo.procedimento pr ON pr.id_procedimento = cp.id_procedimento "
            "WHERE cp.id_consulta = ? ORDER BY pr.descricao", 
            (id_consulta,)
        )
        return cur.fetchall()

def listar_consultas_por_procedimento(id_procedimento):
    """Lista todas as consultas que utilizaram um determinado procedimento."""
    with transacao() as cur:
        cur.execute(
            "SELECT c.id_consulta, c.data_hora, c.status, p.nome AS pet, "
            "       cp.quantidade, cp.valor_cobrado "
            "FROM dbo.consulta_procedimento cp "
            "JOIN dbo.consulta c ON c.id_consulta = cp.id_consulta "
            "JOIN dbo.pet p ON p.id_pet = c.id_pet "
            "WHERE cp.id_procedimento = ? ORDER BY c.data_hora", 
            (id_procedimento,)
        )
        return cur.fetchall()

def total_da_consulta(id_consulta):
    """Calcula o somatório total cobrado nos procedimentos de uma consulta."""
    with transacao() as cur:
        cur.execute(
            "SELECT ISNULL(SUM(quantidade * valor_cobrado), 0) "
            "FROM dbo.consulta_procedimento WHERE id_consulta = ?", 
            (id_consulta,)
        )
        return cur.fetchone()[0]

def atualizar_status_consulta(id_consulta, status):
    """Altera o status operacional da consulta."""
    if status not in STATUS_CONSULTA_VALIDOS:
        raise ErroNegocio("Status inválido. Escolha entre: AGENDADA, REALIZADA ou CANCELADA.")
    
    with transacao() as cur:
        cur.execute("UPDATE dbo.consulta SET status = ? WHERE id_consulta = ?", (status, id_consulta))
        if cur.rowcount == 0:
            raise ErroNegocio("Consulta não encontrada.")

def excluir_consulta(id_consulta):
    """Exclui a consulta mantendo a consistência no banco."""
    with transacao() as cur:
        cur.execute("DELETE FROM dbo.consulta WHERE id_consulta = ?", (id_consulta,))
        if cur.rowcount == 0:
            raise ErroNegocio("Consulta não encontrada.")

def historico_do_pet(id_pet):
    """Consulta o histórico de atendimento acessando a view 'vw_resumo_consulta'."""
    with transacao() as cur:
        cur.execute(
            "SELECT id_consulta, data_hora, status, veterinario, qtd_itens, valor_total "
            "FROM dbo.vw_resumo_consulta "
            "WHERE id_consulta IN (SELECT id_consulta FROM dbo.consulta WHERE id_pet = ?) "
            "ORDER BY data_hora", 
            (id_pet,)
        )
        return cur.fetchall()