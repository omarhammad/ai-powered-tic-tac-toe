# Tic-Tac-Toe Game Backend (Python Refactor)
A refactored and modernized Python version of the classic Tic-Tac-Toe game.


## Game Source
Original game (Java):  
https://www.geeksforgeeks.org/java/tic-tac-toe-game-in-java/

---

## Refactoring Process

---

### Prompt 1 — Understanding the Legacy Code
**Purpose:** Understand what the original Java code does before rebuilding it.

**Prompt:**
``` 
I will give you legacy code for a Tic-Tac-Toe game written in java language.
Please help me understand it in a structured way.

Please do the following:

1. Explain the game rules based on the code.
2. List the main domain elements (board, players, moves, win check, etc.).
3. Describe how the original code works step-by-step.
4. Mention the main problems, code smells, or bad practices.
5. Point out what needs to be improved when rebuilding in Python.

Give the answer in clear sections and keep it simple.

{Game java code}

```
---
## Prompt 2 — Rebuilding the Domain Layer in Python
**Purpose:** Create a clean, testable Domain Layer based on the original Java logic.

**Prompt:**
```
Using the legacy code summary, please rewrite the game in clean Python using a layered architecture.

Focus only on the Domain Layer.  
Do not include FastAPI, I/O, UI, databases, or logging yet.

Requirements:
- Follow good software engineering practices.
- Use classes for GameSession, Board, and Rules.
- Keep everything pure and testable.
- No external libraries.
- Support: making moves, switching turns, checking win/draw, and getting board state.

Please output clean and well-organized Python code.
```

## Prompt 3 — Add Gameplay Logging Hooks
**Purpose:** Add logging points required by the assignment without implementing the backend yet.

**Prompt:**
```
Please extend my current Domain and Service Layer so the game supports gameplay logging.

Add a simple logging interface called “LoggingService” with methods like:
- log_move(sessionId, playerId, boardState, moveIndex, timestamp)
- log_state(sessionId, boardState, turn, moveCount, timestamp)
- log_end(sessionId, result, finalBoardState, timestamp)

Then:
- Update GameSession or GameService so it calls the logging methods at the correct points.
- Do NOT implement the actual logging here. Only create the LoggingService interface and show where it will be used.

Please keep the explanation short and easy to understand.
```

---

## Prompt 4 — Prepare for AI Support
**Purpose:** Allow the game engine to support AI players later.

**Prompt:**
```
Please extend the Service Layer so the game can support an AI player.

Create a simple interface called “AiStrategy” with:
- choose_move(gameSession) -> int

Then update the GameService so that:
- The service checks if the current turn belongs to an AI player.
- If it is an AI turn, GameService calls choose_move().
- The move is applied using the same GameSession logic as a human move.
- All logging actions should still be triggered.

I only need the interface and updated GameService code. Please do not implement the AI algorithm yet.
```


---

## Prompt 5 — Build the Infrastructure Layer
**Purpose:** Create the storage and logging clients used by the Service Layer.

**Prompt:**
```
Please build the Infrastructure Layer for my layered architecture game engine.

I need:

1. A SessionRepository that stores GameSession objects in memory.
2. A LoggingClient that sends HTTP POST requests to the Java backend to store gameplay logs.
3. Both components should be simple classes that the Service Layer can use.
4. Add short comments to help explain what each class does.

Keep everything simple and written in clean Python.
```


---

## Prompt 6 — Build the FastAPI Controller Layer
**Purpose:** Expose REST endpoints for the platform and frontend.

**Prompt:**
```
Please create the API Layer (FastAPI controllers) for my layered architecture game engine.

The controllers should include:

1. POST /session/create   
   - Called by the Java Game BC  
   - Creates a new GameSession  
   - Returns sessionId and the URL for the game UI page

2. POST /move  
   - Called by the game frontend  
   - Applies a move through the Service Layer  
   - Logs the move to the Java backend  
   - Returns the updated board and turn

3. GET /play/{sessionId}  
   - Returns the HTML template for the game UI

The controllers should call into the Service Layer and not talk to Domain or Infrastructure directly.
```

---

## Prompt 7 — Create Unit Tests (Human vs Human)
**Purpose:** Build the required unit test suite for the Domain and Service layers.

**Prompt:**
```
Please create a complete pytest unit test suite for my Python Tic-Tac-Toe game engine using a layered architecture.

Important notes:
- The AI feature is NOT implemented yet, so please test only Human vs Human gameplay.
- The Java Game BC logging backend does not exist yet, so the LoggingClient must be mocked using a simple stub or MagicMock.
- The tests should focus on testing the Domain Layer and the Service Layer.

Tests needed:

1. Test GameSession (Domain Layer):
   - A valid move is applied correctly.
   - An invalid move (cell already taken) raises an exception.
   - An invalid move (playing when it's not your turn) raises an exception.
   - The turn switches between players after each valid move.
   - Win detection works for:
     * Horizontal rows
     * Vertical columns
     * Both diagonals
   - A draw is detected when the board is full and no winner exists.

2. Test GameService (Application/Service Layer):
   - play_move() loads the session from the repository and applies a move.
   - play_move() calls logger.log_move() with the correct arguments (mocked logger).
   - play_move() returns the updated GameSession.
   - If the move is invalid, play_move() must NOT call the logger.

3. Test SessionRepository (Infrastructure layer — in-memory):
   - Saving a session stores it correctly.
   - Retrieving a session returns the right object.
   - Retrieving a non-existing session returns None.

General rules:
- Use pytest for all tests.
- Use MagicMock from unittest.mock to mock the LoggingClient.
- Do NOT write any tests for AI, since AI is not implemented yet.
- Keep all tests easy to read and suitable for a student project.

Please output these files:
- tests/test_game_session.py
- tests/test_game_service.py
- tests/test_session_repository.py

Make sure the code is clean, simple, and ready to run in my current project.
```

