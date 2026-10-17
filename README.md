# siem-luz-brute-force

SIEM leve com detecção de brute force em logs de autenticação. Stack: Python, Flask, JSON e SQLite.

Deteta 10 falhas consecutivas de autenticação por par (usuário, IP) e gera um alerta. Uma autenticação bem-sucedida zera o contador, então não há re-alerta enquanto o mesmo ataque estiver em curso. Inclui dashboard simples em HTML e endpoints JSON para integração.

---

## Português do Brasil

### Descrição

`siem-luz-brute-force` é um SIEM mínimo voltado a detecção de brute force. Lê eventos de autenticação (usuário, IP, sucesso/falha), armazena em SQLite e dispara um alerta quando o mesmo par (usuário, IP) acumula 10 falhas seguidas.

### Como usar

1. Crie o ambiente e instale as dependências:

```bash
cd siem-luz-brute-force
uv sync --dev
```

2. Inicie o servidor:

```bash
uv run siem-luz
# ou: uv run python -m siem_luz.app
```

O servidor escuta em `http://127.0.0.1:5000` e grava o banco em `data/siem.db`.

3. Registre eventos de autenticação:

```bash
curl -X POST http://127.0.0.1:5000/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","ip":"10.0.0.1","success":false}'
```

4. Consulte alertas e eventos:

```bash
curl http://127.0.0.1:5000/alerts
curl http://127.0.0.1:5000/events
```

5. Abra o dashboard:

```text
http://127.0.0.1:5000/dashboard
```

### Endpoints

| Método | Caminho | Corpo | Retorna |
|--------|---------|-------|---------|
| POST | `/auth` | `{"username","ip","success"}` | status e alerta, se houver |
| GET | `/alerts` | — | lista de alertas (mais recentes primeiro) |
| GET | `/events` | — | últimos eventos de autenticação |
| GET | `/dashboard` | — | dashboard em HTML |

### Testes

```bash
uv run pytest -q
```

Resultado esperado: 8 passed. A suíte cobre o limiar de 10 falhas, 9 falhas sem alerta, 11 falhas com um único alerta, reset do contador após sucesso e separação por usuário/IP.

### Licença

MIT

### Autor

Kelvin Oliveira

---

## English

### Description

`siem-luz-brute-force` is a minimal SIEM for brute force detection. It reads authentication events (username, IP, success/failure), stores them in SQLite, and raises an alert when the same (username, IP) pair accumulates 10 consecutive failures. A successful authentication resets the counter, so there is no re-alert while the same attack is ongoing. Includes a simple HTML dashboard and JSON endpoints for integration.

### How to use

1. Create the environment and install dependencies:

```bash
cd siem-luz-brute-force
uv sync --dev
```

2. Start the server:

```bash
uv run siem-luz
# or: uv run python -m siem_luz.app
```

The server listens on `http://127.0.0.1:5000` and writes the database to `data/siem.db`.

3. Register authentication events:

```bash
curl -X POST http://127.0.0.1:5000/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","ip":"10.0.0.1","success":false}'
```

4. Query alerts and events:

```bash
curl http://127.0.0.1:5000/alerts
curl http://127.0.0.1:5000/events
```

5. Open the dashboard:

```text
http://127.0.0.1:5000/dashboard
```

### Endpoints

| Method | Path | Body | Returns |
|--------|------|------|---------|
| POST | `/auth` | `{"username","ip","success"}` | status and alert, if any |
| GET | `/alerts` | — | list of alerts (newest first) |
| GET | `/events` | — | recent authentication events |
| GET | `/dashboard` | — | HTML dashboard |

### Tests

```bash
uv run pytest -q
```

Expected result: 8 passed. The suite covers the 10-failure threshold, 9 failures without alert, 11 failures with a single alert, counter reset after success, and per user/IP separation.

### License

MIT

### Author

Kelvin Oliveira
