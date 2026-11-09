// Eight lines that decide a winner: three rows, three columns, two diagonals.
const WIN_LINES = [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8],
  [2, 4, 6],
];

const CELL_LABELS = [
  "Row 1, column 1",
  "Row 1, column 2",
  "Row 1, column 3",
  "Row 2, column 1",
  "Row 2, column 2",
  "Row 2, column 3",
  "Row 3, column 1",
  "Row 3, column 2",
  "Row 3, column 3",
];

const COMPUTER_DELAY_MS = 550;

const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const restartEl = document.getElementById("restart");
const difficultyEl = document.getElementById("difficulty");
const modeLabelEl = document.getElementById("mode-label");
const scoreXEl = document.getElementById("score-x");
const scoreOEl = document.getElementById("score-o");
const scoreXLabelEl = document.getElementById("score-x-label");
const scoreOLabelEl = document.getElementById("score-o-label");
const scoreDrawsEl = document.getElementById("score-draws");
const modeButtons = [...document.querySelectorAll("[data-mode]")];
const difficultyButtons = [...document.querySelectorAll("[data-difficulty]")];
const cells = [...boardEl.querySelectorAll(".cell")];

// board holds null, "X", or "O". Scores survive Restart until the page reloads.
const state = {
  board: Array(9).fill(null),
  currentPlayer: "X",
  gameOver: false,
  winningLine: [],
  scores: { X: 0, O: 0, draws: 0 },
  mode: "pvp",
  difficulty: "easy",
  computerThinking: false,
};

// Bumped on restart or mode change so a pending computer move cannot land late.
let moveToken = 0;
let computerTimer = null;

function winningLine(board) {
  return (
    WIN_LINES.find(([a, b, c]) => {
      return board[a] && board[a] === board[b] && board[a] === board[c];
    }) || []
  );
}

function isBoardFull(board) {
  return board.every((cell) => cell !== null);
}

function emptyIndexes(board) {
  const indexes = [];
  board.forEach((cell, index) => {
    if (cell === null) {
      indexes.push(index);
    }
  });
  return indexes;
}

function isComputerTurn() {
  return state.mode === "pvc" && state.currentPlayer === "O" && !state.gameOver;
}

function randomEmpty(board) {
  const open = emptyIndexes(board);
  return open[Math.floor(Math.random() * open.length)];
}

// Look one move ahead for an immediate win for the given mark.
function findWinningMove(board, player) {
  for (const index of emptyIndexes(board)) {
    const next = board.slice();
    next[index] = player;
    if (winningLine(next).length > 0) {
      return index;
    }
  }
  return null;
}

function chooseMediumMove(board) {
  return findWinningMove(board, "O") ?? findWinningMove(board, "X") ?? randomEmpty(board);
}

// Minimax scores a finished board for the computer (O).
// A faster win scores higher than a slower one. A faster loss scores worse.
function terminalScore(board, depth) {
  const line = winningLine(board);
  if (line.length > 0) {
    return board[line[0]] === "O" ? 10 - depth : depth - 10;
  }
  if (isBoardFull(board)) {
    return 0;
  }
  return null;
}

function minimax(board, isMaximizing, depth) {
  const score = terminalScore(board, depth);
  if (score !== null) {
    return score;
  }

  const player = isMaximizing ? "O" : "X";
  let best = isMaximizing ? -Infinity : Infinity;

  for (const index of emptyIndexes(board)) {
    const next = board.slice();
    next[index] = player;
    const nextScore = minimax(next, !isMaximizing, depth + 1);
    best = isMaximizing ? Math.max(best, nextScore) : Math.min(best, nextScore);
  }

  return best;
}

function chooseHardMove(board) {
  let bestScore = -Infinity;
  let bestIndex = emptyIndexes(board)[0];

  for (const index of emptyIndexes(board)) {
    const next = board.slice();
    next[index] = "O";
    const score = minimax(next, false, 1);
    if (score > bestScore) {
      bestScore = score;
      bestIndex = index;
    }
  }

  return bestIndex;
}

function chooseComputerMove(board) {
  if (state.difficulty === "easy") {
    return randomEmpty(board);
  }
  if (state.difficulty === "medium") {
    return chooseMediumMove(board);
  }
  return chooseHardMove(board);
}

