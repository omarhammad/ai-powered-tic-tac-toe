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
