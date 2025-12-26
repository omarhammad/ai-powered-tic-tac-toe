let state = null;
let myRole = null;
let lastProcessedMoveCount = -1;
let isFetching = false;

// ---------------------------------------------------------
// INITIAL LOAD
// ---------------------------------------------------------
window.addEventListener("DOMContentLoaded", async () => {
    await loadSession();
    setInterval(loadSession, 1000);
});

// ---------------------------------------------------------
// LOAD SESSION
// ---------------------------------------------------------
async function loadSession() {
    if (isFetching) return;
    isFetching = true;

    try {
        const res = await fetch(`/sessions/${SESSION_ID}`);
        if (!res.ok) return;

        const snapshot = await res.json();
        applyState(snapshot);
    } finally {
        isFetching = false;
    }
}

// ---------------------------------------------------------
// APPLY STATE + AI HANDLING
// ---------------------------------------------------------
function applyState(snapshot) {
    if (!snapshot || !snapshot.board) return;

    const moveCount = countMoves(snapshot.board);

    // IMPORTANT FIX: merge instead of overwrite
    state = { ...state, ...snapshot };

    determineMyRole();
    renderUI();

    updateWinningProba();

    const isAITurn =
        (state.currentTurn === "X" && state.playerX?.isAI) ||
        (state.currentTurn === "O" && state.playerO?.isAI);

    if (isAITurn && moveCount === lastProcessedMoveCount) {
        triggerAIMove();
    }

    lastProcessedMoveCount = moveCount;
}

function countMoves(board) {
    return board.filter(v => v !== null).length;
}

// ---------------------------------------------------------
// DETERMINE HUMAN ROLE
// ---------------------------------------------------------
function determineMyRole() {
    if (!state?.playerX || !state?.playerO) {
        myRole = null;
        return;
    }

    const isX = PLAYER_ID === state.playerX.id;
    const isO = PLAYER_ID === state.playerO.id;

    if (!isX && !isO) {
        myRole = null;
        return;
    }

    if ((isX && state.playerX.isAI) || (isO && state.playerO.isAI)) {
        myRole = null;
        return;
    }

    myRole = isX ? "X" : "O";
}

// ---------------------------------------------------------
// AI MOVE TRIGGER
// ---------------------------------------------------------
async function triggerAIMove() {
    if (!state || state.isFinished) return;

    const turn = state.currentTurn;
    const aiPlayerId = turn === "X" ? state.playerX.id : state.playerO.id;

    try {
        const res = await fetch("/move", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                sessionId: SESSION_ID,
                playerId: aiPlayerId,
                moveIndex: -1
            })
        });

        if (res.ok) {
            const updated = await res.json();
            applyState(updated);
        }
    } catch (err) {
        console.error("[AI] Error:", err);
    }
}

// ---------------------------------------------------------
// RENDER UI
// ---------------------------------------------------------
function renderUI() {
    renderPlayers();
    renderInfoBanner();
    renderBoard();
}

function renderPlayers() {
    const sid = state.sessionId;
    document.getElementById("session-short").textContent =
        `${sid.slice(0, 6)}...${sid.slice(-3)}`;

    document.getElementById("player-x-name").textContent = state.playerX?.name || "?";
    document.getElementById("player-x-role").textContent =
        state.playerX?.isAI ? "(AI)" : "(Human)";

    document.getElementById("player-o-name").textContent = state.playerO?.name || "?";
    document.getElementById("player-o-role").textContent =
        state.playerO?.isAI ? "(AI)" : "(Human)";

    document.getElementById("you-badge").textContent =
        myRole ? `YOU ARE PLAYER ${myRole}` : "SPECTATOR";
}

function renderInfoBanner() {
    const banner = document.getElementById("info-banner");

    if (!myRole) {
        banner.textContent = "You are watching the game";
        banner.className = "info-banner info-spectator";
        return;
    }

    if (state.isFinished) {
        banner.textContent = state.winner
            ? `Winner: ${state.winner}`
            : "It's a draw!";
        banner.className = "info-banner info-winner";
        return;
    }

    if (state.currentTurn === myRole) {
        banner.textContent = "Your turn";
        banner.className = "info-banner info-your-turn";
    } else {
        banner.textContent = "Waiting for opponent...";
        banner.className = "info-banner info-opponent-turn";
    }
}

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

// ---------------------------------------------------------
// HUMAN MOVE
// ---------------------------------------------------------
async function tryMove(index) {
    if (state.isFinished) return;
    if (!myRole) return;
    if (state.currentTurn !== myRole) return;
    if (state.board[index] !== null) return;

    const res = await fetch("/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            sessionId: SESSION_ID,
            playerId: PLAYER_ID,
            moveIndex: index
        })
    });

    if (res.ok) {
        const updated = await res.json();
        applyState(updated);
    }
}

async function updateWinningProba() {
    if (!state) return;

    const movesPlayed = state.board.filter(v => v !== null).length;

    const xBar = document.getElementById("proba-x");
    const oBar = document.getElementById("proba-o");

    if (!xBar || !oBar) return;

    // Force 50 / 50 at game start
    if (movesPlayed === 0) {
        xBar.style.width = "50%";
        oBar.style.width = "50%";
        return;
    }

    try {
        const res = await fetch(`/session/${SESSION_ID}/winning-proba`);
        if (!res.ok) return;

        const data = await res.json();

        const x = data.x;
        const o = data.o;

        const total = x + o;
        if (total <= 0) return;

        const xPct = Math.round((x / total) * 100);
        const oPct = 100 - xPct;

        xBar.style.width = `${xPct}%`;
        oBar.style.width = `${oPct}%`;
    } catch (_) {}
}
