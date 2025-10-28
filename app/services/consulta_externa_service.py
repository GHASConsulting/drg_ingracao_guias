"""
Serviço para consulta externa de guias
"""

import httpx
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config.config import get_settings
from app.models.guias import Guia

logger = logging.getLogger(__name__)


class ConsultaExternaService:
    """Serviço para consultar guias em rotas externas"""

    def __init__(self):
        self.settings = get_settings()

    async def consultar_guia_externa(
        self,
        db: Session,
        numero_guia: str,
        data_ultima_atualizacao: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Consulta uma guia em uma rota externa

        Args:
            db: Sessão do banco de dados
            numero_guia: Número da guia para consultar
            data_ultima_atualizacao: Data da última atualização da guia (opcional)

        Returns:
            Dict com resultado da consulta
        """
        try:
            # Buscar guia no banco
            guia = db.query(Guia).filter(Guia.numero_guia == numero_guia).first()

            if not guia:
                return {
                    "sucesso": False,
                    "erro": f"Guia {numero_guia} não encontrada no banco de dados",
                }

            # Verificar se já foi consultada recentemente
            if self._deve_pular_consulta(guia, data_ultima_atualizacao):
                return {
                    "sucesso": True,
                    "mensagem": "Guia já foi consultada recentemente",
                    "dados": self._parse_dados_retornados(guia.dados_retornados),
                    "status_consulta": guia.status_consulta,
                }

            # Preparar parâmetros para consulta externa
            params = {
                "numero_guia": numero_guia,
                "data_ultima_atualizacao": (
                    data_ultima_atualizacao.isoformat()
                    if data_ultima_atualizacao
                    else guia.data_atualizacao.isoformat()
                ),
            }

            # Usar URL do .env
            url_destino = self.settings.CONSULTA_EXTERNA_URL

            # Fazer consulta externa
            resultado_consulta = await self._fazer_consulta_externa(url_destino, params)

            if resultado_consulta["sucesso"]:
                # Atualizar guia com dados retornados
                self._atualizar_guia_com_resultado(
                    db, guia, resultado_consulta["dados"]
                )

                return {
                    "sucesso": True,
                    "mensagem": "Consulta realizada com sucesso",
                    "dados": resultado_consulta["dados"],
                    "status_consulta": "R",  # Retornado
                }
            else:
                # Marcar como consultada mas com erro
                guia.status_consulta = "C"  # Consultado
                guia.data_ultima_consulta = datetime.utcnow()
                guia.mensagem_erro = resultado_consulta["erro"]
                guia.status_monitoramento = "M"  # Monitorando (para tentar novamente)
                db.commit()

                return {
                    "sucesso": False,
                    "erro": resultado_consulta["erro"],
                    "status_consulta": "C",
                }

        except Exception as e:
            logger.error(f"Erro ao consultar guia externa {numero_guia}: {e}")
            return {"sucesso": False, "erro": f"Erro interno: {str(e)}"}

    def _deve_pular_consulta(
        self, guia: Guia, data_ultima_atualizacao: Optional[datetime]
    ) -> bool:
        """
        Verifica se deve pular a consulta baseado no intervalo configurado
        """
        # Se já foi retornada (status R), não consultar novamente
        if guia.status_consulta == "R":
            return True

        # Se não tem data de última consulta, pode consultar
        if not guia.data_ultima_consulta:
            return False

        # Calcular diferença em milissegundos desde a última consulta
        diferenca_ms = (
            datetime.utcnow() - guia.data_ultima_consulta
        ).total_seconds() * 1000

        # Se passou menos tempo que o intervalo configurado, pular
        if diferenca_ms < self.settings.CONSULTA_EXTERNA_INTERVALO_MS:
            return True

        # Se a guia foi atualizada desde a última consulta, deve consultar novamente
        if data_ultima_atualizacao and guia.data_ultima_consulta:
            if data_ultima_atualizacao > guia.data_ultima_consulta:
                return False

        return False

    async def _fazer_consulta_externa(
        self, url: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Faz a consulta HTTP para a rota externa
        """
        timeout_ms = self.settings.CONSULTA_EXTERNA_TIMEOUT_MS
        timeout_seconds = timeout_ms / 1000

        try:
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                logger.info(f"Consultando URL externa: {url} com parâmetros: {params}")

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    dados = response.json()

                    # Verificar se a resposta indica sucesso
                    if self._verificar_resposta_sucesso(dados):
                        return {"sucesso": True, "dados": dados}
                    else:
                        return {
                            "sucesso": False,
                            "erro": f"Resposta da API indica erro: {dados.get('erro', 'Erro desconhecido')}",
                        }
                else:
                    return {
                        "sucesso": False,
                        "erro": f"Erro HTTP {response.status_code}: {response.text}",
                    }

        except httpx.TimeoutException:
            return {
                "sucesso": False,
                "erro": f"Timeout na consulta externa (>{timeout_ms}ms)",
            }
        except httpx.RequestError as e:
            return {"sucesso": False, "erro": f"Erro de conexão: {str(e)}"}
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro inesperado: {str(e)}"}

    def _verificar_resposta_sucesso(self, dados: Dict[str, Any]) -> bool:
        """
        Verifica se a resposta da API externa indica sucesso
        """
        # Verificar campos comuns de sucesso
        if isinstance(dados, dict):
            # Verificar se tem campo de sucesso
            if "success" in dados:
                return dados["success"] is True

            if "sucesso" in dados:
                return dados["sucesso"] is True

            # Verificar se tem campo de erro (se não tem erro, é sucesso)
            if "erro" in dados and dados["erro"]:
                return False

            if "error" in dados and dados["error"]:
                return False

            # Se não tem campos de erro, considerar sucesso
            return True

        return False

    def _atualizar_guia_com_resultado(
        self, db: Session, guia: Guia, dados: Dict[str, Any]
    ):
        """
        Atualiza a guia com os dados retornados da consulta externa
        Desmembra o JSON e atualiza campos específicos conforme necessário
        """
        try:
            # Atualizar campos básicos de controle
            guia.status_consulta = "R"  # Retornado
            guia.data_ultima_consulta = datetime.utcnow()
            guia.dados_retornados = json.dumps(dados, ensure_ascii=False)

            # Definir status de monitoramento baseado na situação da guia
            if guia.situacao_guia in ["A", "N"]:  # Aprovado ou Negado
                guia.status_monitoramento = "F"  # Finalizado
            else:
                guia.status_monitoramento = "M"  # Monitorando

            # Desmembrar e atualizar campos específicos
            self._desmembrar_e_atualizar_campos(db, guia, dados)

            db.commit()
            logger.info(
                f"Guia {guia.numero_guia} atualizada com dados da consulta externa"
            )

        except Exception as e:
            logger.error(f"Erro ao atualizar guia {guia.numero_guia}: {e}")
            db.rollback()
            raise

    def _desmembrar_e_atualizar_campos(
        self, db: Session, guia: Guia, dados: Dict[str, Any]
    ):
        """
        Desmembra o JSON de retorno e atualiza campos específicos da guia
        """
        try:
            logger.info(f"Iniciando desmembramento para guia {guia.numero_guia}")
            logger.info(f"Dados recebidos: {dados}")

            # 1. VERIFICAR APROVAÇÃO E STATUS
            aprovacao_detectada = self._verificar_aprovacao(dados)
            logger.info(f"Aprovação detectada: {aprovacao_detectada}")

            if aprovacao_detectada:
                guia.situacao_guia = "A"  # Aprovada
                guia.tp_status = "T"  # Transmitida
                logger.info(f"Guia {guia.numero_guia} aprovada via consulta externa")

            # 2. ATUALIZAR CAMPOS DE AUTORIZAÇÃO
            self._atualizar_campos_autorizacao(guia, dados)

            # 3. ATUALIZAR CAMPOS DE DIARIAS
            self._atualizar_campos_diarias(guia, dados)

            # 4. ATUALIZAR CAMPOS DE ACOMODAÇÃO
            self._atualizar_campos_acomodacao(guia, dados)

            # 5. ATUALIZAR CAMPOS DE ALTA
            self._atualizar_campos_alta(guia, dados)

            # 6. ATUALIZAR OBSERVAÇÕES
            self._atualizar_observacoes(guia, dados)

            logger.info(
                f"Campos desmembrados e atualizados para guia {guia.numero_guia}"
            )

            # Commit das mudanças
            db.commit()

        except Exception as e:
            logger.error(f"Erro ao desmembrar campos da guia {guia.numero_guia}: {e}")
            db.rollback()
            raise

    def _atualizar_campos_autorizacao(self, guia: Guia, dados: Dict[str, Any]):
        """Atualiza campos relacionados à autorização"""
        logger.info(f"Atualizando campos de autorização para guia {guia.numero_guia}")
        logger.info(f"Dados recebidos: {dados}")

        campos_autorizacao = {
            "numero_autorizacao": [
                "numero_autorizacao",
                "numeroAutorizacao",
                "autorizacao",
                "auth_number",
            ],
            "data_autorizacao": [
                "data_autorizacao",
                "dataAutorizacao",
                "data_aprovacao",
                "dataAprovacao",
            ],
            "cnes_autorizado": [
                "cnes_autorizado",
                "cnesAutorizado",
                "cnes",
                "cnes_aprovado",
            ],
            "senha_autorizacao": [
                "senha_autorizacao",
                "senhaAutorizacao",
                "senha_aprovacao",
                "senhaAprovacao",
                "senha_autorizada",
                "senhaAutorizada",
                "senha_retorno",
                "senhaRetorno",
            ],
            "justificativa_operadora": [
                "justificativa",
                "justificativa_operadora",
                "motivo",
                "observacao_operadora",
            ],
        }

        for campo_guia, campos_json in campos_autorizacao.items():
            valor = self._buscar_valor_em_campos(dados, campos_json)
            logger.info(f"Campo {campo_guia}: valor encontrado = {valor}")
            if valor:
                # Converter data se necessário
                if campo_guia == "data_autorizacao" and isinstance(valor, str):
                    try:
                        from datetime import datetime

                        valor = datetime.strptime(valor, "%Y-%m-%d").date()
                        logger.info(f"Data convertida: {valor}")
                    except ValueError:
                        logger.warning(f"Formato de data inválido: {valor}")
                        continue

                setattr(guia, campo_guia, valor)
                logger.info(f"Campo {campo_guia} atualizado: {valor}")
            else:
                logger.info(f"Campo {campo_guia}: nenhum valor encontrado")

    def _atualizar_campos_diarias(self, guia: Guia, dados: Dict[str, Any]):
        """Atualiza campos relacionados às diárias"""
        campos_diarias = {
            "qtde_diarias_autorizadas": [
                "diarias_autorizadas",
                "diariasAutorizadas",
                "qtde_diarias",
                "quantidade_diarias",
            ],
            "diarias_solicitadas": [
                "diarias_solicitadas",
                "diariasSolicitadas",
                "diarias_originais",
            ],
        }

        for campo_guia, campos_json in campos_diarias.items():
            valor = self._buscar_valor_em_campos(dados, campos_json)
            if valor:
                try:
                    # Converter para inteiro se possível
                    valor_int = int(valor) if str(valor).isdigit() else valor
                    setattr(guia, campo_guia, valor_int)
                    logger.debug(f"Campo {campo_guia} atualizado: {valor_int}")
                except (ValueError, TypeError):
                    logger.warning(
                        f"Não foi possível converter {valor} para inteiro no campo {campo_guia}"
                    )

    def _atualizar_campos_acomodacao(self, guia: Guia, dados: Dict[str, Any]):
        """Atualiza campos relacionados à acomodação"""
        campos_acomodacao = {
            "tipo_acomodacao_autorizada": [
                "tipo_acomodacao",
                "tipoAcomodacao",
                "acomodacao_autorizada",
                "acomodacaoAutorizada",
            ],
            "tipo_acomodacao_solicitada": [
                "acomodacao_solicitada",
                "acomodacaoSolicitada",
                "tipo_acomodacao_original",
            ],
        }

        for campo_guia, campos_json in campos_acomodacao.items():
            valor = self._buscar_valor_em_campos(dados, campos_json)
            if valor:
                setattr(guia, campo_guia, valor)
                logger.debug(f"Campo {campo_guia} atualizado: {valor}")

    def _atualizar_campos_alta(self, guia: Guia, dados: Dict[str, Any]):
        """Atualiza campos relacionados à alta"""
        campos_alta = {
            "data_alta": ["data_alta", "dataAlta", "data_da_alta", "dataDaAlta"],
            "tipo_alta": ["tipo_alta", "tipoAlta", "motivo_alta", "motivoAlta"],
            "motivo_encerramento": [
                "motivo_encerramento",
                "motivoEncerramento",
                "motivo_fechamento",
            ],
        }

        for campo_guia, campos_json in campos_alta.items():
            valor = self._buscar_valor_em_campos(dados, campos_json)
            if valor:
                # Se for data, converter para datetime
                if campo_guia == "data_alta" and isinstance(valor, str):
                    try:
                        from datetime import datetime

                        valor = datetime.fromisoformat(valor.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        logger.warning(
                            f"Não foi possível converter {valor} para data no campo {campo_guia}"
                        )
                        continue

                setattr(guia, campo_guia, valor)
                logger.debug(f"Campo {campo_guia} atualizado: {valor}")

    def _atualizar_observacoes(self, guia: Guia, dados: Dict[str, Any]):
        """Atualiza campos de observações"""
        campos_observacao = {
            "observacao_guia": [
                "observacao",
                "observacao_guia",
                "observacaoGuia",
                "comentarios",
                "notas",
            ],
            "justificativa_operadora": [
                "justificativa",
                "justificativa_operadora",
                "justificativaOperadora",
                "motivo_operadora",
            ],
        }

        for campo_guia, campos_json in campos_observacao.items():
            valor = self._buscar_valor_em_campos(dados, campos_json)
            if valor:
                # Se já tem observação, concatenar
                valor_atual = getattr(guia, campo_guia) or ""
                if valor_atual and valor:
                    nova_observacao = f"{valor_atual} | {valor}"
                else:
                    nova_observacao = valor or valor_atual

                setattr(guia, campo_guia, nova_observacao)
                logger.debug(f"Campo {campo_guia} atualizado: {nova_observacao}")

    def _buscar_valor_em_campos(
        self, dados: Dict[str, Any], campos_possiveis: list
    ) -> Any:
        """
        Busca um valor em diferentes campos possíveis do JSON
        """
        # Buscar em campos diretos
        for campo in campos_possiveis:
            if campo in dados:
                valor = dados[campo]
                if valor is not None and valor != "":
                    return valor

        # Buscar em subcampos (ex: dados.aprovacao.numero)
        for campo in campos_possiveis:
            if "." in campo:
                partes = campo.split(".")
                valor = dados
                try:
                    for parte in partes:
                        valor = valor[parte]
                    if valor is not None and valor != "":
                        return valor
                except (KeyError, TypeError):
                    continue

        # Buscar em campos aninhados
        for campo in campos_possiveis:
            valor = self._buscar_campo_aninhado(dados, campo)
            if valor is not None and valor != "":
                return valor

        return None

    def _buscar_campo_aninhado(self, dados: Dict[str, Any], campo: str) -> Any:
        """
        Busca um campo em estruturas aninhadas do JSON
        """
        if isinstance(dados, dict):
            # Buscar em todas as chaves (case insensitive)
            for chave, valor in dados.items():
                if chave.lower() == campo.lower():
                    return valor

                # Buscar recursivamente em sub-objetos
                if isinstance(valor, dict):
                    resultado = self._buscar_campo_aninhado(valor, campo)
                    if resultado is not None:
                        return resultado

                # Buscar em listas
                if isinstance(valor, list):
                    for item in valor:
                        if isinstance(item, dict):
                            resultado = self._buscar_campo_aninhado(item, campo)
                            if resultado is not None:
                                return resultado

        return None

    def _verificar_aprovacao(self, dados: Dict[str, Any]) -> bool:
        """
        Verifica se os dados indicam aprovação da guia
        """
        if isinstance(dados, dict):
            # Verificar campos comuns de aprovação
            campos_aprovacao = [
                "aprovada",
                "approved",
                "autorizada",
                "authorized",
                "status",
                "situacaoGuia",
                "situacao_guia",
                "statusProcessamento",
                "status_processamento",
            ]

            for campo in campos_aprovacao:
                if campo in dados:
                    valor = dados[campo]
                    if isinstance(valor, str):
                        valor_lower = valor.lower()
                        # Verificar se é "A" (Aprovado) ou contém palavras de aprovação
                        if valor == "A" or any(
                            palavra in valor_lower
                            for palavra in [
                                "aprov",
                                "autoriz",
                                "approved",
                                "authorized",
                                "aprovada",
                            ]
                        ):
                            return True
                    elif isinstance(valor, bool):
                        return valor

            # Verificar se tem dados de retorno (indica que foi processada)
            if "dados" in dados or "data" in dados:
                return True

        return False

    def _parse_dados_retornados(
        self, dados_json: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Converte string JSON para dicionário
        """
        if not dados_json:
            return None

        try:
            return json.loads(dados_json)
        except json.JSONDecodeError:
            return None

    async def consultar_multiplas_guias(
        self, db: Session, guias: list
    ) -> Dict[str, Any]:
        """
        Consulta múltiplas guias em lote
        """
        resultados = []
        sucessos = 0
        erros = 0

        for guia_info in guias:
            numero_guia = guia_info.get("numero_guia")
            data_ultima_atualizacao = guia_info.get("data_ultima_atualizacao")

            if not numero_guia:
                resultados.append(
                    {
                        "numero_guia": numero_guia,
                        "sucesso": False,
                        "erro": "Número da guia não informado",
                    }
                )
                erros += 1
                continue

            resultado = await self.consultar_guia_externa(
                db, numero_guia, data_ultima_atualizacao
            )

            resultados.append({"numero_guia": numero_guia, **resultado})

            if resultado["sucesso"]:
                sucessos += 1
            else:
                erros += 1

        return {
            "sucesso": erros == 0,
            "total_processadas": len(guias),
            "sucessos": sucessos,
            "erros": erros,
            "resultados": resultados,
        }
