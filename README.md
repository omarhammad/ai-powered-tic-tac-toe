# Tic-Tac-Toe AI Player Service  
MCTS-based AI Player with support for multiple difficulty levels, FastAPI endpoints, and a clean architecture ready for ML integration.

This service is built using a layered design:
- **Domain layer:** pure game state models (TicTacToeState, Move, enums)
- **Infrastructure layer:** MCTS implementation
- **Service layer:** AIService for move selection and difficulty management
- **Controller layer:** FastAPI routes for `/choose-move` and `/winning-proba`
- **Schemas layer:** Pydantic models for API input/output

The project is designed from the start to allow **ML integration later**, especially for:
- policy imitation (best-move prediction)
- winning probability estimation

Below is the full prompt set that was used while building the AI Player.  

---

## Prompt 1 — Architecture Design

**Title:** *Design the Architecture for My FastAPI MCTS AI System*

```
You are helping me design a small AI module for a board-game platform.
The goal is to build an AI Player for Tic-Tac-Toe using FastAPI and MCTS.
Please follow these constraints:

1. The project must use a clean layered architecture:

    * Controller layer (FastAPI endpoints)
    * Service layer (AI logic, difficulty adjustment)
    * Infrastructure layer (MCTS agents, reusable strategy classes)
    * Repository layer (only if needed later)

2. The AI must expose:

    * POST /choose-move      → returns the AI's move
    * GET  /winning-proba    → placeholder endpoint, not implemented yet

3. The AI uses an MCTS agent as the first and only AI model for now.
   Later I want the design to allow ML models to be plugged in.

4. Difficulty levels must work by changing the computation budget
   (simulations, number of rollouts, etc.).

5. The AI receives a JSON-formatted TicTacToeState.
   Please tell me exactly what fields I need to include based on a
   typical refactored game engine.

6. Please use clear bullet points, diagrams if useful, and
   explain reasoning step by step (chain of thought).

Before finalizing the design,
ask me questions if any requirement is unclear.
```

---

## Prompt 2 — Folder Structure and Scaffolding

**Title:** *Create the Project Structure for the AI Module*

```
Based on the architecture you just designed, generate a full folder
structure for the FastAPI AI Player service.

Please include:

* app/controllers
* app/services
* app/infrastructure/mcts
* app/domain (game state models)
* app/config
* main.py

Use clear explanations and small code samples to show me how each
file fits together.

Follow good software engineering practices.
Make the structure ready for replacing the MCTS agent with ML models later.

If something is missing, ask me.
```

---

## Prompt 3 — Domain Models

**Title:** *Define the TicTacToeState Domain Model*

```
I am now working on the domain layer.
Please create clean Python dataclasses for:

* TicTacToeState
* Move
* Player enum
* GameStatus enum

The model must include the fields needed for:

* describing the board state
* identifying the current player
* determining legal moves
* representing end game states

Use simple, explicit attributes so they can be serialized to JSON easily.

Provide:

* final code
* 1 example JSON state coming from a running game
```

---

## Prompt 4 — MCTS Implementation

**Title:** *Implement an MCTS Agent with Adjustable Difficulty*

```
I want a clean and reusable implementation of MCTS for Tic-Tac-Toe.
Please implement it inside app/infrastructure/mcts.

Include these components:

* Node class
* MCTS class with:

    * selection
    * expansion
    * simulation
    * backpropagation
* A choose_move(state, computation_budget) function

Difficulty levels must be simply:

* easy: few simulations
* medium: moderate simulations
* hard: many simulations

Make sure the algorithm is fully deterministic unless randomness is needed.

Explain the logic step by step, then generate the final code.
```

---

## Prompt 5 — AI Service

**Title:** *Create AIService with Difficulty Management and Dynamic Adjustment*

```
Please implement the AIService class.

Responsibilities:

1. Accept TicTacToeState and call the MCTS agent.

2. Dynamically choose difficulty based on a simple rule:

    * if the human is winning often → increase difficulty
    * if the human is losing badly → decrease difficulty
      (just make a placeholder rule)

3. Add a method get_winning_probability(state)
   but return a static value for now.

4. Keep the design open for switching from MCTS to ML models later.

Produce final code and explain how each method works.
```

---

## Prompt 6 — FastAPI Controllers

**Title:** *Generate FastAPI Controllers for choose_move and winning_proba*

```
Please create the controller layer using FastAPI.

Endpoints:
POST /choose-move
- Input: TicTacToeState as JSON
- Output: best move (row, col)

GET /winning-proba
- Input: TicTacToeState (optional via query or body)
- Output: static probability for now

Make sure the controller calls the AIService correctly.

Return Pydantic models for input and output.

After generating the code:

* list all imports
* show the final main.py file

```

---

## Prompt 7 — Integration Tests

**Title:** *Generate Integration Tests for the AI Endpoints*

```
Please write pytest integration tests for the FastAPI service:

* test_choose_move_returns_valid_cell
* test_choose_move_changes_with_difficulty
* test_winning_proba_endpoint_exists

Use TestClient from fastapi.testclient.

Use example TicTacToeState JSON objects.
```

---

## Prompt 8 — Review and Refinement

**Title:** *Review the Full AI Module and Suggest Improvements*

```
Now that all layers are implemented, review the design and code.

Please:

1. propose improvements
2. detect weaknesses in architecture
3. suggest how to later plug in ML models:

    * for policy imitation
    * for win probability prediction
4. suggest performance improvements for MCTS

Then regenerate a revised version of any files that need changes.
```

---