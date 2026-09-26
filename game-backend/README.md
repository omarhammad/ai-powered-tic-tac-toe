# Tic-Tac-Toe Game Backend

A Python game service for playing Tic-Tac-Toe through a browser or REST API. It manages game sessions and rules, connects to a separate AI service for computer moves and win probabilities, and publishes game state events to RabbitMQ for a wider game platform.

## Highlights

- Supports human-versus-human and human-versus-AI sessions, with turn validation and win/draw detection.
- Exposes FastAPI endpoints for session creation, game state, moves, and win probability estimates.
- Provides a browser interface with a responsive board and regular state refreshes.
- Requests AI moves and probability estimates from an external service; AI-versus-AI games are handled outside this backend.
- Publishes state updates to a RabbitMQ topic exchange after moves.
- Includes domain, service, repository, and API tests and a GitLab CI pipeline for compilation, tests, dependency scanning, and image builds.

## Tech stack

Python 3.11, FastAPI, Pydantic, Jinja2, vanilla JavaScript, RabbitMQ (`pika`), HTTPX, pytest, GitLab CI, and Cloud Native Buildpacks.

## Architecture

| Area | Responsibility |
| --- | --- |
| `src/main/python/domain/` | Board, players, turns, and game rules |
| `src/main/python/services/` | Session lifecycle, move handling, AI requests, and event creation |
| `src/main/python/controllers/` | HTTP routes and request/response models |
| `src/main/python/infrastructure/` | In-memory sessions, external AI client, and RabbitMQ publisher |
| `src/main/resources/` | Browser template, styles, and JavaScript |
| `src/tests/` | Automated tests |

## Run locally

From the repository root, create a Python 3.11 environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main.python.main:app --reload --port 8090
```

On Windows, activate the environment with `.venv\Scripts\activate`.

The API is available at `http://127.0.0.1:8090`, with interactive documentation at `/docs`. Sessions are held in memory, so restarting the process clears them. For AI moves and win probabilities, run the companion AI service and set `AI_BASE_URL` to its `/ai` base URL. For event delivery, configure `AMQP_URL` for an accessible RabbitMQ broker. The application reads these values from environment variables or a local `.env` file; the defaults are in `src/main/python/config/config.py`.

### Try a game

Create a human-versus-human session:

```bash
curl -X POST http://127.0.0.1:8090/session/create \
  -H 'Content-Type: application/json' \
  -d '{"sessionId":"demo-game","player_x_id":"player-x","player_o_id":"player-o","player_x_name":"Player X","player_o_name":"Player O","player_x_is_ai":false,"player_o_is_ai":false}'
```

Open either URL in the `gamePlayableUrls` response. Each URL identifies a player. The backend also exposes `GET /sessions/{sessionId}`, `POST /move`, and `GET /session/{sessionId}/winning-proba`. Probability estimates require the external AI service.

## Tests

```bash
pytest -q
```

The tests cover the game rules, application service, in-memory repository, and API behavior.

## Related project

The companion AI service supplies computer moves and win probability estimates. This repository contains the playable game and its integration with that service.
