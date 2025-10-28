#!/usr/bin/env python3
"""
Script simples para enviar JSON para a API DRG
"""

import json
from app.services.drg_service import DRGService


def enviar_json():
    """Envia JSON para a API DRG"""

    # JSON de exemplo - você pode modificar conforme necessário
    json_drg = {
        "loteGuias": {
            "guia": [
                {
                    "codigoOperadora": "3945",
                    "numeroGuia": "R679500",
                    "numeroGuiaOperadora": "UI856321",
                    "numeroGuiaInternacao": "G001-COMP",
                    "dataAutorizacao": "2025-08-02",
                    "senha": "896532177",
                    "dataValidade": "2025-07-04",
                    "numeroCarteira": "797615",
                    "dataValidadeCarteira": "2027-09-04",
                    "rn": "N",
                    "dataNascimento": "1955-05-04 00:00",
                    "sexo": "M",
                    "situacaoBeneficiario": "A",
                    "nomeBeneficiario": "JOÃO DA SILVA SANTOS",
                    "codigoPrestador": "7050611659800A",
                    "nomePrestador": "GABRIELA MARTINS",
                    "nomeProfissional": "ANGELICA MIRANDA",
                    "codigoProfissional": "56",
                    "numeroRegistroProfissional": "G37050306980008",
                    "ufProfissional": "SP",
                    "codigoCbo": "C87456",
                    "codigoContratado": "5499",
                    "nomeHospital": "HOSPITAL I9MED",
                    "dataSugeridaInternacao": "2025-08-02",
                    "caraterAtendimento": "3",
                    "tipoInternacao": "2",
                    "regimeInternacao": "1",
                    "diariasSolicitadas": "1",
                    "previsaoUsoOpme": "N",
                    "previsaoUsoQuimioterapico": "N",
                    "indicacaoClinica": "Obtido a partir de um serviço externo de consulta, fornecido por um sistema integrador, a consulta do nome do beneficiário será realizada em tempo real, sempre que necessário para exibição na interface do Painel de Guias. O nome do beneficiário não é persistido em nenhuma tabela da plataforma, incluindo a tb_drg_registro_paciente_guia_internacao, em observância às boas práticas de segurança da informação e às normas da LGPD.",
                    "indicacaoAcidente": "1",
                    "tipoAcomodacaoSolicitada": "1",
                    "dataAdmissaoEstimada": "2025-08-05",
                    "qtdeDiariasAutorizadas": "7",
                    "tipoAcomodacaoAutorizada": "4",
                    "cnesAutorizado": "9632587",
                    "porteHospital": "2",
                    "complexidadeHospital": "1",
                    "esferaAdministrativa": "2",
                    "enderecoHospital": "Rua Dias Adorno, 152 - Santo Agostinho - Belo Horizonte/MG - CEP: 30190100",
                    "observacaoGuia": "OBSERVAÇÃO GUIA DE TESTE",
                    "dataSolicitacao": "2025-07-30",
                    "justificativaOperadora": "Uma guia de internação é um documento essencial no sistema de saúde, utilizado para solicitar, autorizar ou negar a internação de um paciente em um hospital ou clínica. É um formulário padrão, muitas vezes parte do processo de autorização de procedimentos médicos, que contém informações sobre o paciente e o motivo da internação222.",
                    "naturezaGuia": "2",
                    "guiaComplementar": "N",
                    "situacaoGuia": "P",
                    "tipoDoenca": "2",
                    "tempoDoenca": "8",
                    "longaPermanencia": "1",
                    "motivoEncerramento": "1",
                    "tipoAlta": "7",
                    "dataAlta": "2025-08-16",
                    "anexo": [
                        {
                            "dataCriacao": "2025-08-05",
                            "nome": "DOC TESTE 02",
                            "numeroLoteDocumento": "78544125445",
                            "numeroProtocoloDocumento": "44125745841",
                            "formatoDocumento": "2",
                            "sequencialDocumento": "7854",
                            "urlDocumento": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/800px-Google_2015_logo.svg.png",
                            "observacaoDocumento": "OBSERVAÇÃO DO DOCUMENTO TESTE 02",
                            "tipoDocumento": "03",
                        }
                    ],
                    "procedimento": [
                        {
                            "tabela": "98",
                            "codigo": "96547854",
                            "descricao": "TESTE DAY",
                            "qtdeSolicitada": "1",
                            "valorUnitario": "119.25",
                            "qtdeAutorizada": "",
                            "nome": "nome teste 05",
                        }
                    ],
                    "diagnostico": [
                        {"codigo": "A021", "tipo": "P"},
                        {"codigo": "A009", "tipo": "S"},
                        {"codigo": "A010", "tipo": "S"},
                    ],
                }
            ]
        }
    }

    print("🚀 Enviando JSON para API DRG...")
    print(f"📋 Operadora: {json_drg['loteGuias']['guia'][0]['codigoOperadora']}")
    print(f"📋 Hospital: {json_drg['loteGuias']['guia'][0]['nomeHospital']}")

    try:
        drg_service = DRGService()
        resultado = drg_service.enviar_guia(json_drg)

        if resultado["sucesso"]:
            print("✅ JSON enviado com sucesso!")
            resposta = resultado.get("resposta", {})
            guias_resposta = resposta.get("guias", [])

            if guias_resposta:
                guia_resposta = guias_resposta[0]
                print(f"📋 Resposta:")
                print(f"   • Número: {guia_resposta.get('numeroGuia', 'N/A')}")
                print(f"   • Situação: {guia_resposta.get('situacao', 'N/A')}")

                if guia_resposta.get("erro"):
                    print(f"   • Erro: {guia_resposta['erro']}")
                else:
                    print(f"   • ✅ Sucesso!")
        else:
            print(f"❌ Erro: {resultado['erro']}")

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    enviar_json()
