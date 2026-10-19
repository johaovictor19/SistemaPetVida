import sys
from datetime import datetime

import db
import repositorio as repo
from repositorio import ErroNegocio

def exibir_resultados(registros):
    if not registros:
        print("Nenhum registro encontrado.")
    else:
        for reg in registros:
            print(tuple(reg))

def menu_principal():
    print("\n=== Sistema PetVida ===")
    print("1 - Testar conexão com o banco")
    print("2 - Listar tutores (com filtro por nome)")
    print("3 - Cadastrar novo tutor")
    print("4 - Listar pets de um tutor")
    print("5 - Agendar consulta")
    print("6 - Ver procedimentos e total de uma consulta")
    print("7 - Consultar histórico do pet")
    print("0 - Sair")
    return input("Selecione uma opção: ")

def processar_opcao(opcao):
    if opcao == "1":
        info = db.testar_conexao()
        print("\n[Conexão Estabelecida]")
        print("Servidor:", info["servidor"])
        print("Banco de Dados:", info["banco"])
        print("Versão SQL Server:", info["versao"])

    elif opcao == "2":
        filtro = input("Filtro de nome (pressione Enter para listar todos): ")
        exibir_resultados(repo.listar_tutores(filtro))

    elif opcao == "3":
        nome = input("Nome do tutor: ")
        cpf = input("CPF (apenas 11 números): ")
        email = input("E-mail (opcional): ") or None
        telefone = input("Telefone (opcional): ") or None
        id_tutor = repo.criar_tutor(nome, cpf, email, telefone)
        print(f"-> Tutor cadastrado com sucesso! ID: {id_tutor}")

    elif opcao == "4":
        id_tutor = int(input("Informe o ID do tutor: "))
        exibir_resultados(repo.listar_pets_do_tutor(id_tutor))

    elif opcao == "5":
        id_pet = int(input("ID do pet: "))
        id_vet = int(input("ID do veterinário: "))
        data_str = input("Data e hora (Formato AAAA-MM-DD HH:MM): ")
        data_hora = datetime.strptime(data_str, "%Y-%m-%d %H:%M")
        motivo = input("Motivo da consulta: ")
        
        procs_input = input("IDs dos procedimentos (separados por vírgula): ")
        ids_procedimentos = [int(p.strip()) for p in procs_input.split(",") if p.strip()]
        
        id_consulta = repo.agendar_consulta(id_pet, id_vet, data_hora, motivo, ids_procedimentos)
        print(f"-> Consulta agendada com sucesso! ID: {id_consulta}")

    elif opcao == "6":
        id_consulta = int(input("Informe o ID da consulta: "))
        print("\n--- Procedimentos Realizados ---")
        exibir_resultados(repo.listar_procedimentos_da_consulta(id_consulta))
        total = repo.total_da_consulta(id_consulta)
        print(f"Valor Total da Consulta: R$ {total:.2f}")

    elif opcao == "7":
        id_pet = int(input("Informe o ID do pet: "))
        print("\n--- Histórico de Consultas ---")
        exibir_resultados(repo.historico_do_pet(id_pet))

    else:
        print("Opção inválida. Escolha um número do menu.")

def main():
    while True:
        opcao = menu_principal()
        if opcao == "0":
            print("\nEncerrando a aplicação...")
            break
        try:
            processar_opcao(opcao)
        except ErroNegocio as e:
            print(f"\n[Aviso de Regra de Negócio]: {e}")
        except ValueError:
            print("\n[Erro de Digitação]: Por favor, informe dados numéricos ou formatos de data válidos.")

if __name__ == "__main__":
    main()