#!/usr/bin/env python3
"""
Script para criar banco SQLite de teste com dados fictícios
"""

import sys
import os
from datetime import datetime, date
import sqlite3

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import Base, engine
from app.models import Guia, Anexo, Procedimento, Diagnostico


def criar_banco_sqlite():
    """Cria o banco SQLite e as tabelas."""
    print("=== Criando banco SQLite de teste ===\n")

    # Configurar SQLite
    db_path = "teste_drg.db"
    sqlite_url = f"sqlite:///{db_path}"

    # Atualizar engine para SQLite
    from sqlalchemy import create_engine

    engine = create_engine(sqlite_url, echo=True)

    print(f"📁 Banco criado em: {os.path.abspath(db_path)}")

    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

    return engine, db_path


def criar_dados_ficticios(engine):
    """Cria dados fictícios no banco."""
    print("\n=== Criando dados fictícios ===\n")

    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Criar guia fictícia
        guia = Guia(
            codigo_operadora="4764",
            numero_guia="R679541",
            numero_guia_operadora="UI856321",
            numero_guia_internacao="",
            data_autorizacao=date(2025, 8, 2),
            senha="896532177",
            data_validade=date(2025, 7, 4),
            # Dados do beneficiário
            numero_carteira="797615",
            data_validade_carteira=date(2027, 9, 4),
            rn="N",
            data_nascimento=datetime(1955, 5, 4),
            sexo="M",
            situacao_beneficiario="A",
            # Dados do prestador
            codigo_prestador="7050611659800A",
            nome_prestador="GABRIELA MARTINS",
            nome_profissional="ANGELICA MIRANDA",
            codigo_profissional="56",
            numero_registro_profissional="G37050306980008",
            uf_profissional="SP",
            codigo_cbo="C87456",
            # Dados do hospital
            codigo_contratado="5306",
            nome_hospital="HOSPITAL CINCO",
            data_sugerida_internacao=date(2025, 8, 2),
            carater_atendimento="3",
            tipo_internacao="2",
            regime_internacao="1",
            diarias_solicitadas=1,
            previsao_uso_opme="N",
            previsao_uso_quimioterapico="N",
            indicacao_clinica="Obtido a partir de um serviço externo de consulta, fornecido por um sistema integrador, a consulta do nome do beneficiário será realizada em tempo real, sempre que necessário para exibição na interface do Painel de Guias.",
            indicacao_acidente="1",
            tipo_acomodacao_solicitada="1",
            # Dados da autorização
            data_admissao_estimada=date(2025, 8, 5),
            qtde_diarias_autorizadas=7,
            tipo_acomodacao_autorizada="4",
            cnes_autorizado="8774563",
            observacao_guia="OBSERVAÇÃO GUIA DE TESTE 02",
            data_solicitacao=date(2025, 7, 30),
            justificativa_operadora="Uma guia de internação é um documento essencial no sistema de saúde, utilizado para solicitar, autorizar ou negar a internação de um paciente em um hospital ou clínica.",
            # Dados complementares
            natureza_guia="2",
            guia_complementar="N",
            situacao_guia="N",
            tipo_doenca="2",
            tempo_doenca=8,
            longa_permanencia="1",
            motivo_encerramento="1",
            tipo_alta="7",
            data_alta=date(2025, 8, 16),
            # Status de processamento
            tp_status="A",  # Aguardando processamento
            tentativas=0,
        )

        session.add(guia)
        session.flush()  # Para obter o ID

        print(f"✅ Guia criada: {guia.numero_guia} (ID: {guia.id})")

        # Criar anexo
        anexo = Anexo(
            guia_id=guia.id,
            data_criacao=datetime(2025, 8, 5),
            nome="DOC TESTE 02",
            numero_lote_documento="78544125445",
            numero_protocolo_documento="44125745841",
            formato_documento="2",
            sequencial_documento="7854",
            url_documento="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/800px-Google_2015_logo.svg.png",
            observacao_documento="OBSERVAÇÃO DO DOCUMENTO TESTE 02",
            tipo_documento="03",
        )

        session.add(anexo)
        print(f"✅ Anexo criado: {anexo.nome}")

        # Criar procedimento
        procedimento = Procedimento(
            guia_id=guia.id,
            tabela="98",
            codigo="96547854",
            descricao="TESTE DAY",
            qtde_solicitada=1,
            valor_unitario=119.25,
            qtde_autorizada=0,  # Corrigido: campo obrigatório
        )

        session.add(procedimento)
        print(f"✅ Procedimento criado: {procedimento.descricao}")

        # Criar diagnósticos
        diagnosticos = [
            Diagnostico(guia_id=guia.id, codigo="A021", tipo="P"),
            Diagnostico(guia_id=guia.id, codigo="A009", tipo="S"),
            Diagnostico(guia_id=guia.id, codigo="A010", tipo="S"),
        ]

        for diagnostico in diagnosticos:
            session.add(diagnostico)
            print(f"✅ Diagnóstico criado: {diagnostico.codigo} ({diagnostico.tipo})")

        # Criar mais algumas guias para teste
        guias_adicionais = [
            {
                "numero_guia": "R679542",
                "nome_prestador": "DR. JOÃO SILVA",
                "nome_hospital": "HOSPITAL SÃO PAULO",
                "tp_status": "T",  # Transmitida
            },
            {
                "numero_guia": "R679543",
                "nome_prestador": "DRA. MARIA SANTOS",
                "nome_hospital": "CLÍNICA MEDICAL",
                "tp_status": "E",  # Erro
            },
            {
                "numero_guia": "R679544",
                "nome_prestador": "DR. CARLOS OLIVEIRA",
                "nome_hospital": "HOSPITAL UNIVERSAIS",
                "tp_status": "A",  # Aguardando
            },
        ]

        for dados_guia in guias_adicionais:
            nova_guia = Guia(
                codigo_operadora="4764",
                numero_guia=dados_guia["numero_guia"],
                numero_guia_operadora=f"UI{dados_guia['numero_guia'][-6:]}",
                data_autorizacao=date(2025, 8, 2),
                numero_carteira="797615",
                data_nascimento=datetime(1955, 5, 4),
                sexo="M",
                situacao_beneficiario="A",
                codigo_prestador="7050611659800A",
                nome_prestador=dados_guia["nome_prestador"],
                nome_profissional="PROFISSIONAL TESTE",
                codigo_profissional="56",
                numero_registro_profissional="G37050306980008",
                uf_profissional="SP",
                codigo_cbo="C87456",
                codigo_contratado="5306",
                nome_hospital=dados_guia["nome_hospital"],
                data_sugerida_internacao=date(2025, 8, 2),
                carater_atendimento="3",
                tipo_internacao="2",
                regime_internacao="1",
                diarias_solicitadas=1,
                previsao_uso_opme="N",
                previsao_uso_quimioterapico="N",
                indicacao_clinica="Indicação clínica para teste",
                indicacao_acidente="1",
                tipo_acomodacao_solicitada="1",
                data_solicitacao=date(2025, 7, 30),
                natureza_guia="2",
                guia_complementar="N",
                situacao_guia="N",
                tp_status=dados_guia["tp_status"],
                tentativas=0,
            )

            session.add(nova_guia)
            print(
                f"✅ Guia adicional criada: {nova_guia.numero_guia} (Status: {nova_guia.tp_status})"
            )

        # Commit das alterações
        session.commit()
        print(f"\n✅ {len(guias_adicionais) + 1} guias criadas com sucesso!")
        print(f"✅ {len(diagnosticos)} diagnósticos criados!")
        print(f"✅ {1} anexo criado!")
        print(f"✅ {1} procedimento criado!")

        return True

    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao criar dados: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        session.close()


