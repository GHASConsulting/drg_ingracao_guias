import requests  # pyright: ignore[reportMissingModuleSource]
import json
from typing import Dict, Any, Optional
from app.config.config import get_settings
from app.services.token_manager import (
    TokenManager,
    TokenExpiredError,
    is_token_expired_error,
)
from app.utils.logger import drg_logger


def is_retentable_error(error_msg: str, status_code: int = None) -> bool:
    """
    Verifica se um erro é retentável (deve manter status 'A' para reenvio).
    
    Erros retentáveis (infraestrutura temporária):
    - Erro 500 (erro interno do servidor)
    - Erro 502, 503, 504 (bad gateway, service unavailable, gateway timeout)
    - Timeout
    - Erros de conexão (DRG fora do ar)
    - Erros de rede
    
    Erros não-retentáveis (validação/dados):
    - Erro 400 (bad request)
    - Erro 401, 403 (autenticação/autorização - podem ser temporários, mas tratamos como não-retentáveis)
    - Erros de validação retornados pela API
    
    Args:
        error_msg: Mensagem de erro
        status_code: Código HTTP de status (se disponível)
    
    Returns:
        bool: True se o erro é retentável, False caso contrário
    """
    error_lower = error_msg.lower() if error_msg else ""
    
    # Erros de status HTTP retentáveis
    if status_code:
        if status_code >= 500:  # 500, 502, 503, 504
            return True
        if status_code in [400, 401, 403, 404]:  # Não retentáveis
            return False
    
    # Palavras-chave que indicam erro retentável
    retentable_keywords = [
        "timeout",
        "connection",
        "conexão",
        "network",
        "rede",
        "unavailable",
        "indisponível",
        "gateway",
        "server error",
        "erro interno",
        "internal server",
        "temporarily",
        "temporariamente",
        "service unavailable",
        "serviço indisponível",
    ]
    
    # Palavras-chave que indicam erro não-retentável (validação)
    non_retentable_keywords = [
        "invalid",
        "inválido",
        "campo obrigatório",
        "obrigatório",
        "não foi informado",
        "não encontrado",
        "não cadastrado",
        "cadastrado no drg",
        "autorização não",
        "validação",
        "validation",
        "bad request",
        "requisição inválida",
        "unauthorized",
        "forbidden",
        "não autorizado",
    ]
    
    # Verificar primeiro por erros não-retentáveis (validação)
    for keyword in non_retentable_keywords:
        if keyword in error_lower:
            return False
    
    # Verificar por erros retentáveis (infraestrutura)
    for keyword in retentable_keywords:
        if keyword in error_lower:
            return True
    
    # Se tem código de status 500+, é retentável
    if status_code and status_code >= 500:
        return True
    
    # Padrão: se não identificar, assume não-retentável para segurança
    return False


