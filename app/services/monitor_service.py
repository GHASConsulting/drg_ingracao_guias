#!/usr/bin/env python3
"""
Serviço de monitoramento automático da tabela de guias
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database.database import get_session
from app.models import Guia
from app.services.drg_service import DRGService
from app.services.guia_service import GuiaService
from app.config.config import get_settings
from app.utils.logger import drg_logger


class MonitorService:
    """Serviço para monitoramento automático da tabela de guias"""

    def _is_retentable_error_from_message(self, error_msg: str) -> bool:
        """
        Verifica se uma mensagem de erro indica erro retentável (500, 504, timeout, connection, etc).

        Args:
            error_msg: Mensagem de erro a verificar

        Returns:
            bool: True se o erro é retentável, False caso contrário
        """
        if not error_msg:
            return False

        error_lower = str(error_msg).lower()

        # Erros HTTP retentáveis
        retentable_patterns = [
            "500",  # Internal Server Error
            "502",  # Bad Gateway
            "503",  # Service Unavailable
            "504",  # Gateway Timeout
            "timeout",
            "gateway timeout",
            "connection",
            "conexão",
            "network",
            "rede",
            "unavailable",
            "indisponível",
            "server error",
            "erro interno",
            "internal server",
            "temporarily",
            "temporariamente",
            "service unavailable",
            "bad gateway",
        ]

        return any(pattern in error_lower for pattern in retentable_patterns)

    def __init__(self):
        self.settings = get_settings()
        self.drg_service = DRGService()
        self.guia_service = GuiaService()
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._task = None
        self.auto_reprocess = os.getenv("AUTO_REPROCESS", "true").lower() == "true"

    async def start_monitoring(self):
        """Inicia o monitoramento automático"""
        if not self.settings.AUTO_MONITOR_ENABLED:
            self.logger.info("🔕 Monitoramento automático desabilitado")
            return

        if self.settings.MONITOR_INTERVAL_MINUTES <= 0:
            self.logger.info("🔕 Monitoramento automático desabilitado (intervalo = 0)")
            return

        if self._running:
            self.logger.warning("⚠️ Monitoramento já está em execução")
            return

        self._running = True
        self.logger.info(
            f"🚀 Iniciando monitoramento automático (intervalo: {self.settings.MONITOR_INTERVAL_MINUTES} min)"
        )

        # Iniciar task em background
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self):
        """Para o monitoramento automático"""
        if not self._running:
            self.logger.warning("⚠️ Monitoramento não está em execução")
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self.logger.info("🛑 Monitoramento automático parado")

    async def _monitor_loop(self):
        """Loop principal do monitoramento"""
        try:
            while self._running:
                try:
                    await self._process_pending_guias()
                except Exception as e:
                    self.logger.error(f"❌ Erro no monitoramento: {e}")

                # Aguardar próximo ciclo
                await asyncio.sleep(self.settings.MONITOR_INTERVAL_MINUTES * 60)

        except asyncio.CancelledError:
            self.logger.info("🔄 Monitoramento cancelado")
            raise
        except Exception as e:
            self.logger.error(f"❌ Erro fatal no monitoramento: {e}")
            self._running = False

    async def _process_pending_guias(self):
        """Processa todas as guias pendentes, enviando em lotes de 5 para a API"""
        try:
            # Obter sessão do banco
            session = get_session()

            try:
                # Buscar TODAS as guias aguardando processamento (sem limite)
                if self.auto_reprocess:
                    # Buscar todas as guias aguardando (tp_status = 'A')
                    # E também guias com erro retentável (tp_status = 'E' mas com erro 504, 500, timeout, etc)
                    guias_pendentes = (
                        session.query(Guia)
                        .filter(
                            or_(
                                Guia.tp_status == "A",  # Aguardando
                                # Guias com erro mas que são retentáveis (504, 500, timeout, etc)
                                and_(
                                    Guia.tp_status == "E",
                                    or_(
                                        Guia.mensagem_erro.like("%504%"),
                                        Guia.mensagem_erro.like("%500%"),
                                        Guia.mensagem_erro.like("%timeout%"),
                                        Guia.mensagem_erro.like("%Timeout%"),
                                        Guia.mensagem_erro.like("%TIMEOUT%"),
                                        Guia.mensagem_erro.like("%Gateway Timeout%"),
                                        Guia.mensagem_erro.like("%gateway timeout%"),
                                        Guia.mensagem_erro.like("%connection%"),
                                        Guia.mensagem_erro.like("%Connection%"),
                                        Guia.mensagem_erro.like("%conexão%"),
                                        Guia.mensagem_erro.like("%Conexão%"),
                                        Guia.mensagem_erro.like("%502%"),
                                        Guia.mensagem_erro.like("%503%"),
                                    ),
                                ),
                            )
                        )
                        .all()
                    )
                else:
                    # Buscar apenas guias que nunca foram tentadas
                    guias_pendentes = (
                        session.query(Guia)
                        .filter(Guia.tp_status == "A")  # Aguardando
                        .filter(
                            (Guia.tentativas == 0) | (Guia.tentativas.is_(None))
                        )  # Só primeira tentativa
                        .all()
                    )

                if not guias_pendentes:
                    self.logger.debug("📋 Nenhuma guia pendente encontrada")
                    return

                total_guias = len(guias_pendentes)
                batch_size = self.settings.MONITOR_BATCH_SIZE

                self.logger.info(
                    f"📋 Encontradas {total_guias} guias pendentes. Processando em lotes de {batch_size}..."
                )

                # Processar em lotes de 5 (ou o tamanho configurado)
                total_lotes = (
                    total_guias + batch_size - 1
                ) // batch_size  # Arredondar para cima

                for lote_num in range(total_lotes):
                    inicio = lote_num * batch_size
                    fim = min(inicio + batch_size, total_guias)
                    lote_guias = guias_pendentes[inicio:fim]

                    self.logger.info(
                        f"📦 Processando lote {lote_num + 1}/{total_lotes} ({len(lote_guias)} guias: {inicio + 1}-{fim})"
                    )

                    # Processar este lote
                    await self._process_lote_guias(session, lote_guias)

                    # Pequena pausa entre lotes para não sobrecarregar a API
                    if lote_num < total_lotes - 1:  # Não pausar após o último lote
                        await asyncio.sleep(1)  # 1 segundo entre lotes

                self.logger.info(
                    f"✅ Ciclo completo: {total_guias} guias processadas em {total_lotes} lotes"
                )

            finally:
                session.close()

        except Exception as e:
            self.logger.error(f"❌ Erro ao acessar banco de dados: {e}")

    async def _process_lote_guias(self, session: Session, guias: List[Guia]):
        """Processa um lote de guias"""
        try:
            self.logger.info(f"🚀 Processando lote de {len(guias)} guias")

            # Marcar todas as guias como processando
            # Se alguma guia estava com tp_status = "E" mas tem erro retentável, apenas logar
            for guia in guias:
                # Se estava com erro mas é retentável, logar para debug
                if guia.tp_status == "E" and guia.mensagem_erro:
                    erro_msg_lower = (guia.mensagem_erro or "").lower()
                    erros_retentaveis = [
                        "504",
                        "500",
                        "502",
                        "503",
                        "timeout",
                        "connection",
                        "conexão",
                        "gateway",
                    ]
                    if any(erro in erro_msg_lower for erro in erros_retentaveis):
                        self.logger.info(
                            f"🔄 Reprocessando guia {guia.numero_guia} com erro retentável (era 'E', agora será processada)"
                        )

                guia.tp_status = "P"
                if self.auto_reprocess:
                    # Garantir que tentativas não seja None
                    guia.tentativas = (guia.tentativas or 0) + 1
                else:
                    # Sem incremento de tentativas quando reprocessamento está desabilitado
                    if guia.tentativas is None or guia.tentativas == 0:
                        guia.tentativas = 1
                guia.data_processamento = datetime.utcnow()

            session.commit()

            # Processar lote usando GuiaService
            resultado = self.guia_service.processar_lote_guias(guias, self.drg_service)

            if resultado.get("sucesso"):
                # Sucesso - marcar todas como transmitidas
                for guia in guias:
                    guia.tp_status = "T"
                    guia.mensagem_erro = None

                self.logger.info(
                    f"✅ Lote de {len(guias)} guias processado com sucesso"
                )
            else:
                # Erro - verificar se é retentável
                erro_msg = resultado.get("erro", "Erro desconhecido")
                retentavel = resultado.get("retentavel", False)

                # Verificação adicional: mesmo se retentavel=False, verificar na mensagem de erro
                # Isso garante que erros 500, 504, timeout, etc sempre resultem em tp_status = "A"
                if not retentavel:
                    retentavel = self._is_retentable_error_from_message(erro_msg)

                if retentavel:
                    # Erro retentável (500, 504, timeout, conexão, etc) - manter status 'A' para reenvio
                    for guia in guias:
                        guia.tp_status = "A"  # Voltar para Aguardando
                        guia.mensagem_erro = erro_msg
                        # Não incrementar tentativas aqui, já foi incrementado antes

                    self.logger.warning(
                        f"⚠️ Erro retentável no lote (será reenviado): {erro_msg}"
                    )
                else:
                    # Erro não-retentável (validação) - marcar como erro
                    for guia in guias:
                        guia.tp_status = "E"
                        guia.mensagem_erro = erro_msg

                    self.logger.error(f"❌ Erro ao processar lote: {erro_msg}")

            # Atualizar data de processamento
            for guia in guias:
                guia.data_processamento = datetime.utcnow()

            session.commit()

        except Exception as e:
            # Erro crítico - verificar se é retentável (ex: erro de conexão com banco)
            error_msg = f"Erro crítico: {str(e)}"

            # Verificar se é erro retentável usando a função auxiliar
            is_retentable = self._is_retentable_error_from_message(error_msg)

            for guia in guias:
                if is_retentable:
                    # Erro retentável (500, 504, timeout, connection, etc) - manter status 'A'
                    guia.tp_status = "A"
                else:
                    # Erro não-retentável - marcar como erro
                    guia.tp_status = "E"

                guia.mensagem_erro = error_msg
                if self.auto_reprocess:
                    # Garantir que tentativas não seja None
                    guia.tentativas = (guia.tentativas or 0) + 1
                else:
                    # Sem incremento de tentativas quando reprocessamento está desabilitado
                    if guia.tentativas is None or guia.tentativas == 0:
                        guia.tentativas = 1
                guia.data_processamento = datetime.utcnow()

            session.commit()
            if is_retentable:
                self.logger.warning(
                    f"⚠️ Erro crítico retentável ao processar lote (será reenviado): {e}"
                )
            else:
                self.logger.error(f"❌ Erro crítico ao processar lote: {e}")
            raise

    async def _process_single_guia(self, session: Session, guia: Guia):
        """Processa uma única guia"""
        try:
            self.logger.info(f"🔄 Processando guia {guia.numero_guia} (ID: {guia.id})")

            # Marcar como processando
            guia.tp_status = "P"
            if self.auto_reprocess:
                # Garantir que tentativas não seja None
                guia.tentativas = (guia.tentativas or 0) + 1
            else:
                # Sem incremento de tentativas quando reprocessamento está desabilitado
                if guia.tentativas is None or guia.tentativas == 0:
                    guia.tentativas = 1
            guia.data_processamento = datetime.utcnow()
            session.commit()

            # Processar guia
            resultado = self.guia_service.processar_guia_completa(
                guia, self.drg_service
            )

            if resultado.get("sucesso"):
                # Sucesso
                guia.tp_status = "T"
                guia.mensagem_erro = None
                self.logger.info(f"✅ Guia {guia.numero_guia} processada com sucesso")
            else:
                # Erro - verificar se é retentável
                erro_msg = resultado.get("erro", "Erro desconhecido")
                retentavel = resultado.get("retentavel", False)

                # Verificação adicional: mesmo se retentavel=False, verificar na mensagem de erro
                # Isso garante que erros 500, 504, timeout, etc sempre resultem em tp_status = "A"
                if not retentavel:
                    retentavel = self._is_retentable_error_from_message(erro_msg)

                if retentavel:
                    # Erro retentável (500, 504, timeout, conexão, etc) - manter status 'A' para reenvio
                    guia.tp_status = "A"  # Voltar para Aguardando
                    guia.mensagem_erro = erro_msg
                    # Não incrementar tentativas aqui, já foi incrementado antes
                    self.logger.warning(
                        f"⚠️ Erro retentável na guia {guia.numero_guia} (será reenviada): {erro_msg}"
                    )
                else:
                    # Erro não-retentável (validação) - marcar como erro
                    guia.tp_status = "E"
                    guia.mensagem_erro = erro_msg
                    self.logger.error(
                        f"❌ Erro ao processar guia {guia.numero_guia}: {erro_msg}"
                    )

            guia.data_processamento = datetime.utcnow()
            session.commit()

        except Exception as e:
            # Erro crítico - verificar se é retentável
            error_msg = f"Erro crítico: {str(e)}"

            # Verificar se é erro retentável usando a função auxiliar
            is_retentable = self._is_retentable_error_from_message(error_msg)

            if is_retentable:
                # Erro retentável (500, 504, timeout, connection, etc) - manter status 'A'
                guia.tp_status = "A"
                self.logger.warning(
                    f"⚠️ Erro crítico retentável na guia {guia.numero_guia} (será reenviada): {e}"
                )
            else:
                # Erro não-retentável - marcar como erro
                guia.tp_status = "E"
                self.logger.error(f"❌ Erro crítico na guia {guia.numero_guia}: {e}")

            guia.mensagem_erro = error_msg
            if self.auto_reprocess:
                # Garantir que tentativas não seja None
                guia.tentativas = (guia.tentativas or 0) + 1
            else:
                # Sem incremento de tentativas quando reprocessamento está desabilitado
                if guia.tentativas is None or guia.tentativas == 0:
                    guia.tentativas = 1
            guia.data_processamento = datetime.utcnow()
            session.commit()
            raise

    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Retorna status do monitoramento"""
        session = get_session()
        try:
            # Contar guias por status
            total_guias = session.query(Guia).count()
            aguardando = session.query(Guia).filter(Guia.tp_status == "A").count()
            processando = session.query(Guia).filter(Guia.tp_status == "P").count()
            transmitidas = session.query(Guia).filter(Guia.tp_status == "T").count()
            com_erro = session.query(Guia).filter(Guia.tp_status == "E").count()

            return {
                "monitoramento_ativo": self._running,
                "intervalo_minutos": self.settings.MONITOR_INTERVAL_MINUTES,
                "auto_monitor_enabled": self.settings.AUTO_MONITOR_ENABLED,
                "auto_reprocess_enabled": self.auto_reprocess,
                "total_guias": total_guias,
                "aguardando": aguardando,
                "processando": processando,
                "transmitidas": transmitidas,
                "com_erro": com_erro,
                "ultima_verificacao": datetime.utcnow().isoformat(),
            }
        finally:
            session.close()


# Instância global do monitor
monitor_service = MonitorService()
