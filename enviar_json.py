"""
Script simples para enviar JSON para a API DRG
"""

import base64
import requests
from pathlib import Path
from datetime import datetime
from app.services.drg_service import DRGService
from app.config.config import get_settings


def gerar_conteudo_base64_arquivo(caminho_arquivo: str, max_size_mb: int = 20) -> str:
    """Lê arquivo local e converte para Base64."""
    try:
        arquivo_path = Path(caminho_arquivo)

        if not arquivo_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")

        if not arquivo_path.is_file():
            raise ValueError(f"Caminho não é um arquivo: {caminho_arquivo}")

        print(f"📥 Lendo arquivo: {caminho_arquivo}")

        tamanho_bytes = arquivo_path.stat().st_size
        tamanho_mb = tamanho_bytes / (1024 * 1024)

        if tamanho_mb > max_size_mb:
            raise ValueError(
                f"Arquivo excede o limite de {max_size_mb}MB (tamanho: {tamanho_mb:.2f}MB)"
            )

        with arquivo_path.open("rb") as arquivo:
            conteudo = arquivo.read()

        if not conteudo:
            raise ValueError("Arquivo vazio")

        conteudo_base64 = base64.b64encode(conteudo).decode("utf-8")
        print(f"✅ Arquivo convertido para Base64 ({tamanho_mb:.2f}MB)")
        return conteudo_base64

    except FileNotFoundError as e:
        raise Exception(f"Arquivo não encontrado: {e}") from e
    except Exception as e:
        raise Exception(f"Erro ao processar arquivo: {e}") from e


def gerar_conteudo_base64_url(url: str, max_size_mb: int = 20) -> str:
    """Baixa arquivo da URL e converte para Base64."""
    try:
        print(f"📥 Baixando arquivo de: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        conteudo = response.content
        tamanho_mb = len(conteudo) / (1024 * 1024)

        if tamanho_mb > max_size_mb:
            raise ValueError(
                f"Arquivo excede o limite de {max_size_mb}MB (tamanho: {tamanho_mb:.2f}MB)"
            )

        if not conteudo:
            raise ValueError("Arquivo vazio")

        conteudo_base64 = base64.b64encode(conteudo).decode("utf-8")
        print(f"✅ Arquivo convertido para Base64 ({tamanho_mb:.2f}MB)")
        return conteudo_base64

    except requests.RequestException as e:
        raise Exception(f"Erro ao baixar arquivo: {e}") from e
    except Exception as e:
        raise Exception(f"Erro ao processar arquivo: {e}") from e


def enviar_json():
    """Envia JSON para a API DRG usando as credenciais configuradas."""

    # Verificar credenciais configuradas
    settings = get_settings()
    print("🔐 Usando credenciais:")
    print(f"   • Usuário: {settings.DRG_USERNAME}")
    print(f"   • API Key: {settings.DRG_API_KEY[:20]}...")
    print(f"   • Auth URL: {settings.AUTH_API_URL}")
    print(f"   • DRG URL: {settings.DRG_API_URL}")
    print()
    print("🏥 Dados do hospital (do .env):")
    print(
        f"   • Código Contratado: {getattr(settings, 'HOSPITAL_CODIGO_CONTRATADO', 'N/A')}"
    )
    print(f"   • Nome: {getattr(settings, 'HOSPITAL_NOME', 'N/A')}")
    print(f"   • CNES: {getattr(settings, 'HOSPITAL_CNES', 'N/A')}")
    print(f"   • Porte: {getattr(settings, 'HOSPITAL_PORTE', 'N/A')}")
    print(f"   • Complexidade: {getattr(settings, 'HOSPITAL_COMPLEXIDADE', 'N/A')}")
    print(
        f"   • Esfera Administrativa: {getattr(settings, 'HOSPITAL_ESFERA_ADMINISTRATIVA', 'N/A')}"
    )
    print(f"   • Endereço: {getattr(settings, 'HOSPITAL_ENDERECO', 'N/A')}")
    print()

    # Anexo vazio conforme solicitado
    anexo = []
    print("ℹ️  Anexo: [] (array vazio)")
    print()

    # JSON atualizado com dados do log (guia R094342)
    json_drg = {
        "loteGuias": {
            "guia": [
                {
                    "codigoOperadora": "3945",
                    "numeroGuia": "R094342",
                    "numeroGuiaOperadora": "UI856321",
                    "numeroGuiaInternacao": "",
                    "dataAutorizacao": "2025-08-02",
                    "senha": "***2177",
                    "dataValidade": "2025-07-04",
                    "numeroCarteira": "797615",
                    "dataValidadeCarteira": "2027-09-04",
                    "rn": "N",
                    "dataNascimento": "1955-05-04 00:00",
                    "sexo": "M",
                    "situacaoBeneficiario": "A",
                    "nomeBeneficiario": "João Silva Santos",
                    "codigoPrestador": "7050611659800A",
                    "nomePrestador": "GABRIELA MARTINS",
                    "nomeProfissional": "ANGELICA MIRANDA",
                    "codigoProfissional": "56",
                    "numeroRegistroProfissional": "G37050306980008",
                    "ufProfissional": "SP",
                    "codigoCbo": "C87456",
                    "codigoContratado": getattr(
                        settings, "HOSPITAL_CODIGO_CONTRATADO", None
                    ),
                    "nomeHospital": getattr(settings, "HOSPITAL_NOME", None),
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
                    "cnesAutorizado": getattr(settings, "HOSPITAL_CNES", None),
                    "porteHospital": getattr(settings, "HOSPITAL_PORTE", None),
                    "complexidadeHospital": getattr(
                        settings, "HOSPITAL_COMPLEXIDADE", None
                    ),
                    "esferaAdministrativa": getattr(
                        settings, "HOSPITAL_ESFERA_ADMINISTRATIVA", None
                    ),
                    "enderecoHospital": getattr(settings, "HOSPITAL_ENDERECO", None),
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
                    "anexo": anexo,
                    "procedimento": [
                        {
                            "tabela": "98",
                            "codigo": "96547854",
                            "descricao": "TESTE DAY",
                            "qtdeSolicitada": "1",
                            "valorUnitario": "119.25",
                            "qtdeAutorizada": "1",
                            "nome": "",
                        }
                    ],
                    "diagnostico": [{"codigo": "A021", "tipo": "P"}],
                }
            ]
        }
    }

    print("🚀 Enviando JSON para API DRG...")
    print(f"📋 Operadora: {json_drg['loteGuias']['guia'][0]['codigoOperadora']}")
    print(f"📋 Número Guia: {json_drg['loteGuias']['guia'][0]['numeroGuia']}")
    print(f"📋 Hospital: {json_drg['loteGuias']['guia'][0]['nomeHospital']}")
    print(f"📋 Anexo: {len(anexo)} arquivo(s)")
    print()

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
