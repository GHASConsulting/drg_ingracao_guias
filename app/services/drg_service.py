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
        self.put_timeout_ms = settings.DRG_PUT_TIMEOUT_MS
        self.put_max_tentativas = settings.DRG_PUT_MAX_TENTATIVAS
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

    def enviar_lote(self, json_lote: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia lote de guias para a API DRG com gerenciamento automático de token.

        Implementa estratégia híbrida:
        1. Tenta com token válido (renovação preventiva)
        2. Se falhar por token expirado, renova e tenta novamente
        """
        try:
            # Obter token válido (renovação preventiva a cada 3:30h)
            token = self.token_manager.get_valid_token()

            # Primeira tentativa de envio
            result = self._enviar_lote_com_token(json_lote, token)

            # Se sucesso, retornar
            if result["sucesso"]:
                return result

            # Se falhou por token expirado, tentar novamente com token renovado
            if is_token_expired_error(result.get("erro", "")):
                token = self.token_manager.force_refresh()
                return self._enviar_lote_com_token(json_lote, token)

            # Se falhou por outro motivo, retornar erro
            return result

        except Exception as e:
            return {"sucesso": False, "erro": f"Erro ao enviar lote: {str(e)}"}

    def _enviar_lote_com_token(
        self, json_lote: Dict[str, Any], token: str
    ) -> Dict[str, Any]:
        """
        Envia lote de guias usando token específico.

        Args:
            json_lote: Dados do lote em JSON
            token: Token JWT para autenticação

        Returns:
            Dict: Resultado do envio
        """
        try:
            # Headers para envio (formato correto da API DRG)
            headers = {"Content-Type": "application/json", "Authorization": token}

            # Log da requisição de envio
            drg_logger.log_request("POST", self.drg_url, headers, json_data=json_lote)

            # Fazer requisição de envio
            response = requests.post(
                self.drg_url, json=json_lote, headers=headers, timeout=60
            )

            # Log da resposta
            drg_logger.log_response(
                response.status_code, dict(response.headers), response.text
            )

            # Verificar status da resposta
            if response.status_code == 200:
                # Sucesso - processar resposta
                try:
                    response_json = response.json()
                    drg_logger.log_guide_processing(
                        f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                        f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                        json_lote,
                        True,
                        response_json,
                    )
                    return {"sucesso": True, "resposta": response_json}
                except json.JSONDecodeError:
                    # Resposta não é JSON válido
                    drg_logger.log_guide_processing(
                        f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                        f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                        json_lote,
                        False,
                        None,
                        f"Resposta não é JSON válido: {response.text[:200]}",
                    )
                    return {
                        "sucesso": False,
                        "erro": f"Resposta inválida: {response.text[:200]}",
                    }
            else:
                # Erro HTTP
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                drg_logger.log_guide_processing(
                    f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                    f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                    json_lote,
                    False,
                    None,
                    error_msg,
                )
                return {"sucesso": False, "erro": error_msg}

        except requests.exceptions.Timeout:
            error_msg = "Timeout na requisição (60s)"
            drg_logger.log_guide_processing(
                f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                json_lote,
                False,
                None,
                error_msg,
            )
            return {"sucesso": False, "erro": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição: {str(e)}"
            drg_logger.log_guide_processing(
                f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                json_lote,
                False,
                None,
                error_msg,
            )
            return {"sucesso": False, "erro": error_msg}
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            drg_logger.log_guide_processing(
                f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                json_lote,
                False,
                None,
                error_msg,
            )
            return {"sucesso": False, "erro": error_msg}

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

    def enviar_put_guia_aprovada(self, guia_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia PUT para DRG com guia aprovada e senha de autorização.

        Args:
            guia_data: Dados da guia aprovada com senha

        Returns:
            Dict: Resultado do envio
        """
        try:
            # Obter token válido
            token_result = self.token_manager.get_valid_token()
            if not token_result["sucesso"]:
                return token_result

            token = token_result["token"]

            # Preparar JSON para PUT
            json_put = self._montar_json_put_guia_aprovada(guia_data)

            # Enviar PUT com retry
            return self._enviar_put_com_retry(json_put, token)

        except Exception as e:
            drg_logger.error(f"Erro ao enviar PUT para DRG: {e}")
            return {"sucesso": False, "erro": f"Erro ao enviar PUT: {str(e)}"}

    def _montar_json_put_guia_aprovada(self, guia_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monta o JSON para PUT de guia aprovada com senha.
        """
        settings = get_settings()
        
        return {
            "loteGuias": {
                "guia": [{
                    "numeroGuia": guia_data.get("numero_guia"),
                    "situacaoGuia": guia_data.get("situacao_guia", "A"),
                    "senhaAutorizacao": guia_data.get("senha_autorizacao"),
                    "tipoOperacao": "PUT_APROVADA",
                    "dataAprovacao": guia_data.get("data_aprovacao"),
                    "observacaoGuia": guia_data.get("observacao_guia"),
                    "justificativaOperadora": guia_data.get("justificativa_operadora"),
                    "numeroAutorizacao": guia_data.get("numero_autorizacao"),
                    "qtdeDiariasAutorizadas": guia_data.get("qtde_diarias_autorizadas"),
                    "tipoAcomodacaoAutorizada": guia_data.get("tipo_acomodacao_autorizada"),
                    "cnesAutorizado": guia_data.get("cnes_autorizado"),
                    "dataAutorizacao": guia_data.get("data_autorizacao"),
                    # Campos do hospital
                    "codigoContratado": settings.HOSPITAL_CODIGO_CONTRATADO,
                    "nomeHospital": settings.HOSPITAL_NOME,
                    "cnesHospital": settings.HOSPITAL_CNES,
                    "porteHospital": settings.HOSPITAL_PORTE,
                    "complexidadeHospital": settings.HOSPITAL_COMPLEXIDADE,
                    "esferaAdministrativa": settings.HOSPITAL_ESFERA_ADMINISTRATIVA,
                    "enderecoHospital": settings.HOSPITAL_ENDERECO,
                }]
            }
        }

    def _enviar_put_com_retry(self, json_put: Dict[str, Any], token: str) -> Dict[str, Any]:
        """
        Envia PUT com retry automático.
        """
        for tentativa in range(1, self.put_max_tentativas + 1):
            try:
                drg_logger.info(f"📡 Enviando guia aprovada para DRG (tentativa {tentativa}/{self.put_max_tentativas})")
                
                # Log do JSON sendo enviado
                drg_logger.log_request("POST", self.drg_url, json_put)

                # Fazer requisição POST para a mesma rota principal
                response = requests.post(
                    self.drg_url,
                    json=json_put,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "X-API-Key": self.api_key,
                    },
                    timeout=self.put_timeout_ms / 1000,  # Converter para segundos
                )

                # Log da resposta
                drg_logger.log_response(
                    response.status_code, dict(response.headers), response.text
                )

                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        drg_logger.info(f"✅ Guia aprovada enviada com sucesso para DRG")
                        return {
                            "sucesso": True,
                            "dados": response_data,
                            "tentativa": tentativa,
                        }
                    except ValueError:
                        drg_logger.error(
                            f"Resposta não é JSON válido: {response.text[:200]}",
                        )
                        return {
                            "sucesso": False,
                            "erro": f"Resposta inválida: {response.text[:200]}",
                        }
                elif response.status_code == 401:
                    # Token expirado, tentar renovar
                    drg_logger.warning("Token expirado, tentando renovar...")
                    token_result = self.token_manager.force_refresh()
                    if token_result["sucesso"]:
                        token = token_result["token"]
                        continue
                    else:
                        return {"sucesso": False, "erro": "Falha ao renovar token"}
                else:
                    # Erro HTTP
                    drg_logger.error(f"Erro HTTP {response.status_code}: {response.text}")
                    if tentativa < self.put_max_tentativas:
                        drg_logger.info(f"Tentando novamente em 2 segundos...")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        return {
                            "sucesso": False,
                            "erro": f"Erro HTTP {response.status_code}: {response.text[:200]}",
                        }

            except requests.exceptions.Timeout:
                drg_logger.error(f"Timeout na tentativa {tentativa}")
                if tentativa < self.put_max_tentativas:
                    continue
                else:
                    return {"sucesso": False, "erro": "Timeout após todas as tentativas"}

            except requests.exceptions.RequestException as e:
                drg_logger.error(f"Erro de requisição na tentativa {tentativa}: {e}")
                if tentativa < self.put_max_tentativas:
                    continue
                else:
                    return {"sucesso": False, "erro": f"Erro de requisição: {str(e)}"}

        return {"sucesso": False, "erro": "Falha após todas as tentativas"}
