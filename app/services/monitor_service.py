#!/usr/bin/env python3
"""
Serviço de monitoramento automático da tabela de guias
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.database.database import get_session
from app.models import Guia
from app.services.drg_service import DRGService
from app.services.guia_service import GuiaService
from app.config.config import get_settings
from app.utils.logger import drg_logger


class MonitorService:
    """Serviço para monitoramento automático da tabela de guias"""

    def __init__(self):
        self.settings = get_settings()
        self.drg_service = DRGService()
        self.guia_service = GuiaService()
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._task = None

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
        """Processa guias pendentes em lote"""
        try:
            # Obter sessão do banco
            session = get_session()

            try:
                # Buscar guias aguardando processamento
                guias_pendentes = (
                    session.query(Guia)
                    .filter(Guia.tp_status == "A")  # Aguardando
                    .limit(10)
                    .all()
                )  # Processar até 10 por vez

                if not guias_pendentes:
                    self.logger.debug("📋 Nenhuma guia pendente encontrada")
                    return

                self.logger.info(
                    f"📋 Encontradas {len(guias_pendentes)} guias pendentes"
                )

                # Processar lote de guias
                await self._process_lote_guias(session, guias_pendentes)

            finally:
                session.close()

        except Exception as e:
            self.logger.error(f"❌ Erro ao acessar banco de dados: {e}")

    async def _process_lote_guias(self, session: Session, guias: List[Guia]):
        """Processa um lote de guias"""
        try:
            self.logger.info(f"🚀 Processando lote de {len(guias)} guias")

            # Marcar todas as guias como processando
            for guia in guias:
                guia.tp_status = "P"
                guia.tentativas += 1
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
                # Erro - marcar todas como erro
                erro_msg = resultado.get("erro", "Erro desconhecido")
                for guia in guias:
                    guia.tp_status = "E"
                    guia.mensagem_erro = erro_msg

                self.logger.error(f"❌ Erro ao processar lote: {erro_msg}")

            # Atualizar data de processamento
            for guia in guias:
                guia.data_processamento = datetime.utcnow()

            session.commit()

        except Exception as e:
            # Erro crítico - marcar todas como erro
            for guia in guias:
                guia.tp_status = "E"
                guia.mensagem_erro = f"Erro crítico: {str(e)}"
                guia.tentativas += 1
                guia.data_processamento = datetime.utcnow()

            session.commit()
            self.logger.error(f"❌ Erro crítico ao processar lote: {e}")
            raise

    async def _process_single_guia(self, session: Session, guia: Guia):
        """Processa uma única guia"""
        try:
            self.logger.info(f"🔄 Processando guia {guia.numero_guia} (ID: {guia.id})")

            # Marcar como processando
            guia.tp_status = "P"
            guia.tentativas += 1
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
                # Erro
                guia.tp_status = "E"
                guia.mensagem_erro = resultado.get("erro", "Erro desconhecido")
                self.logger.error(
                    f"❌ Erro ao processar guia {guia.numero_guia}: {resultado.get('erro')}"
                )

            guia.data_processamento = datetime.utcnow()
            session.commit()

        except Exception as e:
            # Erro crítico
            guia.tp_status = "E"
            guia.mensagem_erro = f"Erro crítico: {str(e)}"
            guia.tentativas += 1
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
