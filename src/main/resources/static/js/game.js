// ---------------------------------------------------------
// This script:
//  - Loads game state from /sessions/{SESSION_ID}
//  - Determines if this browser controls X or O
//  - Allows moves only when it's this player's turn
//  - Polls every 1s to keep both players in sync
// ---------------------------------------------------------

let state = null;
let myRole = null;
let moveCount = 0;
let pollingInterval = null;

// -----------------------------------------------------------
window.addEventListener("DOMContentLoaded", () => {
    loadSession();
    pollingInterval = setInterval(loadSession, 1000);
});

// -----------------------------------------------------------
async function loadSession() {
    const res = await fetch(`/sessions/${SESSION_ID}`);
    if (!res.ok) return;

    state = await res.json();
    moveCount = state.board.filter(v => v !== null).length;

    determineMyRole();
    renderUI();

    // Stop polling if game is over
    if (state.isFinished) clearInterval(pollingInterval);
}

// -----------------------------------------------------------
function determineMyRole() {
    if (PLAYER_ID === state.playerX.id) myRole = "X";
    else if (PLAYER_ID === state.playerO.id) myRole = "O";
    else myRole = null;
}

// -----------------------------------------------------------
function renderUI() {
    renderPlayers();
    renderInfoBanner();
    renderBoard();
}

// -----------------------------------------------------------
function renderPlayers() {
    const sid = state.sessionId;
    document.getElementById("session-short").textContent =
        `${sid.slice(0, 6)}...${sid.slice(-3)}`;

    document.getElementById("player-x-name").textContent = state.playerX.name;
    document.getElementById("player-x-role").textContent = state.playerX.isAI ? "(AI)" : "(Human)";

    document.getElementById("player-o-name").textContent = state.playerO.name;
    document.getElementById("player-o-role").textContent = state.playerO.isAI ? "(AI)" : "(Human)";

    document.getElementById("you-badge").textContent =
        myRole ? `YOU ARE PLAYER ${myRole}` : "SPECTATOR";
}

// -----------------------------------------------------------
function renderInfoBanner() {
    const banner = document.getElementById("info-banner");

    // Spectator
    if (!myRole) {
        banner.textContent = "You are watching the game";
        banner.className = "info-banner info-spectator";
        return;
    }

    // Finished game
    if (state.isFinished) {
        if (state.winner) {
            const winnerName =
                state.winner === "X"
                    ? state.playerX.name
                    : state.playerO.name;

            banner.textContent = `🏆 Winner: ${winnerName}`;
            banner.className = "info-banner info-winner";
        } else {
            banner.textContent = "It's a Draw!";
            banner.className = "info-banner info-draw";
        }
        return;
    }

    // Player's turn
    if (state.currentTurn === myRole) {
        banner.textContent = "Your Turn";
        banner.className = "info-banner info-your-turn";
    } else {
        const oppName =
            state.currentTurn === "X"
                ? state.playerX.name
                : state.playerO.name;

        banner.textContent = `Waiting for ${oppName}...`;
        banner.className = "info-banner info-opponent-turn";
    }
}

// -----------------------------------------------------------
function renderBoard() {
    const board = document.getElementById("board");
    board.innerHTML = "";

    state.board.forEach((v, i) => {
        const cell = document.createElement("div");
        cell.classList.add("cell");

        if (v === "X") cell.classList.add("x");
        if (v === "O") cell.classList.add("o");

        const span = document.createElement("span");
        span.textContent = v || "";
        cell.appendChild(span);

        cell.addEventListener("click", () => tryMove(i));

        board.appendChild(cell);
    });

    board.classList.toggle("disabled", state.isFinished);
}

// -----------------------------------------------------------
async function tryMove(index) {
    if (state.isFinished) return;
    if (!myRole) return;
    if (state.currentTurn !== myRole) return;
    if (state.board[index] !== null) return;

    const res = await fetch("/move", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            sessionId: SESSION_ID,
            playerId: PLAYER_ID,
            moveIndex: index
        })
    });

    if (res.ok) {
        state = await res.json();
        moveCount = state.board.filter(v => v !== null).length;
        renderUI();

        // If move finishes game → stop polling
        if (state.isFinished) clearInterval(pollingInterval);
    }
}
