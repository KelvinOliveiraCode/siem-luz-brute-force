"""Aplicação Flask do siem-luz-brute-force."""

from __future__ import annotations

import argparse
import sqlite3

from flask import Flask, jsonify, render_template_string, request

from .database import connect, fetch_alerts, fetch_events
from .detection import THRESHOLD_DEFAULT, BruteForceDetector

DEFAULT_DB_PATH = "data/siem.db"

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>siem-luz-brute-force — Dashboard</title>
<style>
  body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
         margin: 0; padding: 2rem; background: #f7f8fa; color: #111; }
  h1 { font-size: 1.25rem; margin: 0 0 1rem 0; }
  .card { background: #fff; border: 1px solid #d5d8de; border-radius: 8px;
          padding: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px
          rgba(0, 0, 0, 0.04); }
  .kpi { display: flex; gap: 1rem; flex-wrap: wrap; }
  .kpi .stat { background: #eef0f3; border-radius: 6px; padding: 0.6rem 1rem; }
  .kpi .stat .value { font-size: 1.5rem; font-weight: 700; color: #0b6; }
  .kpi .stat .label { font-size: 0.85rem; color: #555; }
  table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  th, td { border: 1px solid #d5d8de; padding: 0.5rem 0.75rem; text-align: left; }
  th { background: #eef0f3; font-weight: 600; }
  tr:nth-child(even) td { background: #fafbfc; }
  .alert-row { color: #b00020; font-weight: 600; }
  .badge-fail { color: #b00020; } .badge-ok { color: #0b6; }
  code { background: #eef0f3; padding: 0 0.25rem; border-radius: 4px;
         font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
  a { color: #0b6; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>
  <h1>siem-luz-brute-force</h1>
  <p>SIEM leve de detecção de <code>brute force</code> — limiar de
     <strong>{{ threshold }}</strong> falhas consecutivas por (usuário, IP).</p>

  <div class="card">
    <div class="kpi">
      <div class="stat"><div class="value">{{ total_events }}</div>
          <div class="label">eventos de autenticação</div></div>
      <div class="stat"><div class="value" style="color:#b00020">{{ total_alerts }}</div>
          <div class="label">alertas de brute force</div></div>
    </div>
  </div>

  <div class="card">
    <h2 style="margin-top:0;font-size:1rem">Alertas recentes</h2>
    {% if alerts %}
    <table>
      <thead><tr><th>Disparado em</th><th>Usuário</th><th>IP</th>
          <th>Falhas</th><th>Regra</th></tr></thead>
      <tbody>
      {% for a in alerts %}
        <tr class="alert-row"><td>{{ a.triggered_at }}</td><td>{{ a.username }}</td>
          <td>{{ a.ip }}</td><td>{{ a.failure_count }}</td><td>{{ a.rule }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
    {% else %}
      <p style="color:#555">Nenhum alerta até agora.</p>
    {% endif %}
  </div>

  <div class="card">
    <h2 style="margin-top:0;font-size:1rem">Últimos eventos de autenticação</h2>
    {% if events %}
    <table>
      <thead><tr><th>Timestamp</th><th>Usuário</th><th>IP</th><th>Resultado</th></tr></thead>
      <tbody>
      {% for e in events %}
        <tr><td>{{ e.timestamp }}</td><td>{{ e.username }}</td><td>{{ e.ip }}</td>
          <td class="{{ 'badge-ok' if e.success else 'badge-fail' }}">
          {{ 'sucesso' if e.success else 'falha' }}</td></tr>
      {% endfor %}
      </tbody>
    </table>
    {% else %}
      <p style="color:#555">Nenhum evento registrado.</p>
    {% endif %}
  </div>

  <p style="margin-top:1rem;color:#555;font-size:0.85rem">
    Endpoints: <code>POST /auth</code> · <code>GET /alerts</code> ·
    <code>GET /events</code> · <code>GET /dashboard</code>
  </p>
</body>
</html>
"""


def create_app(db_path: str = DEFAULT_DB_PATH) -> Flask:
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path
    detector = BruteForceDetector(db_path, threshold=THRESHOLD_DEFAULT)

    def _row_dict(row: sqlite3.Row) -> dict:
        return {key: row[key] for key in row.keys()}  # noqa: SIM118 (sqlite3.Row iteração dá valores, não chaves)

    @app.post("/auth")
    def auth():
        """Registra uma tentativa de autenticação.

        Body JSON: {"username": str, "ip": str, "success": bool}
        """
        data = request.get_json(silent=True) or {}
        username = str(data.get("username", ""))
        ip = str(data.get("ip", ""))
        success = bool(data.get("success", False))
        alert = detector.process_event(username, ip, success)
        response = {"status": "ok", "alert": None}
        if alert is not None:
            response["alert"] = {
                "username": alert.username,
                "ip": alert.ip,
                "failure_count": alert.failure_count,
                "triggered_at": alert.triggered_at,
                "rule": alert.rule,
            }
        return jsonify(response), 201

    @app.get("/alerts")
    def alerts():
        """Lista alertas de brute force (mais recentes primeiro)."""
        with connect(app.config["DB_PATH"]) as conn:
            rows = fetch_alerts(conn)
        return jsonify([_row_dict(r) for r in rows])

    @app.get("/events")
    def events():
        """Lista eventos de autenticação recentes."""
        with connect(app.config["DB_PATH"]) as conn:
            rows = fetch_events(conn)
        return jsonify([_row_dict(r) for r in rows])

    @app.get("/dashboard")
    def dashboard():
        """Dashboard simples em HTML."""
        with connect(app.config["DB_PATH"]) as conn:
            alert_rows = list(fetch_alerts(conn))
            event_rows = list(fetch_events(conn))
        return render_template_string(
            DASHBOARD_HTML,
            threshold=THRESHOLD_DEFAULT,
            total_events=len(event_rows),
            total_alerts=len(alert_rows),
            alerts=[_row_dict(r) for r in alert_rows],
            events=[_row_dict(r) for r in event_rows],
        )

    return app


def main() -> None:
    """Ponto de entrada de linha de comando."""
    parser = argparse.ArgumentParser(
        description="siem-luz-brute-force: SIEM leve de detecção de brute force"
    )
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="caminho do SQLite")
    parser.add_argument("--host", default="127.0.0.1", help="host do servidor")
    parser.add_argument("--port", type=int, default=5000, help="porta do servidor")
    args = parser.parse_args()
    app = create_app(args.db)
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
