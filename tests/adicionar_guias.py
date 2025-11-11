#!/usr/bin/env python3
"""
Sistema simples para adicionar guias de teste
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import init_db, get_session
from app.models import Guia, Anexo, Procedimento, Diagnostico
from datetime import datetime, date
import random


def gerar_numero_guia():
    """Gera um número de guia aleatório."""
    return f"R{random.randint(600000, 999999)}"


def gerar_numero_operadora():
    """Gera um número de guia da operadora."""
    return f"UI{random.randint(800000, 999999)}"


def adicionar_guias_automaticas(quantidade=10):
    """Adiciona guias automaticamente com cenários variados."""
    try:
        print(f"📋 Adicionando {quantidade} guias automaticamente...")

        # Inicializar banco se necessário
        init_db()
        session = get_session()

        # Dados de exemplo expandidos
        hospitais = [
            "HOSPITAL SÃO PAULO",
            "CLÍNICA MEDICAL CENTER",
            "HOSPITAL UNIVERSAIS",
            "SANTA CASA DE MISERICÓRDIA",
            "HOSPITAL DAS CLÍNICAS",
            "CLÍNICA ESPECIALIZADA",
            "HOSPITAL REGIONAL",
            "CENTRO MÉDICO INTEGRADO",
            "HOSPITAL MUNICIPAL",
            "CLÍNICA CARDIOLÓGICA",
            "HOSPITAL ONCOLÓGICO",
            "CENTRO DE TRAUMATOLOGIA",
        ]

        prestadores = [
            "GABRIELA MARTINS",
            "MARIA SILVA",
            "CARLOS OLIVEIRA",
            "PATRICIA LIMA",
            "ROBERTO SOUZA",
            "ANA COSTA",
            "JOÃO SANTOS",
            "FERNANDA ALVES",
            "RICARDO PEREIRA",
            "JULIANA FERREIRA",
            "MARCOS RODRIGUES",
            "LUCIA CARDOSO",
        ]

        profissionais = [
            "ANGELICA MIRANDA",
            "DR. CARLOS MENDES",
            "DRA. PATRICIA SILVA",
            "DR. ROBERTO LIMA",
            "DRA. ANA SANTOS",
            "DR. JOÃO OLIVEIRA",
            "DRA. FERNANDA COSTA",
            "DR. RICARDO PEREIRA",
            "DRA. JULIANA FERREIRA",
            "DR. MARCOS RODRIGUES",
            "DRA. LUCIA CARDOSO",
            "DR. PEDRO ALMEIDA",
        ]

        # Cenários de teste variados
        cenarios_status = [
            {
                "status": "A",
                "probabilidade": 0.4,
                "descricao": "Aguardando processamento",
            },
            {
                "status": "T",
                "probabilidade": 0.3,
                "descricao": "Transmitida com sucesso",
            },
            {"status": "E", "probabilidade": 0.2, "descricao": "Erro no processamento"},
            {"status": "P", "probabilidade": 0.1, "descricao": "Em processamento"},
        ]

        # Tipos de erro variados
        tipos_erro = [
            "Erro na API DRG - Timeout",
            "Erro na validação dos dados",
            "Erro de autenticação JWT",
            "Dados incompletos na guia",
            "Erro de conexão com DRG",
            "Formato de dados inválido",
        ]

        profissionais = [
            "ANGELICA MIRANDA",
            "JOÃO SANTOS",
            "ANA COSTA",
            "ROBERTO SOUZA",
            "MARIA FERNANDA",
            "CARLOS EDUARDO",
            "PATRICIA SILVA",
            "FERNANDO OLIVEIRA",
        ]

        for i in range(quantidade):
            # Gerar dados aleatórios
            numero_guia = gerar_numero_guia()
            numero_operadora = gerar_numero_operadora()
            hospital = random.choice(hospitais)
            prestador = random.choice(prestadores)
            profissional = random.choice(profissionais)

            # Selecionar cenário baseado em probabilidade
            rand = random.random()
            acumulado = 0
            cenario = cenarios_status[0]  # Default para o primeiro cenário

            for c in cenarios_status:
                acumulado += c["probabilidade"]
                if rand <= acumulado:
                    cenario = c
                    break

            status = cenario["status"]

            # Definir tentativas e erro baseado no status
            if status == "E":
                tentativas = random.randint(1, 2)
                mensagem_erro = random.choice(tipos_erro)
                data_processamento = datetime.utcnow()
            elif status == "T":
                tentativas = random.randint(1, 2)
                mensagem_erro = None
                data_processamento = datetime.utcnow()
            elif status == "P":
                tentativas = 1
                mensagem_erro = None
                data_processamento = datetime.utcnow()
            else:  # A (Aguardando)
                tentativas = 0
                mensagem_erro = None
                data_processamento = None

            # Data aleatória
            data_autorizacao = date(2025, random.randint(1, 12), random.randint(1, 28))
            data_nascimento = datetime(
                random.randint(1950, 2000), random.randint(1, 12), random.randint(1, 28)
            )

            # Criar guia
            guia = Guia(
                numero_guia=numero_guia,
                codigo_operadora="4764",
                numero_guia_operadora=numero_operadora,
                numero_guia_internacao="",
                data_autorizacao=data_autorizacao,
                senha=str(random.randint(100000000, 999999999)),
                data_validade=date(2025, random.randint(1, 12), random.randint(1, 28)),
                numero_carteira=str(random.randint(700000, 999999)),
                data_validade_carteira=date(
                    2027, random.randint(1, 12), random.randint(1, 28)
                ),
                rn="N",
                data_nascimento=data_nascimento,
                sexo=random.choice(["M", "F"]),
                situacao_beneficiario="A",
                codigo_prestador=f"7050611659800{chr(65 + i)}",
                nome_prestador=prestador,
                nome_profissional=profissional,
                codigo_profissional=str(random.randint(50, 99)),
                numero_registro_profissional=f"G{random.randint(30000000, 99999999)}",
                uf_profissional="SP",
                codigo_cbo=f"C{random.randint(80000, 99999)}",
                codigo_contratado=str(random.randint(5300, 5399)),
                nome_hospital=hospital,
                data_sugerida_internacao=data_autorizacao,
                carater_atendimento="3",
                tipo_internacao="2",
                regime_internacao="1",
                diarias_solicitadas=str(random.randint(1, 10)),
                previsao_uso_opme="N",
                previsao_uso_quimioterapico="N",
                indicacao_clinica=f"Indicação clínica para internação - Guia {i+1}",
                indicacao_acidente="1",
                tipo_acomodacao_solicitada="1",
                data_admissao_estimada=date(
                    2025, random.randint(1, 12), random.randint(1, 28)
                ),
                qtde_diarias_autorizadas=str(random.randint(3, 15)),
                tipo_acomodacao_autorizada=str(random.randint(1, 4)),
                cnes_autorizado=str(random.randint(8000000, 9999999)),
                observacao_guia=f"OBSERVAÇÃO GUIA {i+1}",
                data_solicitacao=date(
                    2025, random.randint(1, 12), random.randint(1, 28)
                ),
                justificativa_operadora=f"Justificativa para internação - Guia {i+1}",
                natureza_guia="2",
                guia_complementar="N",
                situacao_guia="N",
                tipo_doenca="2",
                tempo_doenca=str(random.randint(1, 30)),
                longa_permanencia="1",
                motivo_encerramento="1",
                tipo_alta="7",
                data_alta=date(2025, random.randint(1, 12), random.randint(1, 28)),
                tp_status=status,
                tentativas=tentativas,
                mensagem_erro=mensagem_erro,
                data_processamento=data_processamento,
            )

            session.add(guia)
            session.commit()

            # Adicionar relacionamentos para algumas guias
            if i % 2 == 0:  # A cada 2 guias
                # Anexo
                anexo = Anexo(
                    guia_id=guia.id,
                    data_criacao=date(
                        2025, random.randint(1, 12), random.randint(1, 28)
                    ),
                    nome=f"DOC {i+1}",
                    numero_lote_documento=str(random.randint(10000000000, 99999999999)),
                    numero_protocolo_documento=str(
                        random.randint(10000000000, 99999999999)
                    ),
                    formato_documento="2",
                    sequencial_documento=str(random.randint(1000, 9999)),
                    caminho_documento="docs/hc1_balladinstinct_tab.pdf",
                    observacao_documento=f"OBSERVAÇÃO DO DOCUMENTO {i+1}",
                    tipo_documento="03",
                )
                session.add(anexo)

                # Procedimento
                procedimento = Procedimento(
                    guia_id=guia.id,
                    tabela="98",
                    codigo=str(random.randint(90000000, 99999999)),
                    descricao=f"PROCEDIMENTO {i+1}",
                    qtde_solicitada=str(random.randint(1, 5)),
                    valor_unitario=round(random.uniform(50.0, 500.0), 2),
                    qtde_autorizada=random.randint(0, 5),
                )
                session.add(procedimento)

                # Diagnóstico
                diagnostico = Diagnostico(
                    guia_id=guia.id,
                    codigo=f"A{random.randint(100, 999)}",
                    tipo=random.choice(["P", "S"]),
                )
                session.add(diagnostico)

                session.commit()

            print(f"   ✅ Guia {i+1}: {numero_guia} - {hospital} - Status: {status}")

        # Verificar total
        total_guias = session.query(Guia).count()
        total_anexos = session.query(Anexo).count()
        total_procedimentos = session.query(Procedimento).count()
        total_diagnosticos = session.query(Diagnostico).count()

        print(f"\n🎉 {quantidade} guias adicionadas com sucesso!")
        print(f"📊 Total no banco:")
        print(f"   • Guias: {total_guias}")
        print(f"   • Anexos: {total_anexos}")
        print(f"   • Procedimentos: {total_procedimentos}")
        print(f"   • Diagnósticos: {total_diagnosticos}")

        session.close()
        return True

    except Exception as e:
        print(f"❌ Erro ao adicionar guias: {e}")
        return False


def criar_cenarios_especificos():
    """Cria cenários específicos de teste para diferentes situações."""
    try:
        print("🎭 Criando cenários específicos de teste...")

        # Inicializar banco se necessário
        init_db()
        session = get_session()

        # Cenário 1: Guia com erro crítico (máximo de tentativas)
        guia_erro_critico = Guia(
            numero_guia="R999001",
            codigo_operadora="4764",
            numero_guia_operadora="UI999001",
            numero_guia_internacao="",
            data_autorizacao=date(2025, 9, 1),
            senha="999999999",
            data_validade=date(2025, 10, 1),
            numero_carteira="999999",
            data_validade_carteira=date(2027, 12, 31),
            rn="N",
            data_nascimento=datetime(1980, 5, 15),
            sexo="F",
            situacao_beneficiario="A",
            codigo_prestador="7050611659800Z",
            nome_prestador="HOSPITAL TESTE ERRO",
            nome_profissional="DR. ERRO TESTE",
            codigo_profissional="99",
            numero_registro_profissional="G99999999",
            uf_profissional="SP",
            codigo_cbo="C99999",
            codigo_contratado="5399",
            nome_hospital="HOSPITAL TESTE ERRO CRÍTICO",
            data_sugerida_internacao=date(2025, 9, 1),
            carater_atendimento="3",
            tipo_internacao="2",
            regime_internacao="1",
            diarias_solicitadas="5",
            previsao_uso_opme="N",
            previsao_uso_quimioterapico="N",
            indicacao_clinica="CENÁRIO DE TESTE: Erro crítico com máximo de tentativas",
            indicacao_acidente="1",
            tipo_acomodacao_solicitada="1",
            data_admissao_estimada=date(2025, 9, 5),
            qtde_diarias_autorizadas="5",
            tipo_acomodacao_autorizada="2",
            cnes_autorizado="9999999",
            observacao_guia="TESTE: Guia com erro crítico",
            data_solicitacao=date(2025, 8, 30),
            justificativa_operadora="Cenário de teste para erro crítico",
            natureza_guia="2",
            guia_complementar="N",
            situacao_guia="N",
            tipo_doenca="2",
            tempo_doenca="10",
            longa_permanencia="1",
            motivo_encerramento="1",
            tipo_alta="7",
            data_alta=date(2025, 9, 10),
            tp_status="E",
            tentativas=2,  # Máximo de tentativas
            mensagem_erro="ERRO CRÍTICO: Falha na validação de dados obrigatórios",
            data_processamento=datetime.utcnow(),
        )

        # Cenário 2: Guia transmitida com sucesso
        guia_sucesso = Guia(
            numero_guia="R999002",
            codigo_operadora="4764",
            numero_guia_operadora="UI999002",
            numero_guia_internacao="",
            data_autorizacao=date(2025, 9, 1),
            senha="888888888",
            data_validade=date(2025, 10, 1),
            numero_carteira="888888",
            data_validade_carteira=date(2027, 12, 31),
            rn="N",
            data_nascimento=datetime(1975, 3, 20),
            sexo="M",
            situacao_beneficiario="A",
            codigo_prestador="7050611659800Y",
            nome_prestador="HOSPITAL TESTE SUCESSO",
            nome_profissional="DR. SUCESSO TESTE",
            codigo_profissional="88",
            numero_registro_profissional="G88888888",
            uf_profissional="SP",
            codigo_cbo="C88888",
            codigo_contratado="5388",
            nome_hospital="HOSPITAL TESTE SUCESSO",
            data_sugerida_internacao=date(2025, 9, 1),
            carater_atendimento="3",
            tipo_internacao="2",
            regime_internacao="1",
            diarias_solicitadas="3",
            previsao_uso_opme="N",
            previsao_uso_quimioterapico="N",
            indicacao_clinica="CENÁRIO DE TESTE: Transmitida com sucesso",
            indicacao_acidente="1",
            tipo_acomodacao_solicitada="1",
            data_admissao_estimada=date(2025, 9, 3),
            qtde_diarias_autorizadas="3",
            tipo_acomodacao_autorizada="1",
            cnes_autorizado="8888888",
            observacao_guia="TESTE: Guia transmitida com sucesso",
            data_solicitacao=date(2025, 8, 30),
            justificativa_operadora="Cenário de teste para sucesso",
            natureza_guia="2",
            guia_complementar="N",
            situacao_guia="N",
            tipo_doenca="2",
            tempo_doenca="5",
            longa_permanencia="1",
            motivo_encerramento="1",
            tipo_alta="7",
            data_alta=date(2025, 9, 6),
            tp_status="T",
            tentativas=1,
            mensagem_erro=None,
            data_processamento=datetime.utcnow(),
        )

        # Cenário 3: Guia em processamento
        guia_processando = Guia(
            numero_guia="R999003",
            codigo_operadora="4764",
            numero_guia_operadora="UI999003",
            numero_guia_internacao="",
            data_autorizacao=date(2025, 9, 2),
            senha="777777777",
            data_validade=date(2025, 10, 2),
            numero_carteira="777777",
            data_validade_carteira=date(2027, 12, 31),
            rn="N",
            data_nascimento=datetime(1990, 8, 10),
            sexo="F",
            situacao_beneficiario="A",
            codigo_prestador="7050611659800X",
            nome_prestador="HOSPITAL TESTE PROCESSANDO",
            nome_profissional="DR. PROCESSANDO TESTE",
            codigo_profissional="77",
            numero_registro_profissional="G77777777",
            uf_profissional="SP",
            codigo_cbo="C77777",
            codigo_contratado="5377",
            nome_hospital="HOSPITAL TESTE PROCESSANDO",
            data_sugerida_internacao=date(2025, 9, 2),
            carater_atendimento="3",
            tipo_internacao="2",
            regime_internacao="1",
            diarias_solicitadas="7",
            previsao_uso_opme="N",
            previsao_uso_quimioterapico="N",
            indicacao_clinica="CENÁRIO DE TESTE: Em processamento",
            indicacao_acidente="1",
            tipo_acomodacao_solicitada="1",
            data_admissao_estimada=date(2025, 9, 4),
            qtde_diarias_autorizadas="7",
            tipo_acomodacao_autorizada="3",
            cnes_autorizado="7777777",
            observacao_guia="TESTE: Guia em processamento",
            data_solicitacao=date(2025, 9, 1),
            justificativa_operadora="Cenário de teste para processamento",
            natureza_guia="2",
            guia_complementar="N",
            situacao_guia="N",
            tipo_doenca="2",
            tempo_doenca="15",
            longa_permanencia="1",
            motivo_encerramento="1",
            tipo_alta="7",
            data_alta=date(2025, 9, 11),
            tp_status="P",
            tentativas=1,
            mensagem_erro=None,
            data_processamento=datetime.utcnow(),
        )

        # Adicionar guias ao banco
        session.add(guia_erro_critico)
        session.add(guia_sucesso)
        session.add(guia_processando)
        session.commit()

        print("✅ Cenários específicos criados:")
        print(
            f"   • Guia Erro Crítico: {guia_erro_critico.numero_guia} (Status: E, Tentativas: 2)"
        )
        print(
            f"   • Guia Sucesso: {guia_sucesso.numero_guia} (Status: T, Tentativas: 1)"
        )
        print(
            f"   • Guia Processando: {guia_processando.numero_guia} (Status: P, Tentativas: 1)"
        )

        session.close()
        return True

    except Exception as e:
        print(f"❌ Erro ao criar cenários específicos: {e}")
        return False


def adicionar_guia_manual():
    """Adiciona uma guia manualmente."""
    try:
        print("📋 Adicionando guia manualmente...")

        # Inicializar banco se necessário
        init_db()
        session = get_session()

        # Dados básicos (você pode modificar)
        guia = Guia(
            numero_guia=gerar_numero_guia(),
            codigo_operadora="4764",
            numero_guia_operadora=gerar_numero_operadora(),
            data_autorizacao=date(2025, 8, 15),
            senha=str(random.randint(100000000, 999999999)),
            data_validade=date(2025, 9, 15),
            numero_carteira=str(random.randint(700000, 999999)),
            data_validade_carteira=date(2027, 12, 31),
            rn="N",
            data_nascimento=datetime(1980, 5, 15),
            sexo="M",
            situacao_beneficiario="A",
            codigo_prestador="7050611659800Z",
            nome_prestador="HOSPITAL EXEMPLO",
            nome_profissional="DR. EXEMPLO",
            codigo_profissional="99",
            numero_registro_profissional="G99999999999999",
            uf_profissional="SP",
            codigo_cbo="C99999",
            codigo_contratado="5399",
            nome_hospital="HOSPITAL EXEMPLO",
            data_sugerida_internacao=date(2025, 8, 16),
            carater_atendimento="3",
            tipo_internacao="2",
            regime_internacao="1",
            diarias_solicitadas="5",
            previsao_uso_opme="N",
            previsao_uso_quimioterapico="N",
            indicacao_clinica="Indicação clínica para internação",
            indicacao_acidente="1",
            tipo_acomodacao_solicitada="1",
            data_admissao_estimada=date(2025, 8, 17),
            qtde_diarias_autorizadas="7",
            tipo_acomodacao_autorizada="2",
            cnes_autorizado="9999999",
            observacao_guia="OBSERVAÇÃO GUIA MANUAL",
            data_solicitacao=date(2025, 8, 14),
            justificativa_operadora="Justificativa para internação manual",
            natureza_guia="2",
            guia_complementar="N",
            situacao_guia="N",
            tipo_doenca="2",
            tempo_doenca="10",
            longa_permanencia="1",
            motivo_encerramento="1",
            tipo_alta="7",
            data_alta=date(2025, 8, 25),
            tp_status="A",
        )

        session.add(guia)
        session.commit()

        print(f"✅ Guia adicionada: {guia.numero_guia} - {guia.nome_hospital}")

        session.close()
        return True

    except Exception as e:
        print(f"❌ Erro ao adicionar guia manual: {e}")
        return False


def main():
    """Menu principal."""
    print("🏥 SISTEMA DE ADIÇÃO DE GUIAS")
    print("=" * 40)
    print("1. Adicionar 5 guias automaticamente")
    print("2. Adicionar 10 guias automaticamente")
    print("3. Adicionar 1 guia manual")
    print("4. Criar cenários específicos de teste")
    print("5. Sair")

    try:
        opcao = input("\nEscolha uma opção (1-5): ").strip()

        if opcao == "1":
            adicionar_guias_automaticas(5)
        elif opcao == "2":
            adicionar_guias_automaticas(10)
        elif opcao == "3":
            adicionar_guia_manual()
        elif opcao == "4":
            criar_cenarios_especificos()
        elif opcao == "5":
            print("👋 Até logo!")
        else:
            print("❌ Opção inválida!")

    except KeyboardInterrupt:
        print("\n👋 Operação cancelada!")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()
