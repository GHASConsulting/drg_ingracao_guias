"""
Middleware de Segurança para FastAPI
Implementa proteções básicas contra ataques comuns
"""

import logging
import time
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse

# Logger para segurança
security_logger = logging.getLogger("security")


class SecurityMiddleware:
    """Middleware para proteção contra ataques básicos"""

    def __init__(self, app):
        self.app = app
        self.suspicious_paths = [
            "/login",
            "/admin",
            "/wp-admin",
            "/wp-login.php",
            "/administrator",
            "/phpmyadmin",
            "/.env",
            "/config",
            "/backup",
            "/test",
            "/api/login",
            "/api/admin",
        ]
        self.blocked_ips = set()  # IPs bloqueados temporariamente
        self.request_counts = {}  # Contador de requisições por IP

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Verificar IP bloqueado
            client_ip = request.client.host
            if client_ip in self.blocked_ips:
                response = JSONResponse(
                    status_code=403,
                    content={"detail": "Access denied", "reason": "IP blocked"},
                )
                await response(scope, receive, send)
                return

            # Log tentativas suspeitas
            if request.url.path in self.suspicious_paths:
                security_logger.warning(
                    f"🚨 Tentativa suspeita detectada - IP: {client_ip} | "
                    f"Path: {request.url.path} | User-Agent: {request.headers.get('user-agent', 'Unknown')}"
                )

                # Bloquear apenas rotas que já retornam 404
                response = JSONResponse(
                    status_code=404, content={"detail": "Not found"}
                )
                await response(scope, receive, send)
                return

            # Rate limiting básico (simples)
            current_time = time.time()
            if client_ip not in self.request_counts:
                self.request_counts[client_ip] = {
                    "count": 0,
                    "reset_time": current_time + 3600,
                }  # Reset a cada hora

            # Reset contador se passou 1 hora
            if current_time > self.request_counts[client_ip]["reset_time"]:
                self.request_counts[client_ip] = {
                    "count": 0,
                    "reset_time": current_time + 3600,
                }

            # Incrementar contador
            self.request_counts[client_ip]["count"] += 1

            # Bloquear se muitas requisições (mais de 1000 por hora)
            if self.request_counts[client_ip]["count"] > 1000:
                security_logger.warning(f"🚨 Rate limit excedido - IP: {client_ip}")
                self.blocked_ips.add(client_ip)
                response = JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests", "retry_after": 3600},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


def setup_security_middleware(app):
    """Configurar middleware de segurança"""
    app.add_middleware(SecurityMiddleware)
    security_logger.info("🛡️ Middleware de segurança configurado")
