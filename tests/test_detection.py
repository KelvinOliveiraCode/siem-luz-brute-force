"""Testes do detetor de brute force (BruteForceDetector)."""

from __future__ import annotations

from siem_luz.detection import BruteForceDetector

THRESHOLD = 10
USER = "admin"
IP = "10.0.0.0"


def _ts(i: int) -> str:
    return f"2026-01-01T00:00:{i:02d}Z"


def _alerts(detector: BruteForceDetector, username: str, ip: str,
            successes: list[bool], offset: int = 0) -> list:
    """Executa eventos em sequência e devolve os alertas gerados."""
    alerts = []
    for i, success in enumerate(successes):
        alert = detector.process_event(username, ip, success, _ts(offset + i))
        if alert is not None:
            alerts.append(alert)
    return alerts


def test_dez_falhas_consecutivas_geram_um_alerta(tmp_path):
    db = tmp_path / "siem.db"
    detector = BruteForceDetector(db, threshold=THRESHOLD)
    alerts = _alerts(detector, USER, IP, [False] * THRESHOLD)
    assert len(alerts) == 1
    assert alerts[0].failure_count == THRESHOLD
    assert alerts[0].rule == "brute_force_10_consecutive_failures"


def test_nove_falhas_nao_geram_alerta(tmp_path):
    db = tmp_path / "siem.db"
    detector = BruteForceDetector(db, threshold=THRESHOLD)
    alerts = _alerts(detector, USER, IP, [False] * 9)
    assert alerts == []


def test_onze_falhas_geram_apenas_um_alerta(tmp_path):
    db = tmp_path / "siem.db"
    detector = BruteForceDetector(db, threshold=THRESHOLD)
    alerts = _alerts(detector, USER, IP, [False] * (THRESHOLD + 1))
    assert len(alerts) == 1


def test_sucesso_zera_contador_e_novo_alerta(tmp_path):
    db = tmp_path / "siem.db"
    detector = BruteForceDetector(db, threshold=THRESHOLD)
    alerts = _alerts(detector, USER, IP, [False] * THRESHOLD)
    assert len(alerts) == 1
    # Autenticação bem-sucedida zera o contador (timestamp posterior).
    detector.process_event(USER, IP, True, _ts(100))
    # Mais 10 falhas com timestamps posteriores disparam um novo alerta.
    alerts += _alerts(detector, USER, IP, [False] * THRESHOLD, offset=101)
    assert len(alerts) == 2


def test_usuarios_e_ips_contam_separadamente(tmp_path):
    db = tmp_path / "siem.db"
    detector = BruteForceDetector(db, threshold=THRESHOLD)
    _alerts(detector, "user_a", IP, [False] * THRESHOLD)
    alerts = _alerts(detector, "user_b", IP, [False] * THRESHOLD)
    assert len(alerts) == 1
    assert alerts[0].username == "user_b"
