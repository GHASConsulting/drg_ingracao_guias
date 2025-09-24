"""
Gerenciador de tokens JWT para API DRG
"""

import time
import threading
from typing import Optional, Dict, Any
from app.config.config import get_settings


class TokenManager:
    """
    Gerenciador de tokens JWT com renovação automática e fallback.

    Estratégia híbrida:
    1. Renovação preventiva a cada 3:30h
    2. Fallback automático se token expirar durante uso
    3. Cache seguro em memória
    4. Lock para evitar múltiplas renovações simultâneas
    """

    def __init__(self, drg_service):
        """
        Inicializa o gerenciador de tokens.

        Args:
            drg_service: Instância do DRGService para fazer autenticação
        """
        self.drg_service = drg_service
        self._token: Optional[str] = None
        self._last_auth: Optional[float] = None
        self._lock = threading.Lock()
        self._refresh_interval = 3.5 * 3600  # 3:30h em segundos

    def get_valid_token(self) -> str:
        """
        Retorna um token válido, renovando se necessário.

        Returns:
            str: Token JWT válido

        Raises:
            Exception: Se não conseguir obter token válido
        """
        with self._lock:
            # Se não tem token ou precisa renovar preventivamente
            if self._should_refresh():
                return self._refresh_token()

            return self._token

    def force_refresh(self) -> str:
        """
        Força a renovação do token.

        Returns:
            str: Novo token JWT

        Raises:
            Exception: Se não conseguir renovar token
        """
        with self._lock:
            return self._refresh_token()

    def _should_refresh(self) -> bool:
        """
        Verifica se o token deve ser renovado.

        Returns:
            bool: True se deve renovar
        """
        # Se não tem token
        if not self._token or not self._last_auth:
            return True

        # Se passou do tempo de renovação preventiva
        time_since_auth = time.time() - self._last_auth
        return time_since_auth >= self._refresh_interval

    def _refresh_token(self) -> str:
        """
        Renova o token fazendo nova autenticação.

        Returns:
            str: Novo token JWT

        Raises:
            Exception: Se falhar na autenticação
        """
        try:
            # Fazer autenticação
            auth_result = self.drg_service.autenticar()

            if not auth_result["sucesso"]:
                raise Exception(
                    f"Falha na autenticação: {auth_result.get('erro', 'Erro desconhecido')}"
                )

            # Atualizar token e timestamp
            self._token = auth_result["token"]
            self._last_auth = time.time()

            return self._token

        except Exception as e:
            # Limpar token inválido em caso de erro
            self._token = None
            self._last_auth = None
            raise Exception(f"Erro ao renovar token: {str(e)}")

    def get_token_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o token atual.

        Returns:
            Dict: Informações do token
        """
        with self._lock:
            if not self._token or not self._last_auth:
                return {
                    "has_token": False,
                    "time_since_auth": None,
                    "should_refresh": True,
                }

            time_since_auth = time.time() - self._last_auth
            return {
                "has_token": True,
                "time_since_auth": time_since_auth,
                "should_refresh": time_since_auth >= self._refresh_interval,
                "refresh_interval": self._refresh_interval,
            }

    def clear_token(self):
        """
        Limpa o token atual (útil para logout ou erro).
        """
        with self._lock:
            self._token = None
            self._last_auth = None


class TokenExpiredError(Exception):
    """Exceção para quando o token JWT expira."""

    pass


def is_token_expired_error(response_text: str) -> bool:
    """
    Verifica se a resposta indica token expirado.

    Args:
        response_text: Texto da resposta da API

    Returns:
        bool: True se indica token expirado
    """
    expired_indicators = [
        "token expired",
        "jwt expired",
        "unauthorized",
        "invalid token",
        "token inválido",
        "sessão expirada",
    ]

    response_lower = response_text.lower()
    return any(indicator in response_lower for indicator in expired_indicators)
