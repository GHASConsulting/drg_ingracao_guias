from datetime import datetime
from typing import Dict, Any
from app.models import Guia, Anexo, Procedimento, Diagnostico
from app.utils.logger import drg_logger


class GuiaService:
    """Serviço para operações com guias."""

    def montar_json_drg(self, guia: Guia) -> Dict[str, Any]:
        """Monta o JSON no formato esperado pela API DRG."""

        # Estrutura base
        json_drg = {
            "loteGuias": {
                "guia": [
                    {
                        # Campos principais
                        "codigoOperadora": guia.codigo_operadora,
                        "numeroGuia": guia.numero_guia,
                        "numeroGuiaOperadora": guia.numero_guia_operadora,
                        "numeroGuiaInternacao": guia.numero_guia_internacao,
                        "dataAutorizacao": self._format_date(guia.data_autorizacao),
                        "senha": guia.senha,
                        "dataValidade": self._format_date(guia.data_validade),
                        # Dados do beneficiário
                        "numeroCarteira": guia.numero_carteira,
                        "dataValidadeCarteira": self._format_date(
                            guia.data_validade_carteira
                        ),
                        "rn": guia.rn,
                        "dataNascimento": self._format_date(guia.data_nascimento),
                        "sexo": guia.sexo,
                        "situacaoBeneficiario": guia.situacao_beneficiario,
                        # Dados do prestador
                        "codigoPrestador": guia.codigo_prestador,
                        "nomePrestador": guia.nome_prestador,
                        "nomeProfissional": guia.nome_profissional,
                        "codigoProfissional": guia.codigo_profissional,
                        "numeroRegistroProfissional": guia.numero_registro_profissional,
                        "ufProfissional": guia.uf_profissional,
                        "codigoCbo": guia.codigo_cbo,
                        # Dados do hospital
                        "codigoContratado": guia.codigo_contratado,
                        "nomeHospital": guia.nome_hospital,
                        "dataSugeridaInternacao": self._format_date(
                            guia.data_sugerida_internacao
                        ),
                        "caraterAtendimento": guia.carater_atendimento,
                        "tipoInternacao": guia.tipo_internacao,
                        "regimeInternacao": guia.regime_internacao,
                        "diariasSolicitadas": str(guia.diarias_solicitadas),
                        "previsaoUsoOpme": guia.previsao_uso_opme,
                        "previsaoUsoQuimioterapico": guia.previsao_uso_quimioterapico,
                        "indicacaoClinica": guia.indicacao_clinica,
                        "indicacaoAcidente": guia.indicacao_acidente,
                        "tipoAcomodacaoSolicitada": guia.tipo_acomodacao_solicitada,
                        # Dados da autorização
                        "dataAdmissaoEstimada": self._format_date(
                            guia.data_admissao_estimada
                        ),
                        "qtdeDiariasAutorizadas": (
                            str(guia.qtde_diarias_autorizadas)
                            if guia.qtde_diarias_autorizadas
                            else None
                        ),
                        "tipoAcomodacaoAutorizada": guia.tipo_acomodacao_autorizada,
                        "cnesAutorizado": guia.cnes_autorizado,
                        "observacaoGuia": guia.observacao_guia,
                        "dataSolicitacao": self._format_date(guia.data_solicitacao),
                        "justificativaOperadora": guia.justificativa_operadora,
                        # Dados complementares
                        "naturezaGuia": guia.natureza_guia,
                        "guiaComplementar": guia.guia_complementar,
                        "situacaoGuia": guia.situacao_guia,
                        "tipoDoenca": guia.tipo_doenca,
                        "tempoDoenca": (
                            str(guia.tempo_doenca) if guia.tempo_doenca else None
                        ),
                        "longaPermanencia": guia.longa_permanencia,
                        "motivoEncerramento": guia.motivo_encerramento,
                        "tipoAlta": guia.tipo_alta,
                        "dataAlta": self._format_date(guia.data_alta),
                        # Relacionamentos
                        "anexo": self._montar_anexos(guia.anexos),
                        "procedimento": self._montar_procedimentos(guia.procedimentos),
                        "diagnostico": self._montar_diagnosticos(guia.diagnosticos),
                    }
                ]
            }
        }

        return json_drg

    def _format_date(self, date_value) -> str:
        """Formata data para string no formato esperado pela API DRG."""
        if not date_value:
            return ""

        if isinstance(date_value, datetime):
            # Formato: "2025-08-02" ou "2025-08-02 00:00"
            return date_value.strftime("%Y-%m-%d %H:%M")

        return (
            date_value.isoformat()
            if hasattr(date_value, "isoformat")
            else str(date_value)
        )

    def _montar_anexos(self, anexos) -> list:
        """Monta lista de anexos."""
        if not anexos:
            return []

        return [
            {
                "numeroLoteDocumento": anexo.numero_lote_documento,
                "numeroProtocoloDocumento": anexo.numero_protocolo_documento,
                "formatoDocumento": anexo.formato_documento,
                "sequencialDocumento": anexo.sequencial_documento,
                "dataCriacao": self._format_date(anexo.data_criacao),
                "nome": anexo.nome,
                "urlDocumento": anexo.url_documento,
                "observacaoDocumento": anexo.observacao_documento,
                "tipoDocumento": anexo.tipo_documento,
            }
            for anexo in anexos
        ]

    def _montar_procedimentos(self, procedimentos) -> list:
        """Monta lista de procedimentos."""
        if not procedimentos:
            return []

        return [
            {
                "tabela": procedimento.tabela,
                "codigo": procedimento.codigo,
                "descricao": procedimento.descricao,
                "qtdeSolicitada": str(procedimento.qtde_solicitada),
                "valorUnitario": str(procedimento.valor_unitario),
                "qtdeAutorizada": (
                    str(procedimento.qtde_autorizada)
                    if procedimento.qtde_autorizada
                    else ""
                ),
                "nome": procedimento.nome if hasattr(procedimento, "nome") else "",
            }
            for procedimento in procedimentos
        ]

    def _montar_diagnosticos(self, diagnosticos) -> list:
        """Monta lista de diagnósticos."""
        if not diagnosticos:
            return []

        return [
            {"codigo": diagnostico.codigo, "tipo": diagnostico.tipo}
            for diagnostico in diagnosticos
        ]

    def montar_lote_drg(self, guias: list) -> Dict[str, Any]:
        """Monta JSON para lote de guias no formato da API DRG."""
        if not guias:
            return {"loteGuias": {"guia": []}}

        # Montar lista de guias
        guias_json = []
        for guia in guias:
            guia_json = self.montar_json_drg(guia)
            # Extrair apenas a guia individual (remover o wrapper loteGuias)
            if "loteGuias" in guia_json and "guia" in guia_json["loteGuias"]:
                guias_json.extend(guia_json["loteGuias"]["guia"])

        return {"loteGuias": {"guia": guias_json}}

    def processar_guia_completa(self, guia: Guia, drg_service) -> Dict[str, Any]:
        """Processa uma guia completa: monta JSON e envia para DRG."""
        try:
            # Montar JSON da guia
            json_drg = self.montar_json_drg(guia)

            # Enviar para DRG
            resultado = drg_service.enviar_guia(json_drg)

            if resultado.get("sucesso"):
                drg_logger.log_guide_processing(
                    guia.id, guia.numero_guia, json_drg, True, resultado
                )
                return {
                    "sucesso": True,
                    "mensagem": "Guia processada com sucesso",
                    "resposta_drg": resultado,
                }
            else:
                drg_logger.log_guide_processing(
                    guia.id,
                    guia.numero_guia,
                    json_drg,
                    False,
                    resultado,
                    resultado.get("erro", "Erro desconhecido"),
                )
                return {
                    "sucesso": False,
                    "erro": resultado.get("erro", "Erro ao enviar para DRG"),
                    "resposta_drg": resultado,
                }

        except Exception as e:
            drg_logger.log_error(f"Erro ao processar guia {guia.numero_guia}: {str(e)}")
            return {"sucesso": False, "erro": str(e)}
