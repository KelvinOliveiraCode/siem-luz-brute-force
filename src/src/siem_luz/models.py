"""Modelos de dados do siem-luz-brute-force."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthEvent:
    """Evento de autenticação observado nos logs.

    Attributes:
        username: nome de usuário tentado.
        ip: endereço IP de origem da tentativa.
        success: True se a autenticação foi bem-sucedida, False caso contrário.
        timestamp: carimbo ISO 8601 em UTC do evento.
    """

    username: str
    ip: str
    success: bool
    timestamp: str


@dataclass(frozen=True)
class Alert:
    """Alerta de brute force gerado quando o limiar é atingido.

    Attributes:
        username: usuário alvo das falhas consecutivas.
        ip: endereço IP de origem das falhas.
        failure_count: número de falhas consecutivas no momento do alerta.
        triggered_at: carimbo em que o alerta foi disparado.
        rule: identificador da regra disparada.
    """

    username: str
    ip: str
    failure_count: int
    triggered_at: str
    rule: str = "brute_force_10_consecutive_failures"
