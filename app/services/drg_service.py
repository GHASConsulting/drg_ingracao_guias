import requests  # pyright: ignore[reportMissingModuleSource]
import json
from typing import Dict, Any
from app.config.config import get_settings
from app.services.token_manager import (
    TokenManager,
    TokenExpiredError,
    is_token_expired_error,
)
from app.utils.logger import drg_logger


class DRGService:
    """Serviço para comunicação com a API DRG."""

    def __init__(self):
        settings = get_settings()
        self.auth_url = settings.AUTH_API_URL
        self.drg_url = settings.DRG_API_URL
        self.username = settings.DRG_USERNAME
        self.password = settings.DRG_PASSWORD
        self.api_key = settings.DRG_API_KEY
        self._token = None

        # Inicializar TokenManager
        self.token_manager = TokenManager(self)

    def autenticar(self) -> Dict[str, Any]:
        """Autentica na API DRG e obtém token."""
        try:
            # Dados de autenticação no formato correto da API DRG
            auth_data = {
                "userName": self.username,
                "password": self.password,
                "origin": "API_DRG",
            }

            # Headers no formato correto da API DRG
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            # Log da requisição de autenticação
            drg_logger.log_request("POST", self.auth_url, headers, json_data=auth_data)

            # Fazer requisição de autenticação
            response = requests.post(
                self.auth_url, json=auth_data, headers=headers, timeout=30
            )

            # Log da resposta
            drg_logger.log_response(
                response.status_code, dict(response.headers), response.text
            )

            if response.status_code == 200:
                # A API retorna o token diretamente como texto, não como JSON
                token = response.text.strip()
                if token:
                    self._token = token

                    # Log de sucesso na autenticação
                    drg_logger.log_authentication(success=True, token=token)

                    return {"sucesso": True, "token": self._token}
                else:
                    drg_logger.log_authentication(
                        success=False, error="Token vazio na resposta"
                    )
                    return {"sucesso": False, "erro": "Token vazio na resposta"}
            else:
                error_msg = (
                    f"Erro na autenticação: {response.status_code} - {response.text}"
                )
                drg_logger.log_authentication(success=False, error=error_msg)
                return {"sucesso": False, "erro": error_msg}

        except Exception as e:
            drg_logger.log_error(e, "Autenticação DRG")
            return {"sucesso": False, "erro": f"Erro ao autenticar: {str(e)}"}

    def enviar_guia(self, json_drg: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia guia para a API DRG com gerenciamento automático de token.

        Implementa estratégia híbrida:
        1. Tenta com token válido (renovação preventiva)
        2. Se falhar por token expirado, renova e tenta novamente
        """
        try:
            # Obter token válido (renovação preventiva a cada 3:30h)
            token = self.token_manager.get_valid_token()

            # Primeira tentativa de envio
            result = self._enviar_com_token(json_drg, token)

            # Se sucesso, retornar
            if result["sucesso"]:
                return result

            # Se falhou por token expirado, tentar novamente com token renovado
            if is_token_expired_error(result.get("erro", "")):
                token = self.token_manager.force_refresh()
                return self._enviar_com_token(json_drg, token)

            # Se falhou por outro motivo, retornar erro
            return result

        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao enviar guia: {str(e)}"}

    def _enviar_com_token(self, json_drg: Dict[str, Any], token: str) -> Dict[str, Any]:
        """
        Envia guia usando token específico.

        Args:
            json_drg: Dados da guia em JSON
            token: Token JWT para autenticação

        Returns:
            Dict: Resultado do envio
        """
        try:
            # Headers para envio (formato correto da API DRG)
            headers = {"Content-Type": "application/json", "Authorization": token}

            # Log da requisição de envio
            drg_logger.log_request("POST", self.drg_url, headers, json_data=json_drg)

            # Fazer requisição de envio
            response = requests.post(
                self.drg_url, json=json_drg, headers=headers, timeout=60
            )

            # Log da resposta
            response_json = None
            try:
                response_json = response.json()
            except:
                pass

            drg_logger.log_response(
                response.status_code,
                dict(response.headers),
                response.text,
                response_json,
            )

            if response.status_code == 200:
                return {"sucesso": True, "resposta": response_json}
            else:
                error_msg = f"Erro no envio: {response.status_code} - {response.text}"
                return {"sucesso": False, "erro": error_msg}

        except Exception as e:
            drg_logger.log_error(e, "Envio de guia DRG")
            return {"sucesso": False, "erro": f"Erro ao enviar guia: {str(e)}"}

    def verificar_status(self) -> Dict[str, Any]:
        """Verifica se a API DRG está disponível."""
        try:
            # Tentar autenticar
            auth_result = self.autenticar()
            return auth_result

        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao verificar status: {str(e)}"}

    def get_token_status(self) -> Dict[str, Any]:
        """
        Retorna status do token atual.

        Returns:
            Dict: Status do token
        """
        try:
            token_info = self.token_manager.get_token_info()
            return {"sucesso": True, "token_info": token_info}
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro ao obter status do token: {str(e)}",
            }

    def renovar_token(self) -> Dict[str, Any]:
        """
        Força a renovação do token.

        Returns:
            Dict: Resultado da renovação
        """
        try:
            token = self.token_manager.force_refresh()
            return {
                "sucesso": True,
                "token": token,
                "mensagem": "Token renovado com sucesso",
            }
        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao renovar token: {str(e)}"}
