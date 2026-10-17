"""Persistência SQLite: eventos de autenticação e alertas.

Todas as funções são síncronas e determinísticas. O esquema é criado
sob demanda na primeira conexão (CREATE TABLE IF NOT EXISTS).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path

from .models import Alert, AuthEvent

SCHEMA = """
CREATE TABLE IF NOT EXISTS auth_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    ip TEXT NOT NULL,
    success INTEGER NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    ip TEXT NOT NULL,
    failure_count INTEGER NOT NULL,
    triggered_at TEXT NOT NULL,
    rule TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_auth_events_user_ip_ts
    ON auth_events(username, ip, timestamp DESC, id DESC);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Abre (e inicializa) a conexão SQLite do caminho indicado."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def insert_event(conn: sqlite3.Connection, event: AuthEvent) -> None:
    """Insere um evento de autenticação."""
    conn.execute(
        "INSERT INTO auth_events (username, ip, success, timestamp) "
        "VALUES (?, ?, ?, ?)",
        (event.username, event.ip, int(event.success), event.timestamp),
    )


def insert_alert(conn: sqlite3.Connection, alert: Alert) -> None:
    """Insere um alerta de brute force."""
    conn.execute(
        "INSERT INTO alerts (username, ip, failure_count, triggered_at, rule) "
        "VALUES (?, ?, ?, ?, ?)",
        (alert.username, alert.ip, alert.failure_count,
         alert.triggered_at, alert.rule),
    )


def fetch_alerts(
    conn: sqlite3.Connection, limit: int = 50
) -> Iterable[sqlite3.Row]:
    """Retorna os alertas mais recentes primeiro."""
    return conn.execute(
        "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)
    )


def fetch_events(
    conn: sqlite3.Connection, limit: int = 50
) -> Iterable[sqlite3.Row]:
    """Retorna os eventos de autenticação mais recentes primeiro."""
    return conn.execute(
        "SELECT * FROM auth_events ORDER BY timestamp DESC, id DESC LIMIT ?",
        (limit,),
    )
