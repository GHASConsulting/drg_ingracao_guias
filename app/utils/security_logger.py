"""
Logger específico para eventos de segurança
"""

import logging
import os
from datetime import datetime


def setup_security_logger():
    """Configurar logger de segurança"""

    # Criar diretório de logs se não existir
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configurar logger de segurança
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.WARNING)

    # Handler para arquivo
    security_handler = logging.FileHandler(f"{log_dir}/security.log")
    security_handler.setLevel(logging.WARNING)

    # Formatter
    security_formatter = logging.Formatter(
        "%(asctime)s - SECURITY - %(levelname)s - %(message)s"
    )
    security_handler.setFormatter(security_formatter)

    # Adicionar handler se não existir
    if not security_logger.handlers:
        security_logger.addHandler(security_handler)

    return security_logger


def log_suspicious_activity(
    ip: str, path: str, user_agent: str = None, details: str = None
):
    """Log atividade suspeita"""
    security_logger = logging.getLogger("security")

    message = f"🚨 SUSPEITO - IP: {ip} | Path: {path}"
    if user_agent:
        message += f" | User-Agent: {user_agent}"
    if details:
        message += f" | Details: {details}"

    security_logger.warning(message)


def log_rate_limit_exceeded(ip: str, endpoint: str, limit: str):
    """Log rate limit excedido"""
    security_logger = logging.getLogger("security")

    message = f"🚨 RATE LIMIT - IP: {ip} | Endpoint: {endpoint} | Limit: {limit}"
    security_logger.warning(message)


def log_blocked_ip(ip: str, reason: str):
    """Log IP bloqueado"""
    security_logger = logging.getLogger("security")

    message = f"🚨 IP BLOQUEADO - IP: {ip} | Reason: {reason}"
    security_logger.error(message)
