#!/usr/bin/env python3
"""
Sistema de logging para monitoramento da integração DRG
"""

import logging
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
from app.config.config import get_settings


class DRGLogger:
    """Logger especializado para integração DRG"""

    def __init__(self):
        settings = get_settings()
        self.log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

        # Configurar logger
        self.logger = logging.getLogger("drg_integration")
        self.logger.setLevel(self.log_level)

        # Remover handlers existentes para evitar duplicação
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Criar diretório de logs se não existir
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Configurar formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Handler para arquivo
        file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Handler para console (apenas em desenvolvimento)
        if settings.DEVELOPMENT:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ):
        """Log de requisição HTTP"""
        self.logger.info("=" * 80)
        self.logger.info(f"🚀 REQUISIÇÃO DRG - {method} {url}")
        self.logger.info("=" * 80)

        # Log headers (mascarando dados sensíveis)
        safe_headers = self._mask_sensitive_headers(headers)
        self.logger.info(
            f"📋 Headers: {json.dumps(safe_headers, indent=2, ensure_ascii=False)}"
        )

        # Log dados
        if data:
            safe_data = self._mask_sensitive_data(data)
            self.logger.info(
                f"📦 Data: {json.dumps(safe_data, indent=2, ensure_ascii=False)}"
            )

        if json_data:
            safe_json = self._mask_sensitive_data(json_data)
            self.logger.info(
                f"📦 JSON: {json.dumps(safe_json, indent=2, ensure_ascii=False)}"
            )

    def log_response(
        self,
        status_code: int,
        headers: Dict[str, str],
        response_text: str,
        response_json: Optional[Dict[str, Any]] = None,
    ):
        """Log de resposta HTTP"""
        self.logger.info("-" * 80)
        self.logger.info(f"📥 RESPOSTA DRG - Status: {status_code}")
        self.logger.info("-" * 80)

        # Log headers da resposta
        self.logger.info(
            f"📋 Response Headers: {json.dumps(dict(headers), indent=2, ensure_ascii=False)}"
        )

        # Log corpo da resposta
        if response_json:
            self.logger.info(
                f"📦 Response JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}"
            )
        else:
            # Limitar tamanho do texto se for muito grande
            text_preview = (
                response_text[:1000] + "..."
                if len(response_text) > 1000
                else response_text
            )
            self.logger.info(f"📦 Response Text: {text_preview}")

    def log_error(self, error: Exception, context: str = ""):
        """Log de erro"""
        self.logger.error("❌" + "=" * 78)
        self.logger.error(f"❌ ERRO DRG - {context}")
        self.logger.error("❌" + "=" * 78)
        self.logger.error(f"❌ Tipo: {type(error).__name__}")
        self.logger.error(f"❌ Mensagem: {str(error)}")
        self.logger.error("❌" + "-" * 78)

    def log_authentication(
        self, success: bool, token: Optional[str] = None, error: Optional[str] = None
    ):
        """Log específico para autenticação"""
        self.logger.info("🔐" + "=" * 78)
        if success:
            masked_token = self._mask_token(token) if token else "None"
            self.logger.info(f"🔐 AUTENTICAÇÃO DRG - SUCESSO")
            self.logger.info(f"🔐 Token: {masked_token}")
        else:
            self.logger.error(f"🔐 AUTENTICAÇÃO DRG - FALHA")
            self.logger.error(f"🔐 Erro: {error}")
        self.logger.info("🔐" + "=" * 78)

    def log_guide_processing(
        self,
        guia_id: int,
        numero_guia: str,
        json_enviado: Dict[str, Any],
        sucesso: bool,
        resposta: Optional[Dict[str, Any]] = None,
        erro: Optional[str] = None,
    ):
        """Log específico para processamento de guia"""
        self.logger.info("📋" + "=" * 78)
        self.logger.info(
            f"📋 PROCESSAMENTO GUIA - ID: {guia_id} | Número: {numero_guia}"
        )
        self.logger.info("📋" + "=" * 78)

        # Log JSON enviado (com dados mascarados)
        safe_json = self._mask_sensitive_data(json_enviado)
        self.logger.info(
            f"📤 JSON Enviado: {json.dumps(safe_json, indent=2, ensure_ascii=False)}"
        )

        if sucesso:
            self.logger.info("✅ PROCESSAMENTO SUCESSO")
            if resposta:
                self.logger.info(
                    f"📥 Resposta: {json.dumps(resposta, indent=2, ensure_ascii=False)}"
                )
        else:
            self.logger.error("❌ PROCESSAMENTO FALHA")
            if erro:
                self.logger.error(f"❌ Erro: {erro}")

        self.logger.info("📋" + "=" * 78)

    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Mascarar headers sensíveis"""
        sensitive_keys = ["authorization", "x-api-key", "api-key"]
        safe_headers = {}

        for key, value in headers.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                safe_headers[key] = f"***{value[-4:]}" if len(value) > 4 else "***"
            else:
                safe_headers[key] = value

        return safe_headers

    def _mask_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mascarar dados sensíveis no JSON"""
        sensitive_keys = ["password", "senha", "token", "api_key", "secret"]

        if isinstance(data, dict):
            safe_data = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    if isinstance(value, str) and len(value) > 4:
                        safe_data[key] = f"***{value[-4:]}"
                    else:
                        safe_data[key] = "***"
                elif isinstance(value, (dict, list)):
                    safe_data[key] = self._mask_sensitive_data(value)
                else:
                    safe_data[key] = value
            return safe_data
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        else:
            return data

    def _mask_token(self, token: Optional[str]) -> str:
        """Mascarar token JWT"""
        if not token:
            return "None"
        if len(token) <= 8:
            return "***"
        return f"{token[:4]}...{token[-4:]}"


# Instância global do logger
drg_logger = DRGLogger()
