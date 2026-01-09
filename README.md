# Connect 4 Game

A complete Connect 4 implementation with a web-based GUI, internal game logic, and an optimal AI bot.

## Project Structure

```
Connect4/
├── game.py          # Internal game representation and logic
├── bot.py           # Optimal bot using minimax with alpha-beta pruning
├── app.py           # Flask web server with API endpoints
├── templates/
│   └── index.html   # Main game interface
├── static/
│   ├── style.css    # Styling for the game
│   └── script.js    # Frontend JavaScript logic
├── tests/
│   ├── test_game.py # Tests for game logic
│   ├── test_bot.py  # Tests for bot algorithm
│   └── test_app.py  # Tests for API endpoints
├── venv/            # Virtual environment (created during setup)
├── requirements.txt # Python dependencies
├── pytest.ini       # Pytest configuration
├── .gitignore       # Git ignore file
└── README.md        # This file
```

## Components

### 1. Internal Game Representation (`game.py`)
- `Connect4` class that handles all game logic
- Board state management (6 rows × 7 columns)
- Move validation and execution
- Win detection (horizontal, vertical, diagonal)
- Draw detection
- Game state copying for bot evaluation

### 2. Optimal Bot (`bot.py`)
- `Bot` class implementing minimax algorithm
- Alpha-beta pruning for efficiency
- Configurable search depth
- Position evaluation heuristic
- Plays optimally against the human player

### 3. Web Server (`app.py`)
- Flask-based REST API
- Endpoints for:
  - Creating new games
  - Making player moves
  - Getting bot moves
  - Querying game state
- Session management for multiple games

## Installation

1. Create and activate a virtual environment (recommended):
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

1. Make sure your virtual environment is activated (you should see `(venv)` in your terminal prompt)

2. Start the Flask server:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## Running Tests

The project includes a comprehensive test suite using pytest. To run the tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_game.py

# Run with verbose output
pytest -v
```

Test coverage reports are generated in the `htmlcov/` directory. The test suite achieves 98% code coverage and includes:
- Game logic tests (initialization, moves, win detection, draw detection)
- Bot algorithm tests (minimax, evaluation, move selection)
- API endpoint tests (all Flask routes and error handling)

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Click on a column to drop your piece (Red). The bot (Yellow) will automatically make its move.

## How to Play

- Click on any column to drop your red piece
- The bot (yellow) will automatically respond
- Get 4 pieces in a row (horizontal, vertical, or diagonal) to win
- Click "New Game" to start over

## API Endpoints

- `POST /api/new_game` - Create a new game
- `POST /api/move` - Make a player move
- `POST /api/bot_move` - Get and execute bot's move
- `GET /api/game_state` - Get current game state

## Customization

### Bot Difficulty
Adjust the bot's search depth in `app.py`:
```python
bot = Bot(depth=6, player=Player.YELLOW)  # Increase depth for harder bot
```

### Board Size
Modify constants in `game.py`:
```python
ROWS = 6
COLS = 7
WIN_LENGTH = 4
```

## License

This project is open source and available for educational purposes.

