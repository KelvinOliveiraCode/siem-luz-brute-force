"""Testes da aplicação Flask (endpoints HTTP)."""

from __future__ import annotations

import pytest

from siem_luz.app import create_app

THRESHOLD = 10
USER = "admin"
IP = "10.0.0.1"


@pytest.fixture
def client(tmp_path):
    db = tmp_path / "siem.db"
    app = create_app(str(db))
    app.testing = True
    return app.test_client()


def _falha(client):
    return client.post("/auth",
                       json={"username": USER, "ip": IP, "success": False})


def test_post_auth_registro_sem_alerta_ate_limiar(client):
    for _ in range(THRESHOLD - 1):
        _falha(client)
    resp = client.get("/alerts")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_post_auth_decimo_falha_gera_alerta(client):
    for _ in range(THRESHOLD):
        _falha(client)
    resp = client.get("/alerts")
    data = resp.get_json()
    assert resp.status_code == 200
    assert len(data) == 1
    assert data[0]["username"] == USER
    assert data[0]["ip"] == IP
    assert data[0]["failure_count"] == THRESHOLD


def test_get_dashboard_retorna_html(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"siem-luz-brute-force" in resp.data
