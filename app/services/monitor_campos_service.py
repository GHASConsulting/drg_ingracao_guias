#!/usr/bin/env python3
"""
Serviço para monitoramento de campos de guias
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.database.database import get_session
from app.models import Guia
from app.services.drg_service import DRGService
from app.services.guia_service import GuiaService
from app.config.config import get_settings
from app.utils.logger import drg_logger


class MonitorCamposService:
    """Serviço para monitoramento de mudanças em campos de guias"""

    def __init__(self):
        self.settings = get_settings()
        self.drg_service = DRGService()
        self.guia_service = GuiaService()
        self.logger = logging.getLogger(__name__)

        # Controle de execução
        self._running = False
        self._task = None

        # Campos críticos para monitoramento
        self.campos_criticos = [
            "situacao_guia",
            "senha_autorizacao",
            "numero_autorizacao",
            "qtde_diarias_autorizadas",
            "tipo_acomodacao_autorizada",
            "cnes_autorizado",
            "data_autorizacao",
            "observacao_guia",
            "justificativa_operadora",
        ]

        # Campos que indicam status final
        self.status_final = ["A", "N"]  # Aprovado, Negado

        # Intervalo de monitoramento (em minutos)
        self.intervalo_monitoramento = getattr(
            self.settings, "MONITOR_CAMPOS_INTERVALO_MINUTES", 10
        )

    async def monitorar_guias(self) -> Dict[str, Any]:
        """
        Monitora guias com status_monitoramento = "M" e detecta mudanças
        """
        try:
            self.logger.info("🔍 Iniciando monitoramento de campos de guias...")

            with get_session() as db:
                # Buscar guias que estão sendo monitoradas
                guias_monitoramento = (
                    db.query(Guia).filter(Guia.status_monitoramento == "M").all()
                )

                if not guias_monitoramento:
                    self.logger.info("📭 Nenhuma guia em monitoramento encontrada")
                    return {
                        "sucesso": True,
                        "total_guias": 0,
                        "guias_processadas": 0,
                        "mudancas_detectadas": 0,
                        "puts_enviados": 0,
                    }

                # Filtrar guias que não devem mais ser monitoradas
                guias_validas = []
                guias_finalizadas = 0

                for guia in guias_monitoramento:
                    if self._deve_finalizar_monitoramento(guia):
                        # Finalizar monitoramento de guias negadas/aprovadas
                        guia.status_monitoramento = "F"
                        guias_finalizadas += 1
                        self.logger.info(
                            f"🏁 Finalizando monitoramento da guia {guia.numero_guia} "
                            f"(situacao: {guia.situacao_guia})"
                        )
                    else:
                        guias_validas.append(guia)

                # Commit das finalizações
                if guias_finalizadas > 0:
                    db.commit()
                    self.logger.info(
                        f"✅ {guias_finalizadas} guias finalizadas automaticamente"
                    )

                if not guias_validas:
                    self.logger.info("📭 Nenhuma guia válida para monitoramento")
                    return {
                        "sucesso": True,
                        "total_guias": len(guias_monitoramento),
                        "guias_processadas": 0,
                        "mudancas_detectadas": 0,
                        "puts_enviados": 0,
                        "guias_finalizadas": guias_finalizadas,
                    }

                self.logger.info(
                    f"📊 Encontradas {len(guias_validas)} guias válidas para monitoramento "
                    f"(total: {len(guias_monitoramento)}, finalizadas: {guias_finalizadas})"
                )

                # Processar cada guia
                guias_processadas = 0
                mudancas_detectadas = 0
                puts_enviados = 0

                for guia in guias_validas:
                    try:
                        resultado = await self._processar_guia(db, guia)
                        guias_processadas += 1

                        if resultado["mudanca_detectada"]:
                            mudancas_detectadas += 1

                        if resultado["put_enviado"]:
                            puts_enviados += 1

                    except Exception as e:
                        self.logger.error(
                            f"❌ Erro ao processar guia {guia.numero_guia}: {e}"
                        )
                        continue

                self.logger.info(
                    f"✅ Monitoramento concluído: {guias_processadas} guias processadas, "
                    f"{mudancas_detectadas} mudanças detectadas, {puts_enviados} PUTs enviados, "
                    f"{guias_finalizadas} guias finalizadas"
                )

                return {
                    "sucesso": True,
                    "total_guias": len(guias_monitoramento),
                    "guias_processadas": guias_processadas,
                    "mudancas_detectadas": mudancas_detectadas,
                    "puts_enviados": puts_enviados,
                    "guias_finalizadas": guias_finalizadas,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            self.logger.error(f"❌ Erro no monitoramento de campos: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _processar_guia(self, db: Session, guia: Guia) -> Dict[str, Any]:
        """
        Processa uma guia específica para detectar mudanças
        """
        try:
            # Verificar se a guia foi atualizada recentemente
            if not self._guia_foi_atualizada_recentemente(guia):
                return {
                    "mudanca_detectada": False,
                    "put_enviado": False,
                    "motivo": "Guia não foi atualizada recentemente",
                }

            # Detectar mudanças nos campos críticos
            campos_mudados = self._detectar_mudancas_campos(guia)

            # Verificar se senha foi preenchida por trigger
            if self._detectar_senha_preenchida(guia):
                self.logger.info(
                    f"🔍 Detectada guia aprovada com senha: {guia.numero_guia}"
                )

                # Enviar PUT específico para guia aprovada com senha
                resultado_put = await self._enviar_put_guia_aprovada(db, guia)

                if resultado_put["sucesso"]:
                    # Finalizar monitoramento após PUT bem-sucedido
                    guia.status_monitoramento = "F"
                    guia.tp_status = "T"  # Transmitida
                    db.commit()
                    self.logger.info(
                        f"✅ Guia completa enviada com sucesso para {guia.numero_guia}"
                    )
                    return {
                        "mudanca_detectada": True,
                        "put_enviado": True,
                        "motivo": "Senha preenchida - Guia completa enviada",
                        "tipo_put": "guia_aprovada",
                    }
                else:
                    self.logger.error(
                        f"❌ Falha ao enviar guia completa para {guia.numero_guia}: {resultado_put.get('erro')}"
                    )
                    return {
                        "mudanca_detectada": True,
                        "put_enviado": False,
                        "motivo": f"Falha no envio: {resultado_put.get('erro')}",
                        "tipo_put": "guia_aprovada",
                    }

            if not campos_mudados:
                return {
                    "mudanca_detectada": False,
                    "put_enviado": False,
                    "motivo": "Nenhuma mudança detectada",
                }

            self.logger.info(
                f"🔄 Mudanças detectadas na guia {guia.numero_guia}: {campos_mudados}"
            )

            # Verificar se deve finalizar monitoramento
            if self._deve_finalizar_monitoramento(guia):
                guia.status_monitoramento = "F"
                db.commit()
                self.logger.info(
                    f"🏁 Monitoramento finalizado para guia {guia.numero_guia}"
                )
                return {
                    "mudanca_detectada": True,
                    "put_enviado": False,
                    "motivo": "Monitoramento finalizado",
                }

            # Enviar PUT para DRG (mudanças normais)
            resultado_put = await self._enviar_put_drg(db, guia, campos_mudados)

            return {
                "mudanca_detectada": True,
                "put_enviado": resultado_put["sucesso"],
                "motivo": resultado_put.get("motivo", "PUT enviado"),
            }

        except Exception as e:
            self.logger.error(f"❌ Erro ao processar guia {guia.numero_guia}: {e}")
            return {
                "mudanca_detectada": False,
                "put_enviado": False,
                "motivo": f"Erro: {str(e)}",
            }

    def _guia_foi_atualizada_recentemente(self, guia: Guia) -> bool:
        """
        Verifica se a guia foi atualizada recentemente
        """
        if not guia.data_atualizacao:
            return False

        # Considerar atualizada se foi modificada nos últimos 30 minutos
        limite_tempo = datetime.utcnow() - timedelta(minutes=30)
        return guia.data_atualizacao >= limite_tempo

    def _detectar_mudancas_campos(self, guia: Guia) -> List[str]:
        """
        Detecta mudanças nos campos críticos da guia
        """
        campos_mudados = []

        # Verificar se algum campo crítico foi modificado
        # Como não temos histórico, vamos usar a data_atualizacao como indicador
        if guia.data_atualizacao and guia.data_atualizacao > guia.data_ultima_consulta:
            # Se foi atualizada após a última consulta, considerar que houve mudança
            campos_mudados = self.campos_criticos.copy()

        # Detectar senha preenchida por trigger quando guia for aprovada
        if self._detectar_senha_preenchida(guia):
            campos_mudados.append("senha_autorizacao_preenchida")

        return campos_mudados

    def _detectar_senha_preenchida(self, guia: Guia) -> bool:
        """
        Detecta se a senha_autorizacao foi preenchida por trigger.
        """
        return (
            guia.situacao_guia == "A"
            and guia.senha_autorizacao is not None
            and guia.senha_autorizacao.strip() != ""
        )

    def _deve_finalizar_monitoramento(self, guia: Guia) -> bool:
        """
        Verifica se deve finalizar o monitoramento da guia
        """
        # Finalizar se a situação da guia for final
        if guia.situacao_guia in self.status_final:
            return True

        # Finalizar se já foi consultada muitas vezes
        if (guia.tentativas or 0) >= 5:
            return True

        return False

    async def _enviar_put_drg(
        self, db: Session, guia: Guia, campos_mudados: List[str]
    ) -> Dict[str, Any]:
        """
        Envia POST para DRG com JSON completo da guia (mesma rota do envio inicial).
        Nota: Apesar do nome do método, agora sempre usa POST com JSON completo.
        """
        try:
            self.logger.info(
                f"📡 Enviando atualização para DRG - Guia {guia.numero_guia}"
            )

            # Montar JSON completo da guia
            json_completo = self.guia_service.montar_json_drg(guia)

            # Enviar JSON completo para DRG usando POST (mesma rota)
            resultado = self.drg_service.enviar_guia(json_completo)

            if resultado["sucesso"]:
                # Atualizar status da guia
                guia.tp_status = "T"  # Transmitida
                guia.tentativas = (guia.tentativas or 0) + 1
                guia.data_processamento = datetime.utcnow()
                guia.mensagem_erro = None

                db.commit()

                self.logger.info(
                    f"✅ Atualização enviada com sucesso para guia {guia.numero_guia}"
                )
                return {"sucesso": True, "motivo": "Atualização enviada com sucesso"}
            else:
                # Erro - verificar se é retentável
                erro_msg = resultado.get("erro", "Erro desconhecido")
                retentavel = resultado.get("retentavel", False)

                if retentavel:
                    # Erro retentável (500, timeout, conexão) - manter status atual
                    # O status_monitoramento já é "M", então continuará sendo monitorado
                    guia.mensagem_erro = erro_msg
                    self.logger.warning(
                        f"⚠️ Erro retentável ao enviar atualização para guia {guia.numero_guia} (será reenviado): {erro_msg}"
                    )
                else:
                    # Erro não-retentável (validação) - marcar como erro
                    guia.tp_status = "E"  # Erro
                    guia.mensagem_erro = erro_msg
                    self.logger.error(
                        f"❌ Erro ao enviar atualização para guia {guia.numero_guia}: {erro_msg}"
                    )

                db.commit()
                return {"sucesso": False, "motivo": f"Erro: {erro_msg}"}

        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar atualização para DRG: {e}")
            return {"sucesso": False, "motivo": f"Erro interno: {str(e)}"}

    async def _enviar_put_guia_aprovada(
        self, db: Session, guia: Guia
    ) -> Dict[str, Any]:
        """
        Envia POST para DRG com JSON completo da guia aprovada (mesma rota do envio inicial).
        Nota: Apesar do nome do método, agora sempre usa POST com JSON completo.
        """
        try:
            self.logger.info(
                f"📡 Enviando guia aprovada completa para DRG - {guia.numero_guia}"
            )

            # Montar JSON completo da guia usando o método existente
            json_completo = self.guia_service.montar_json_drg(guia)

            # O JSON já está completo com todos os campos, incluindo senha_autorizacao
            # Enviar JSON completo para DRG usando POST (mesma rota)
            resultado = self.drg_service.enviar_guia(json_completo)

            if resultado["sucesso"]:
                # Atualizar status da guia
                guia.tp_status = "T"  # Transmitida
                guia.tentativas = (guia.tentativas or 0) + 1
                guia.data_processamento = datetime.utcnow()
                guia.mensagem_erro = None

                db.commit()

                self.logger.info(
                    f"✅ Guia aprovada completa enviada com sucesso para {guia.numero_guia}"
                )
                return {
                    "sucesso": True,
                    "motivo": "Guia aprovada completa enviada com sucesso",
                }
            else:
                # Erro - verificar se é retentável
                erro_msg = resultado.get("erro", "Erro desconhecido")
                retentavel = resultado.get("retentavel", False)

                if retentavel:
                    # Erro retentável (500, timeout, conexão) - manter status atual
                    # O status_monitoramento já é "M", então continuará sendo monitorado
                    guia.mensagem_erro = erro_msg
                    self.logger.warning(
                        f"⚠️ Erro retentável ao enviar guia aprovada {guia.numero_guia} (será reenviado): {erro_msg}"
                    )
                else:
                    # Erro não-retentável (validação) - marcar como erro
                    guia.tp_status = "E"  # Erro
                    guia.mensagem_erro = erro_msg
                    self.logger.error(
                        f"❌ Erro ao enviar guia aprovada {guia.numero_guia}: {erro_msg}"
                    )

                db.commit()
                return {"sucesso": False, "motivo": f"Erro: {erro_msg}"}

        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar guia aprovada completa: {e}")
            return {"sucesso": False, "motivo": f"Erro interno: {str(e)}"}

    async def iniciar_monitoramento_continuo(self):
        """
        Inicia monitoramento contínuo das guias
        """
        self.logger.info(
            f"🚀 Iniciando monitoramento contínuo (intervalo: {self.intervalo_monitoramento} min)"
        )

        while self._running:
            try:
                await self.monitorar_guias()

                # Aguardar próximo ciclo
                await asyncio.sleep(self.intervalo_monitoramento * 60)

            except asyncio.CancelledError:
                self.logger.info("🔄 Monitoramento contínuo cancelado")
                break
            except Exception as e:
                self.logger.error(f"❌ Erro no monitoramento contínuo: {e}")
                await asyncio.sleep(60)  # Aguardar 1 minuto antes de tentar novamente

        self.logger.info("🛑 Monitoramento contínuo finalizado")

    def obter_estatisticas_monitoramento(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do monitoramento
        """
        try:
            with get_session() as db:
                # Contar guias por status de monitoramento
                total_guias = db.query(Guia).count()
                nao_monitorando = (
                    db.query(Guia).filter(Guia.status_monitoramento == "N").count()
                )
                monitorando = (
                    db.query(Guia).filter(Guia.status_monitoramento == "M").count()
                )
                finalizadas = (
                    db.query(Guia).filter(Guia.status_monitoramento == "F").count()
                )

                return {
                    "timestamp": datetime.utcnow().isoformat(),
                    "estatisticas": {
                        "total_guias": total_guias,
                        "nao_monitorando": nao_monitorando,
                        "monitorando": monitorando,
                        "finalizadas": finalizadas,
                    },
                    "configuracoes": {
                        "intervalo_minutos": self.intervalo_monitoramento,
                        "campos_criticos": self.campos_criticos,
                        "status_final": self.status_final,
                    },
                }

        except Exception as e:
            self.logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {"erro": str(e), "timestamp": datetime.utcnow().isoformat()}


# Instância global do serviço
monitor_campos_service = MonitorCamposService()