function cancelComputerMove() {
  moveToken += 1;
  clearTimeout(computerTimer);
  computerTimer = null;
  state.computerThinking = false;
}

function scheduleComputerMove() {
  const token = ++moveToken;
  state.computerThinking = true;
  render();

  computerTimer = setTimeout(() => {
    if (token !== moveToken) {
      return;
    }

    computerTimer = null;
    state.computerThinking = false;

    if (!isComputerTurn()) {
      render();
      return;
    }

    playMove(chooseComputerMove(state.board));
  }, COMPUTER_DELAY_MS);
}

function playMove(index) {
  if (state.gameOver || state.computerThinking || state.board[index] !== null) {
    return;
  }

  state.board[index] = state.currentPlayer;
  const line = winningLine(state.board);

  if (line.length > 0) {
    state.gameOver = true;
    state.winningLine = line;
    state.scores[state.currentPlayer] += 1;
  } else if (isBoardFull(state.board)) {
    state.gameOver = true;
    state.scores.draws += 1;
  } else {
    state.currentPlayer = state.currentPlayer === "X" ? "O" : "X";
  }

  render();

  if (isComputerTurn()) {
    scheduleComputerMove();
  }
}

function restartGame() {
  cancelComputerMove();
  state.board = Array(9).fill(null);
  state.currentPlayer = "X";
  state.gameOver = false;
  state.winningLine = [];
  render();
}

function setMode(mode) {
  if (mode === state.mode) {
    return;
  }
  state.mode = mode;
  restartGame();
}

function setDifficulty(difficulty) {
  state.difficulty = difficulty;
  render();
}

function statusMessage() {
  const vsComputer = state.mode === "pvc";

  if (!state.gameOver) {
    if (vsComputer) {
      return state.currentPlayer === "X" && !state.computerThinking
        ? "Your turn"
        : "Computer's turn";
    }
    return `Player ${state.currentPlayer}'s turn`;
  }

  if (state.winningLine.length > 0) {
    if (vsComputer) {
      return state.currentPlayer === "X" ? "You win" : "Computer wins";
    }
    return `Player ${state.currentPlayer} wins`;
  }

  return "It's a draw";
}

function render() {
  const vsComputer = state.mode === "pvc";
  const computerLock = vsComputer && (state.computerThinking || state.currentPlayer === "O");

  cells.forEach((cell, index) => {
    const mark = state.board[index];
    const locked = state.gameOver || computerLock || mark !== null;

    cell.textContent = mark || "";
    cell.classList.toggle("x", mark === "X");
    cell.classList.toggle("o", mark === "O");
    cell.classList.toggle("winning", state.winningLine.includes(index));
    cell.disabled = locked;
    cell.setAttribute(
      "aria-label",
      mark ? `${CELL_LABELS[index]}, ${mark}` : CELL_LABELS[index]
    );
  });

  boardEl.setAttribute("aria-busy", String(state.computerThinking));
  statusEl.textContent = statusMessage();
  statusEl.classList.toggle("win", state.winningLine.length > 0);
  statusEl.classList.toggle("draw", state.gameOver && state.winningLine.length === 0);

  scoreXEl.textContent = String(state.scores.X);
  scoreOEl.textContent = String(state.scores.O);
  scoreDrawsEl.textContent = String(state.scores.draws);
  scoreXLabelEl.textContent = vsComputer ? "Your wins" : "X wins";
  scoreOLabelEl.textContent = vsComputer ? "Computer wins" : "O wins";
  modeLabelEl.textContent = vsComputer ? "Player vs computer" : "Player vs player";
  difficultyEl.hidden = !vsComputer;

  modeButtons.forEach((button) => {
    const selected = button.dataset.mode === state.mode;
    button.classList.toggle("is-selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });

  difficultyButtons.forEach((button) => {
    const selected = button.dataset.difficulty === state.difficulty;
    button.classList.toggle("is-selected", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
}

boardEl.addEventListener("click", (event) => {
  const cell = event.target.closest(".cell");
  if (!cell || state.computerThinking) {
    return;
  }
  if (state.mode === "pvc" && state.currentPlayer !== "X") {
    return;
  }

  playMove(Number(cell.dataset.index));
});

modeButtons.forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

difficultyButtons.forEach((button) => {
  button.addEventListener("click", () => setDifficulty(button.dataset.difficulty));
});

restartEl.addEventListener("click", restartGame);

render();
