# BRIEF — siem-luz-brute-force

Projeto: **siem-luz-brute-force** (área: Cibersegurança)
Owner de validação: o workflow manager (eu).
Saída: `C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\siem-luz-brute-force\`

## Entregas

| Arquivo | Conteúdo |
|---------|----------|
| `README.md` | Documentação bilíngue PT-BR + EN (título, descrição, como usar, testes, licença MIT, autor Kelvin Oliveira) |
| `BRIEF.md` | Este resumo de entregas e como verificar |
| `pyproject.toml` | Declaração do projeto, dependências (`flask`) e dev (`pytest`, `ruff`) |
| `src/siem_luz/__init__.py` | Pacote e versão |
| `src/siem_luz/models.py` | `AuthEvent` e `Alert` (dataclasses imutáveis, tipadas) |
| `src/siem_luz/database.py` | Persistência SQLite (schema, `connect`, `insert_event`, `insert_alert`, `fetch_alerts`, `fetch_events`) |
| `src/siem_luz/detection.py` | `BruteForceDetector`: limiar de falhas consecutivas (padrão 10) por (usuário, IP) |
| `src/siem_luz/app.py` | Flask: `POST /auth`, `GET /alerts`, `GET /events`, `GET /dashboard` + CLI `siem-luz` |
| `tests/test_detection.py` | Testes do detetor (8 cenários) |
| `tests/test_app.py` | Testes dos endpoints Flask |
| `.venv/` | Ambiente virtual com dependências instaladas |

## Stack

Python 3.10+, Flask, JSON, SQLite. Determinístico, com tipos e docstrings.

## Critérios de aceitação (MVP)

1. Deteta 10 falhas consecutivas de autenticação por (usuário, IP) e gera um alerta.
2. 11 falhas geram apenas um alerta (sem re-alerta durante o ataque).
3. Uma autenticação bem-sucedida zera o contador.
4. Contadores separados por usuário e IP.
5. Suíte de testes passa (`pytest`).
6. README bilíngue PT-BR + EN completo.

## Como verificar

```bash
cd C:\Users\Kelvin\AppData\Local\Temp\opencode\github-staging\projects\siem-luz-brute-force
uv run ruff check .      # qualidade do código (deve passar sem erros)
uv run pytest -q         # suíte de testes (deve passar: 8 passed)
```

Comando de teste usado: `uv run pytest -q`.
Resultado dos testes: **8 passed** (0 failed).
Caminho do README: `...\siem-luz-brute-force\README.md`.
Caminho do BRIEF: `...\siem-luz-brute-force\BRIEF.md`.
