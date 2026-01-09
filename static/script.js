// Game state
let gameId = 'default';
let board = [];
let currentPlayer = 1; // 1 = RED, 2 = YELLOW
let gameOver = false;
let winner = 0;

const ROWS = 6;
const COLS = 7;

// Initialize game
document.addEventListener('DOMContentLoaded', () => {
    createBoard();
    newGame();
    
    document.getElementById('new-game-btn').addEventListener('click', newGame);
});

function createBoard() {
    const boardElement = document.getElementById('board');
    boardElement.innerHTML = '';
    
    for (let row = 0; row < ROWS; row++) {
        for (let col = 0; col < COLS; col++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            cell.addEventListener('click', () => handleCellClick(col));
            boardElement.appendChild(cell);
        }
    }
}

function handleCellClick(col) {
    if (gameOver || currentPlayer !== 1) {
        return;
    }
    
    makeMove(col);
}

async function newGame() {
    try {
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ game_id: gameId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            board = data.board;
            currentPlayer = data.current_player;
            gameOver = data.game_over;
            winner = data.winner;
            updateDisplay();
        }
    } catch (error) {
        console.error('Error starting new game:', error);
        alert('Failed to start new game');
    }
}

async function makeMove(col) {
    if (gameOver || currentPlayer !== 1) {
        return;
    }
    
    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameId,
                col: col
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            board = data.board;
            currentPlayer = data.current_player;
            gameOver = data.game_over;
            winner = data.winner;
            updateDisplay();
            
            // If game is not over and it's bot's turn, make bot move
            if (!gameOver && currentPlayer === 2) {
                setTimeout(() => makeBotMove(), 500);
            }
        } else {
            alert(data.error || 'Invalid move');
        }
    } catch (error) {
        console.error('Error making move:', error);
        alert('Failed to make move');
    }
}

async function makeBotMove() {
    if (gameOver || currentPlayer !== 2) {
        return;
    }
    
    try {
        const response = await fetch('/api/bot_move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            board = data.board;
            currentPlayer = data.current_player;
            gameOver = data.game_over;
            winner = data.winner;
            updateDisplay();
        } else {
            console.error('Bot move error:', data.error);
        }
    } catch (error) {
        console.error('Error making bot move:', error);
    }
}

function updateDisplay() {
    // Update board
    const cells = document.querySelectorAll('.cell');
    cells.forEach((cell, index) => {
        const row = Math.floor(index / COLS);
        const col = index % COLS;
        const value = board[row][col];
        
        cell.className = 'cell';
        
        if (value === 1) {
            cell.classList.add('red');
        } else if (value === 2) {
            cell.classList.add('yellow');
        }
        
        if (gameOver) {
            cell.classList.add('disabled');
        }
    });
    
    // Update status
    const statusElement = document.getElementById('status');
    statusElement.className = 'status';
    
    if (gameOver) {
        if (winner === 1) {
            statusElement.textContent = 'Player 1 (Red) Wins!';
            statusElement.classList.add('winner');
        } else if (winner === 2) {
            statusElement.textContent = 'Player 2 (Yellow) Wins!';
            statusElement.classList.add('winner');
        } else {
            statusElement.textContent = 'Draw!';
            statusElement.classList.add('draw');
        }
    } else {
        if (currentPlayer === 1) {
            statusElement.textContent = 'Player 1\'s Turn (Red)';
            statusElement.classList.add('player1');
        } else {
            statusElement.textContent = 'Player 2\'s Turn (Yellow) - Thinking...';
            statusElement.classList.add('player2');
        }
    }
}

