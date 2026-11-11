# Tasks API (projecte starter)

API de tasques mínima amb FastAPI. És el punt de partida de la lab: **no** conté cap configuració de
Claude Code (ni skills, ni hooks, ni MCP). Això ho heu de configurar vosaltres.

## Posada en marxa

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest -q                 # tests
ruff check . && ruff format --check .   # lint i format
uvicorn app.main:app --reload           # servidor a http://127.0.0.1:8000/docs
```

## Estructura

```
app/
  main.py     # rutes FastAPI
  models.py   # models Pydantic (Task, TaskCreate, TaskStatus)
  store.py    # emmagatzematge en memòria
tests/
  conftest.py # fixtures (client, store net)
  test_tasks.py
```

## Endpoints existents

| Mètode | Ruta            | Descripció            |
|--------|-----------------|-----------------------|
| POST   | `/tasks`        | Crea una tasca (201)  |
| GET    | `/tasks`        | Llista totes          |
| GET    | `/tasks/{id}`   | Detall (404 si no hi és) |
| DELETE | `/tasks/{id}`   | Esborra (204 / 404)   |
