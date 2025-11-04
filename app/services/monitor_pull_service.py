#!/usr/bin/env python3
"""
Serviço de monitoramento PULL para consumir atualizações da API DRG
Implementa a regra de conflito simultâneo (≤ 1 minuto)
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


class MonitorPullService:
    """Serviço para monitoramento PULL (buscar atualizações da DRG)"""

    def __init__(self):
        self.settings = get_settings()
        self.drg_service = DRGService()
        self.guia_service = GuiaService()
        self.logger = logging.getLogger(__name__)

        # Controle de execução
        self._running = False
        self._task = None
        
        # Controle de conflito simultâneo (ultima execução)
        self._last_execution_time: Optional[datetime] = None
        self._last_execution_lock = asyncio.Lock()

    async def iniciar_monitoramento_pull(self):
        """Inicia o monitoramento PULL"""
        if not self.settings.MONITOR_PULL_ENABLED:
            self.logger.info("🔕 Monitoramento PULL desabilitado")
            return

        if self.settings.MONITOR_PULL_INTERVAL_MINUTES <= 0:
            self.logger.info("🔕 Monitoramento PULL desabilitado (intervalo = 0)")
            return

        if self._running:
            self.logger.warning("⚠️ Monitoramento PULL já está em execução")
            return

        self._running = True
        self.logger.info(
            f"🚀 Iniciando monitoramento PULL (intervalo: {self.settings.MONITOR_PULL_INTERVAL_MINUTES} min)"
        )

        # Iniciar task em background
        self._task = asyncio.create_task(self._loop_monitoramento_pull())

    async def parar_monitoramento_pull(self):
        """Para o monitoramento PULL"""
        if not self._running:
            self.logger.warning("⚠️ Monitoramento PULL não está em execução")
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self.logger.info("🛑 Monitoramento PULL parado")

    async def _loop_monitoramento_pull(self):
        """Loop principal do monitoramento PULL"""
        try:
            while self._running:
                try:
                    # Verificar conflito simultâneo antes de executar
                    if await self._verificar_conflito_simultaneo():
                        self.logger.warning("⏸️ Conflito simultâneo detectado, aguardando...")
                        await asyncio.sleep(10)  # Aguardar 10 segundos
                        continue
                    
                    # Processar atualizações
                    await self._processar_atualizacoes_pull()
                except Exception as e:
                    self.logger.error(f"❌ Erro no monitoramento PULL: {e}")

                # Aguardar próximo ciclo
                await asyncio.sleep(self.settings.MONITOR_PULL_INTERVAL_MINUTES * 60)

        except asyncio.CancelledError:
            self.logger.info("🔄 Monitoramento PULL cancelado")
            raise
        except Exception as e:
            self.logger.error(f"❌ Erro fatal no monitoramento PULL: {e}")
            self._running = False

    async def _verificar_conflito_simultaneo(self) -> bool:
        """
        Verifica se há conflito simultâneo (duas execuções em menos de 1 minuto).
        
        Regra: Se a última execução foi há menos de 1 minuto, aguardar.
        
        Returns:
            bool: True se há conflito (deve aguardar), False caso contrário
        """
        async with self._last_execution_lock:
            agora = datetime.utcnow()
            
            # Se nunca executou, não há conflito
            if self._last_execution_time is None:
                self._last_execution_time = agora
                return False
            
            # Calcular diferença
            delta = agora - self._last_execution_time
            
            # Se passou menos de 1 minuto, há conflito
            if delta.total_seconds() < 60:
                self.logger.warning(
                    f"⚠️ Conflito simultâneo: última execução há {delta.total_seconds():.0f}s"
                )
                return True
            
            # Não há conflito, atualizar timestamp
            self._last_execution_time = agora
            return False

    async def _processar_atualizacoes_pull(self):
        """Processa atualizações buscadas da API PULL"""
        session = None
        try:
            session = get_session()
            self.logger.info("🔍 Buscando atualizações da DRG via PULL...")

            # Buscar guias monitoradas que foram enviadas recentemente
            # Considerar guias enviadas nas últimas 24 horas
            # Usar tp_status='T' (Transmitido) para guias enviadas com sucesso
            data_limite = datetime.utcnow() - timedelta(hours=24)
            
            guias_enviadas = (
                session.query(Guia)
                .filter(
                    Guia.tp_status == 'T',  # Status 'T' = Transmitido (enviado com sucesso)
                    Guia.data_processamento.isnot(None),
                    Guia.data_processamento >= data_limite,
                    Guia.numero_guia.isnot(None)
                )
                .all()
            )

            if not guias_enviadas:
                self.logger.info("📭 Nenhuma guia enviada recentemente encontrada")
                return

            self.logger.info(f"📋 Processando {len(guias_enviadas)} guias enviadas...")

            # Agrupar guias em lotes
            lotes = self._agrupar_em_lotes(guias_enviadas, self.settings.MONITOR_PULL_MAX_PAGE_SIZE)

            for i, lote in enumerate(lotes, 1):
                self.logger.info(f"📦 Processando lote {i}/{len(lotes)} ({len(lote)} guias)...")
                
                # Buscar atualizações para este lote
                await self._buscar_atualizacoes_lote(lote)

                # Pequena pausa entre lotes para não sobrecarregar a API
                await asyncio.sleep(1)

            self.logger.info("✅ Processamento PULL concluído")

        except Exception as e:
            self.logger.error(f"❌ Erro ao processar atualizações PULL: {e}", exc_info=True)
        finally:
            if session:
                session.close()

    def _agrupar_em_lotes(self, guias: List[Guia], tamanho_lote: int) -> List[List[Guia]]:
        """
        Agrupa guias em lotes.
        
        Args:
            guias: Lista de guias
            tamanho_lote: Tamanho máximo do lote
            
        Returns:
            List[List[Guia]]: Lista de lotes
        """
        lotes = []
        for i in range(0, len(guias), tamanho_lote):
            lotes.append(guias[i:i + tamanho_lote])
        return lotes

    async def _buscar_atualizacoes_lote(self, guias: List[Guia]):
        """
        Busca atualizações para um lote de guias.
        
        Args:
            guias: Lista de guias do lote
        """
        try:
            # Montar lista de números de guias
            numeros_guias = [guia.numero_guia for guia in guias]

            # Chamar API PULL
            resultado = self.drg_service.consumir_exportacao_guias(
                numero_guia=numeros_guias
            )

            if not resultado.get("sucesso"):
                self.logger.error(f"❌ Erro ao buscar atualizações: {resultado.get('erro')}")
                return

            # Processar resposta
            resposta = resultado.get("resposta")
            if not resposta:
                self.logger.warning("⚠️ Resposta vazia da API PULL")
                return

            # Atualizar guias com dados retornados
            await self._processar_resposta_pull(resposta, guias)

        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar atualizações do lote: {e}", exc_info=True)

    async def _processar_resposta_pull(self, resposta: Dict[str, Any], guias: List[Guia]):
        """
        Processa a resposta da API PULL e atualiza as guias.
        
        Args:
            resposta: Resposta da API DRG (formato completo da guia)
            guias: Lista de guias esperadas
        """
        session = None
        try:
            session = get_session()
            
            # A estrutura da resposta pode variar
            # Assumindo que retorna uma lista de guias ou um objeto com 'guia'
            guias_resposta = []
            
            if isinstance(resposta, list):
                guias_resposta = resposta
            elif isinstance(resposta, dict):
                # Tentar diferentes formatos
                if "guia" in resposta:
                    guias_resposta = resposta["guia"] if isinstance(resposta["guia"], list) else [resposta["guia"]]
                elif "guias" in resposta:
                    guias_resposta = resposta["guias"] if isinstance(resposta["guias"], list) else [resposta["guias"]]
                elif "data" in resposta:
                    guias_resposta = resposta["data"] if isinstance(resposta["data"], list) else [resposta["data"]]
                elif "items" in resposta:  # Formato comum de paginação
                    guias_resposta = resposta["items"] if isinstance(resposta["items"], list) else [resposta["items"]]

            if not guias_resposta:
                self.logger.warning("⚠️ Nenhuma guia encontrada na resposta")
                return

            self.logger.info(f"📝 Processando {len(guias_resposta)} guias da resposta...")

            # Processar cada guia da resposta
            for guia_data in guias_resposta:
                if not isinstance(guia_data, dict):
                    continue

                numero_guia = guia_data.get("numeroGuia")
                if not numero_guia:
                    continue

                # Buscar guia local
                guia_local = session.query(Guia).filter(
                    Guia.numero_guia == numero_guia
                ).first()

                if not guia_local:
                    self.logger.warning(f"⚠️ Guia {numero_guia} não encontrada localmente")
                    continue

                # Atualizar guia local com dados da DRG
                self._atualizar_guia_com_dados_drg(guia_local, guia_data)

            # Commit das atualizações
            session.commit()
            self.logger.info("✅ Atualizações salvas com sucesso")

        except Exception as e:
            self.logger.error(f"❌ Erro ao processar resposta PULL: {e}", exc_info=True)
            if session:
                session.rollback()
        finally:
            if session:
                session.close()

    def _atualizar_guia_com_dados_drg(self, guia_local: Guia, guia_drg: Dict[str, Any]):
        """
        Atualiza uma guia local com dados retornados pela DRG.
        
        Args:
            guia_local: Instância de Guia do banco local
            guia_drg: Dicionário com dados da DRG
        """
        try:
            atualizacoes = []

            # Campos que podem ser atualizados do PULL
            # Mapeamento: campo_drg -> campo_local
            campos_para_atualizar = {
                "situacao_guia": guia_drg.get("situacaoGuia") or guia_drg.get("situacao"),
                "senha_autorizacao": guia_drg.get("senhaAutorizacao") or guia_drg.get("senha"),
                "qtde_diarias_autorizadas": guia_drg.get("qtdeDiariasAutorizadas"),
                "tipo_acomodacao_autorizada": guia_drg.get("tipoAcomodacaoAutorizada"),
                "cnes_autorizado": guia_drg.get("cnesAutorizado"),
                "data_autorizacao": self._parse_date(guia_drg.get("dataAutorizacao")),
                "observacao_guia": guia_drg.get("observacaoGuia"),
                "justificativa_operadora": guia_drg.get("justificativaOperadora"),
            }

            # Atualizar campos
            for campo_local, valor_drg in campos_para_atualizar.items():
                if valor_drg is not None:
                    valor_atual = getattr(guia_local, campo_local)
                    if valor_atual != valor_drg:
                        setattr(guia_local, campo_local, valor_drg)
                        atualizacoes.append(campo_local)

            # Se houve atualizações, registrar log
            if atualizacoes:
                self.logger.info(
                    f"📝 Guia {guia_local.numero_guia} atualizada: {', '.join(atualizacoes)}"
                )

        except Exception as e:
            self.logger.error(
                f"❌ Erro ao atualizar guia {guia_local.numero_guia}: {e}",
                exc_info=True
            )

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Converte string de data para datetime.
        
        Args:
            date_str: String de data em formato ISO ou similar
            
        Returns:
            Optional[datetime]: Data convertida ou None
        """
        if not date_str:
            return None

        try:
            # Tentar formatos comuns
            formatos = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y",
            ]

            for formato in formatos:
                try:
                    return datetime.strptime(date_str, formato)
                except ValueError:
                    continue

            self.logger.warning(f"⚠️ Formato de data não reconhecido: {date_str}")
            return None

        except Exception as e:
            self.logger.error(f"❌ Erro ao converter data {date_str}: {e}")
            return None

    async def obter_estatisticas_pull(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do monitoramento PULL.
        
        Returns:
            Dict com estatísticas
        """
        try:
            return {
                "monitoramento_ativo": self._running,
                "ultima_execucao": self._last_execution_time.isoformat() if self._last_execution_time else None,
                "configuracao": {
                    "habilitado": self.settings.MONITOR_PULL_ENABLED,
                    "intervalo_minutos": self.settings.MONITOR_PULL_INTERVAL_MINUTES,
                    "tamanho_max_lote": self.settings.MONITOR_PULL_MAX_PAGE_SIZE,
                },
            }
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter estatísticas PULL: {e}")
            return {"erro": str(e), "timestamp": datetime.utcnow().isoformat()}


# Instância global do serviço
monitor_pull_service = MonitorPullService()

