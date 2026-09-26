# Tic-Tac-Toe AI Service

A FastAPI service for choosing Tic-Tac-Toe moves and estimating the current player's chance of winning. It combines Monte Carlo Tree Search (MCTS) with trained machine learning models, and includes a self-play pipeline for generating game-state data.

## Features

- **Move selection:** `POST /ai/choose-move` accepts a board and difficulty. Easy and medium use MCTS with different simulation budgets; hard uses an XGBoost policy model.
- **Win probability:** `POST /ai/winning-proba` uses a saved scikit-learn model loaded through MLflow to estimate the current player's win probability.
- **Self-play data:** AI-vs-AI games record board state, legal moves, chosen move, a stronger MCTS move, outcome, and reward. Events are published to RabbitMQ.
- **Experiments:** notebooks prepare self-play data and compare models for policy imitation and win probability. MLflow artifacts and processed Parquet datasets are included.
- **Delivery:** Dockerfile, GitLab CI jobs for compilation/tests/image build, and API/integration tests.

## How move selection works

The game state is represented as a nine-cell board and current player. The service rejects completed games and returns the index of a legal cell. The MCTS implementation performs selection, expansion, random simulation, and backpropagation. Its search budget varies by difficulty. For hard difficulty, the policy model predicts scores for board positions and masks occupied cells before selecting a move.

The win probability endpoint is a separate prediction task; it loads a model trained on game-state features. These estimates are model outputs, not guaranteed outcomes.

## API

Run the service from the repository root:

```bash
python -m pip install -r requirements.txt
uvicorn src.main.python.main:app --reload --port 9100
```

Open `http://localhost:9100/docs` for the interactive API documentation. The service expects its saved policy and win-probability model files under `src/main/resources/models/`.

Example request to `POST /ai/choose-move?difficulty=medium`:

```json
{
  "board": ["X", "O", " ", " ", "X", " ", " ", " ", "O"],
  "current_player": "X"
}
```

A successful response has an `index` from 0 to 8. The same board shape can be posted to `/ai/winning-proba`, which returns a `probability` between 0 and 1.

## Repository structure

| Path | Purpose |
| --- | --- |
| [`src/main/python/domain/`](src/main/python/domain/) | Board state, moves, game records, and enums. |
| [`src/main/python/infrastructure/mcts/`](src/main/python/infrastructure/mcts/) | MCTS search and tree nodes. |
| [`src/main/python/infrastructure/ml/`](src/main/python/infrastructure/ml/) | Policy and win-probability model loading and inference. |
| [`src/main/python/services/`](src/main/python/services/) | Move selection and self-play orchestration. |
| [`src/main/python/controllers/`](src/main/python/controllers/) | FastAPI routes and request/response models. |
| [`ml_scripts/`](ml_scripts/) | Dataset preparation, model experiments, and MLflow outputs. |
| [`scripts/run_self_play.py`](scripts/run_self_play.py) | CLI entry point for generating self-play events through RabbitMQ. |
| [`src/tests/`](src/tests/) | API and model integration tests. |

## Self-play and experiments

The self-play script accepts `--games`, `--noise`, and `--amqp-url`. It requires a reachable RabbitMQ broker and publishes game-state messages plus a completion event. The ML notebooks use collected data to train or compare policy imitation and win-probability models. Existing Parquet files and MLflow runs are snapshots of those experiments.

## Technology

Python · FastAPI · Pydantic · MCTS · XGBoost · scikit-learn · MLflow · RabbitMQ · pandas · Parquet · Docker · GitLab CI

## Reproducibility notes

Run commands from the repository root because model locations are relative paths. The packaged models are required even for MCTS requests because the service loads both models on startup. The ML notebooks and local MLflow database contain experiment artifacts; reproducing their training runs may require the original event pipeline and environment. The API and tests have not been rerun for this README.
