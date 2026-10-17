"""Detecção de brute force: limiar de falhas consecutivas dispara alerta.

Regra de negócio: por par (usuário, IP), conta as falhas consecutivas
terminadas no evento mais recente. Ao atingir exatamente o limiar
(padrão 10) gera-se um alerta. Uma autenticação bem-sucedida zera o
contador. Não se re-alerta enquanto o mesmo ataque estiver em curso.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .database import connect, insert_alert, insert_event
from .models import Alert, AuthEvent

THRESHOLD_DEFAULT = 10


class BruteForceDetector:
    """Detetor de brute force com persistência SQLite.

    Args:
        db_path: caminho do ficheiro SQLite.
        threshold: número de falhas consecutivas que dispara o alerta.
    """

    def __init__(self, db_path: str | Path, threshold: int = THRESHOLD_DEFAULT) -> None:
        self.db_path = str(db_path)
        self.threshold = int(threshold)

    def process_event(
        self,
        username: str,
        ip: str,
        success: bool,
        timestamp: str | None = None,
    ) -> Alert | None:
        """Regista um evento e devolve um Alert se o limiar for atingido."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        event = AuthEvent(
            username=username,
            ip=ip,
            success=success,
            timestamp=timestamp,
        )
        with connect(self.db_path) as conn:
            insert_event(conn, event)
            if not success:
                consecutive = self._consecutive_failures(conn, username, ip)
                if consecutive == self.threshold:
                    alert = Alert(
                        username=username,
                        ip=ip,
                        failure_count=consecutive,
                        triggered_at=timestamp,
                    )
                    insert_alert(conn, alert)
                    return alert
        return None

    def _consecutive_failures(
        self, conn: sqlite3.Connection, username: str, ip: str
    ) -> int:
        """Conta falhas consecutivas a partir do evento mais recente."""
        rows = conn.execute(
            """
            SELECT success FROM auth_events
            WHERE username = ? AND ip = ?
            ORDER BY timestamp DESC, id DESC
            LIMIT ?
            """,
            (username, ip, self.threshold + 1),
        ).fetchall()
        count = 0
        for (success,) in rows:
            if success == 0:
                count += 1
            else:
                break
        return count
