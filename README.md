# AI-Powered Tic-Tac-Toe Platform

A playable Tic-Tac-Toe platform built as two Python services: a game backend for sessions and the browser experience, and an AI service for computer moves and win probability estimates. The services communicate over HTTP; the game backend also publishes state changes to RabbitMQ for integration with a wider game platform.

## What the platform does

- Play human-versus-human or human-versus-AI games through a browser interface.
- Create sessions and make moves through FastAPI endpoints, with turn validation and win/draw detection.
- Choose AI moves with Monte Carlo Tree Search (easy and medium) or a trained XGBoost policy model (hard).
- Estimate each player's win probability with a separate machine learning model.
- Publish game updates through RabbitMQ. The AI service also contains a self-play data pipeline and ML experiments.

## Repository layout

| Directory | Role |
| --- | --- |
| [`game-backend/`](game-backend/) | FastAPI game API, domain rules, in-memory sessions, browser UI, AI HTTP client, and RabbitMQ event publisher. |
| [`ai-service/`](ai-service/) | AI API, MCTS, trained model inference, self-play scripts, and ML experiments. |

Each directory contains its own dependencies, tests, and original project README. The repository combines the Git histories of the two services, so the progression of each project is available in the commit history.

## How the services work together

1. The game backend creates a session for two human players or one human and one AI player.
2. The browser loads the game state and submits moves to the backend.
3. On an AI turn, the backend calls the AI service's `/ai/choose-move` endpoint and applies the returned move using the same game rules.
4. The browser requests `/session/{sessionId}/winning-proba` from the backend, which obtains model estimates from the AI service.
5. After a move, the backend publishes a game state event to RabbitMQ when a broker is available.

## Run locally

Use Python 3.11. Open **two terminals** at the monorepo root and set up each service separately; each has its own `requirements.txt`.

**Terminal 1 — AI service:**

```bash
cd ai-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main.python.main:app --reload --port 9100
```

The AI API documentation is at `http://localhost:9100/docs`. Its saved models under `ai-service/src/main/resources/models/` are needed at startup.

**Terminal 2 — game backend:**

```bash
cd game-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
AI_BASE_URL=http://localhost:9100/ai uvicorn src.main.python.main:app --reload --port 8090
```

The game API documentation is at `http://localhost:8090/docs`. On Windows, use `.venv\Scripts\activate` instead. Start each command from its service directory because templates, static files, and model paths are relative to the working directory.

The backend stores sessions in memory; restarting it clears active games. To deliver game events, set `AMQP_URL` to a reachable RabbitMQ broker. The self-play pipeline in `ai-service/` also needs RabbitMQ. Service settings can be supplied as environment variables or through the service's local `.env` file.

### Create a game

With both services running, create a human-versus-AI session:

```bash
curl -X POST http://localhost:8090/session/create \
  -H 'Content-Type: application/json' \
  -d '{"sessionId":"demo-game","player_x_id":"human","player_o_id":"computer","player_x_name":"Player","player_o_name":"AI","player_x_is_ai":false,"player_o_is_ai":true,"player_o_ai_difficulty":"medium"}'
```

Open the URL in the `gamePlayableUrls` response to play as the human player. The game backend also provides `GET /sessions/{sessionId}` and `POST /move`; the AI service exposes `POST /ai/choose-move` and `POST /ai/winning-proba`.

## Tests

Run the suites independently from each service directory:

```bash
cd game-backend
pytest -q
```

```bash
cd ai-service
pytest -q
```

The game backend tests cover rules, service behavior, repository storage, and API endpoints. The AI service includes API and integration tests; some may require packaged models or external services.

## Technology

Python · FastAPI · Pydantic · JavaScript · Jinja2 · RabbitMQ · MCTS · XGBoost · scikit-learn · MLflow · pytest · GitLab CI