def verificar_dados(engine):
    """Verifica os dados criados."""
    print("\n=== Verificando dados criados ===\n")

    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Contar registros
        total_guias = session.query(Guia).count()
        total_anexos = session.query(Anexo).count()
        total_procedimentos = session.query(Procedimento).count()
        total_diagnosticos = session.query(Diagnostico).count()

        print(f"📊 Total de registros:")
        print(f"   🏥 Guias: {total_guias}")
        print(f"   📎 Anexos: {total_anexos}")
        print(f"   🔧 Procedimentos: {total_procedimentos}")
        print(f"   🏥 Diagnósticos: {total_diagnosticos}")

        # Listar guias por status
        print(f"\n📊 Guias por status:")
        for status in ["A", "T", "E"]:
            count = session.query(Guia).filter(Guia.tp_status == status).count()
            status_name = {"A": "Aguardando", "T": "Transmitida", "E": "Erro"}[status]
            print(f"   {status_name}: {count}")

        # Listar algumas guias
        print(f"\n📋 Primeiras 3 guias:")
        guias = session.query(Guia).limit(3).all()
        for guia in guias:
            print(
                f"   📋 {guia.numero_guia} - {guia.nome_hospital} - Status: {guia.tp_status}"
            )

        return True

    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        return False
    finally:
        session.close()


def main():
    """Executa a criação do banco de teste."""
    print("🗄️  Criando banco SQLite de teste com dados fictícios...\n")

    try:
        # 1. Criar banco e tabelas
        engine, db_path = criar_banco_sqlite()

        # 2. Popular com dados fictícios
        dados_ok = criar_dados_ficticios(engine)

        if dados_ok:
            # 3. Verificar dados
            verificar_dados(engine)

            print(f"\n🎉 Banco de teste criado com sucesso!")
            print(f"📁 Localização: {os.path.abspath(db_path)}")
            print(f"\n💡 Para visualizar no Cursor:")
            print(f"   1. Abra o arquivo: {db_path}")
            print(f"   2. Ou use a extensão SQLite no Cursor")
            print(f"   3. Ou execute queries SQL diretamente")

            print(f"\n🚀 Próximo passo: Criar rotas da API para acessar os dados")

        else:
            print("❌ Falha ao criar dados fictícios")

    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