class DRGService:
    """Serviço para comunicação com a API DRG."""

    def __init__(self):
        settings = get_settings()
        self.auth_url = settings.AUTH_API_URL
        self.drg_url = settings.DRG_API_URL
        self.drg_pull_url = settings.DRG_API_PULL_URL
        self.username = settings.DRG_USERNAME
        self.password = settings.DRG_PASSWORD
        self.api_key = settings.DRG_API_KEY
        self.pull_username = settings.DRG_PULL_USERNAME
        self.pull_password = settings.DRG_PULL_PASSWORD
        # Se DRG_PULL_API_KEY não estiver configurada ou for placeholder, usa a API Key padrão
        pull_key = settings.DRG_PULL_API_KEY
        if not pull_key or pull_key == "seu_codigo_unico_drg_aqui":
            self.pull_api_key = settings.DRG_API_KEY
        else:
            self.pull_api_key = pull_key
        self._token = None
        self._pull_token = None  # Token separado para PULL

        # Inicializar TokenManager
        self.token_manager = TokenManager(self)

    def autenticar(self, use_pull_credentials: bool = False) -> Dict[str, Any]:
        """Autentica na API DRG e obtém token."""
        try:
            # Escolher credenciais baseado no contexto
            username = self.pull_username if use_pull_credentials else self.username
            password = self.pull_password if use_pull_credentials else self.password
            api_key = self.pull_api_key if use_pull_credentials else self.api_key
            
            # Dados de autenticação no formato correto da API DRG
            auth_data = {
                "userName": username,
                "password": password,
                "origin": "API_DRG",
            }

            # Headers no formato correto da API DRG
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
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
                    # Armazenar token no local apropriado
                    if use_pull_credentials:
                        self._pull_token = token
                        token_to_return = self._pull_token
                    else:
                        self._token = token
                        token_to_return = self._token

                    # Log de sucesso na autenticação
                    drg_logger.log_authentication(success=True, token=token)

                    return {"sucesso": True, "token": token_to_return}
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

            # Fazer requisição de envio (usar timeout do settings)
            settings = get_settings()
            timeout = settings.HTTP_TIMEOUT
            response = requests.post(
                self.drg_url, json=json_lote, headers=headers, timeout=timeout
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

                    # Verificar se há erros na resposta mesmo com status 200
                    erro_msg = None
                    if isinstance(response_json, dict):
                        # Verificar diferentes formatos de erro - CAPTURAR QUALQUER ERRO
                        if "erro" in response_json:
                            erro_msg = response_json["erro"]
                        elif "error" in response_json:
                            erro_msg = response_json["error"]
                        elif "mensagem" in response_json and (
                            "erro" in str(response_json["mensagem"]).lower()
                            or "error" in str(response_json["mensagem"]).lower()
                        ):
                            erro_msg = response_json["mensagem"]
                        elif "message" in response_json and (
                            "erro" in str(response_json["message"]).lower()
                            or "error" in str(response_json["message"]).lower()
                        ):
                            erro_msg = response_json["message"]
                        elif response_json.get("status") in ["erro", "error"]:
                            erro_msg = (
                                response_json.get("message")
                                or response_json.get("mensagem")
                                or str(response_json)
                            )
                        elif "guias" in response_json:
                            erros_guias = []
                            for guia in response_json["guias"]:
                                if isinstance(guia, dict):
                                    if "erro" in guia and guia["erro"] is not None:
                                        erros_guias.append(str(guia["erro"]))
                                    elif "error" in guia and guia["error"] is not None:
                                        erros_guias.append(str(guia["error"]))
                                    elif guia.get("status") in ["erro", "error"]:
                                        erro_guia = (
                                            guia.get("mensagem")
                                            or guia.get("message")
                                            or "Erro na guia"
                                        )
                                        if erro_guia:
                                            erros_guias.append(str(erro_guia))
                            if erros_guias:
                                erro_msg = "; ".join(erros_guias)
                        # Capturar qualquer resposta que pareça ser de erro
                        if not erro_msg and any(
                            key in response_json
                            for key in [
                                "falha",
                                "failure",
                                "problema",
                                "problem",
                                "invalid",
                                "invalido",
                            ]
                        ):
                            erro_msg = str(response_json)
                    elif isinstance(response_json, str):
                        # Se a resposta for uma string, pode ser uma mensagem de erro
                        if (
                            "erro" in response_json.lower()
                            or "error" in response_json.lower()
                        ):
                            erro_msg = response_json

                    # Se encontrou erro, tratar como erro (não-retentável - validação)
                    if erro_msg:
                        drg_logger.log_guide_processing(
                            f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                            f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                            json_lote,
                            False,
                            None,
                            erro_msg,
                        )
                        return {
                            "sucesso": False,
                            "erro": erro_msg,
                            "resposta": response_json,
                            "retentavel": False,  # Erros de validação não são retentáveis
                        }

                    # Sucesso real
                    drg_logger.log_guide_processing(
                        f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                        f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                        json_lote,
                        True,
                        response_json,
                    )
                    return {"sucesso": True, "resposta": response_json}
                except json.JSONDecodeError:
                    # Resposta não é JSON válido - pode ser erro de servidor
                    error_msg = f"Resposta não é JSON válido: {response.text[:200]}"
                    drg_logger.log_guide_processing(
                        f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                        f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                        json_lote,
                        False,
                        None,
                        error_msg,
                    )
                    # Se status é 500+, é retentável
                    retentavel = response.status_code >= 500 if response.status_code else False
                    return {
                        "sucesso": False,
                        "erro": error_msg,
                        "retentavel": retentavel,
                    }
            else:
                # Erro HTTP - verificar se é retentável
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                retentavel = is_retentable_error(error_msg, response.status_code)
                drg_logger.log_guide_processing(
                    f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                    f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                    json_lote,
                    False,
                    None,
                    error_msg,
                )
                return {
                    "sucesso": False,
                    "erro": error_msg,
                    "retentavel": retentavel,
                    "status_code": response.status_code,
                }

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
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": True,  # Timeout é retentável
            }
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erro de conexão: {str(e)}"
            drg_logger.log_guide_processing(
                f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                json_lote,
                False,
                None,
                error_msg,
            )
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": True,  # Erro de conexão é retentável
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição: {str(e)}"
            retentavel = is_retentable_error(error_msg)
            drg_logger.log_guide_processing(
                f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))}",
                f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                json_lote,
                False,
                None,
                error_msg,
            )
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": retentavel,
            }
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            retentavel = is_retentable_error(error_msg)
            drg_logger.log_guide_processing(
                f"lote_{len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                f"Lote de {len(json_lote.get('loteGuias', {}).get('guia', []))} guias",
                json_lote,
                False,
                None,
                error_msg,
            )
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": retentavel,
            }

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

            # Fazer requisição de envio (usar timeout do settings)
            settings = get_settings()
            timeout = settings.HTTP_TIMEOUT
            response = requests.post(
                self.drg_url, json=json_drg, headers=headers, timeout=timeout
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
                # Verificar se a resposta contém erros mesmo com status 200
                if response_json:
                    # Verificar se há campo de erro na resposta
                    erro_msg = None

                    # Verificar diferentes formatos de erro que o DRG pode retornar
                    if isinstance(response_json, dict):
                        # Formato 1: {"erro": "mensagem"}
                        if "erro" in response_json:
                            erro_msg = response_json["erro"]
                        # Formato 2: {"error": "mensagem"}
                        elif "error" in response_json:
                            erro_msg = response_json["error"]
                        # Formato 3: {"mensagem": "erro"}
                        elif "mensagem" in response_json and (
                            "erro" in str(response_json["mensagem"]).lower()
                            or "error" in str(response_json["mensagem"]).lower()
                        ):
                            erro_msg = response_json["mensagem"]
                        # Formato 4: {"message": "erro"}
                        elif "message" in response_json and (
                            "erro" in str(response_json["message"]).lower()
                            or "error" in str(response_json["message"]).lower()
                        ):
                            erro_msg = response_json["message"]
                        # Formato 5: {"status": "erro", "message": "..."}
                        elif response_json.get("status") in ["erro", "error"]:
                            erro_msg = (
                                response_json.get("message")
                                or response_json.get("mensagem")
                                or str(response_json)
                            )
                        # Formato 6: {"guias": [{"erro": "..."}]} - erros dentro das guias
                        elif "guias" in response_json:
                            erros_guias = []
                            for guia in response_json["guias"]:
                                if isinstance(guia, dict):
                                    if "erro" in guia and guia["erro"] is not None:
                                        erros_guias.append(str(guia["erro"]))
                                    elif "error" in guia and guia["error"] is not None:
                                        erros_guias.append(str(guia["error"]))
                                    elif guia.get("status") in ["erro", "error"]:
                                        erro_guia = (
                                            guia.get("mensagem")
                                            or guia.get("message")
                                            or "Erro na guia"
                                        )
                                        if erro_guia:
                                            erros_guias.append(str(erro_guia))
                            if erros_guias:
                                erro_msg = "; ".join(erros_guias)
                        # Se não encontrou erro mas a resposta parece ser de erro, capturar tudo
                        if not erro_msg and any(
                            key in response_json
                            for key in ["falha", "failure", "problema", "problem"]
                        ):
                            erro_msg = str(response_json)
                    elif isinstance(response_json, str):
                        # Se a resposta for uma string, pode ser uma mensagem de erro
                        if (
                            "erro" in response_json.lower()
                            or "error" in response_json.lower()
                        ):
                            erro_msg = response_json

                    # Se encontrou erro, retornar como erro (não-retentável - validação)
                    if erro_msg:
                        return {
                            "sucesso": False,
                            "erro": erro_msg,
                            "resposta": response_json,
                            "retentavel": False,  # Erros de validação não são retentáveis
                        }

                # Se chegou aqui, é sucesso real
                return {"sucesso": True, "resposta": response_json}
            else:
                # Erro HTTP - verificar se é retentável
                error_msg = f"Erro no envio: {response.status_code} - {response.text}"
                retentavel = is_retentable_error(error_msg, response.status_code)
                return {
                    "sucesso": False,
                    "erro": error_msg,
                    "retentavel": retentavel,
                    "status_code": response.status_code,
                }

        except requests.exceptions.Timeout as e:
            error_msg = "Timeout na requisição (60s)"
            drg_logger.log_error(e, "Envio de guia DRG - Timeout")
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": True,  # Timeout é retentável
            }
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erro de conexão: {str(e)}"
            drg_logger.log_error(e, "Envio de guia DRG - Erro de conexão")
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": True,  # Erro de conexão é retentável
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição: {str(e)}"
            drg_logger.log_error(e, "Envio de guia DRG")
            # Verificar se é retentável baseado na mensagem
            retentavel = is_retentable_error(error_msg)
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": retentavel,
            }
        except Exception as e:
            error_msg = f"Erro ao enviar guia: {str(e)}"
            drg_logger.log_error(e, "Envio de guia DRG")
            # Verificar se é retentável baseado na mensagem
            retentavel = is_retentable_error(error_msg)
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": retentavel,
            }

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

    def consumir_exportacao_guias(
        self,
        numero_guia: Optional[str] = None,
        data_ultima_alteracao: Optional[str] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        """
        Consome a API de exportação de guias (PULL da DRG).

        Args:
            numero_guia: Lista de números das guias (será convertido para array)
            data_ultima_alteracao: Data da última alteração no formato aaaa-mm-dd
            page: Número da página (padrão: 1, máximo 100 registros por página)

        Returns:
            Dict: Resultado da consulta com lista de guias

        Documentação:
            - URL: https://apidrg-exporta-assistencial.drgbrasil.com.br/guiainternacao/search
            - Método: POST
            - Headers: Authorization (JWT), x-api-key
        """
        try:
            # Validar que ao menos um parâmetro foi informado
            if not numero_guia and not data_ultima_alteracao:
                return {
                    "sucesso": False,
                    "erro": "É obrigatório informar ao menos um número de guia ou data de alteração",
                }

            # Obter token para PULL (autenticar com credenciais específicas do PULL)
            auth_result = self.autenticar(use_pull_credentials=True)
            if not auth_result.get("sucesso"):
                return {
                    "sucesso": False,
                    "erro": f"Erro na autenticação PULL: {auth_result.get('erro')}",
                }
            token = auth_result["token"]

            # Montar dados da requisição
            payload = {}
            if numero_guia:
                # Se numero_guia for string, converter para array
                if isinstance(numero_guia, str):
                    payload["numeroGuia"] = [numero_guia]
                else:
                    payload["numeroGuia"] = numero_guia

            if data_ultima_alteracao:
                payload["dataUltimaAlteracao"] = data_ultima_alteracao

            payload["page"] = page

            # Headers da requisição
            headers = {
                "Content-Type": "application/json",
                "Authorization": token,
                "x-api-key": self.pull_api_key,
            }

            # Log da requisição
            drg_logger.log_request("POST", self.drg_pull_url, headers, json_data=payload)

            # Fazer requisição (usar timeout do settings)
            settings = get_settings()
            timeout = settings.HTTP_TIMEOUT
            response = requests.post(
                self.drg_pull_url, json=payload, headers=headers, timeout=timeout
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

            # Processar resposta
            if response.status_code == 200:
                # Sucesso - retornar dados
                return {"sucesso": True, "resposta": response_json}
            else:
                # Erro HTTP
                error_msg = f"Erro na exportação: {response.status_code} - {response.text}"
                retentavel = is_retentable_error(error_msg, response.status_code)
                return {
                    "sucesso": False,
                    "erro": error_msg,
                    "retentavel": retentavel,
                    "status_code": response.status_code,
                }

        except requests.exceptions.Timeout as e:
            error_msg = "Timeout na requisição de exportação (60s)"
            drg_logger.log_error(e, "Exportação de guias DRG - Timeout")
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": True,
            }
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Erro de conexão: {str(e)}"
            drg_logger.log_error(e, "Exportação de guias DRG - Erro de conexão")
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": True,
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro na requisição de exportação: {str(e)}"
            drg_logger.log_error(e, "Exportação de guias DRG")
            retentavel = is_retentable_error(error_msg)
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": retentavel,
            }
        except Exception as e:
            error_msg = f"Erro ao consumir exportação: {str(e)}"
            drg_logger.log_error(e, "Exportação de guias DRG")
            retentavel = is_retentable_error(error_msg)
            return {
                "sucesso": False,
                "erro": error_msg,
                "retentavel": retentavel,
            }
