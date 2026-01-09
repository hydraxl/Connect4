"""
Tests for Flask API endpoints.
"""

import pytest
import json
from app import app
from game import Connect4, Player


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def game_id():
    """Return a test game ID."""
    return 'test_game'


class TestIndexRoute:
    """Test the index route."""
    
    def test_index_route(self, client):
        """Test that index route returns HTML."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Connect 4' in response.data


class TestNewGameEndpoint:
    """Test the new game endpoint."""
    
    def test_create_new_game(self, client, game_id):
        """Test creating a new game."""
        response = client.post('/api/new_game',
                              json={'game_id': game_id},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] == True
        assert 'board' in data
        assert data['current_player'] == Player.RED.value
        assert data['game_over'] == False
        assert data['winner'] == Player.NONE.value
    
    def test_create_new_game_default_id(self, client):
        """Test creating a game with default ID."""
        response = client.post('/api/new_game',
                              json={},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_new_game_has_empty_board(self, client, game_id):
        """Test that new game has an empty board."""
        response = client.post('/api/new_game',
                              json={'game_id': game_id},
                              content_type='application/json')
        
        data = json.loads(response.data)
        board = data['board']
        
        assert all(cell == 0 for row in board for cell in row)


class TestMoveEndpoint:
    """Test the move endpoint."""
    
    def test_make_valid_move(self, client, game_id):
        """Test making a valid move."""
        # Create game
        client.post('/api/new_game',
                   json={'game_id': game_id},
                   content_type='application/json')
        
        # Make move
        response = client.post('/api/move',
                              json={'game_id': game_id, 'col': 0},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] == True
        assert 'board' in data
        assert data['current_player'] == Player.YELLOW.value
    
    def test_make_move_invalid_column(self, client, game_id):
        """Test making a move with invalid column."""
        client.post('/api/new_game',
                   json={'game_id': game_id},
                   content_type='application/json')
        
        response = client.post('/api/move',
                              json={'game_id': game_id, 'col': 10},
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_make_move_nonexistent_game(self, client):
        """Test making a move for nonexistent game."""
        response = client.post('/api/move',
                              json={'game_id': 'nonexistent', 'col': 0},
                              content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_make_move_full_column(self, client, game_id):
        """Test making a move in a full column."""
        client.post('/api/new_game',
                   json={'game_id': game_id},
                   content_type='application/json')
        
        # Fill column 0
        for _ in range(Connect4.ROWS):
            client.post('/api/move',
                       json={'game_id': game_id, 'col': 0},
                       content_type='application/json')
            client.post('/api/move',
                       json={'game_id': game_id, 'col': 1},
                       content_type='application/json')
        
        # Try to move in full column
        response = client.post('/api/move',
                              json={'game_id': game_id, 'col': 0},
                              content_type='application/json')
        
        assert response.status_code == 400


class TestBotMoveEndpoint:
    """Test the bot move endpoint."""
    
    def test_bot_makes_move(self, client, game_id):
        """Test that bot makes a move."""
        client.post('/api/new_game',
                   json={'game_id': game_id},
                   content_type='application/json')
        
        # Make player move
        client.post('/api/move',
                   json={'game_id': game_id, 'col': 0},
                   content_type='application/json')
        
        # Get bot move
        response = client.post('/api/bot_move',
                              json={'game_id': game_id},
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] == True
        assert 'col' in data
        assert 0 <= data['col'] < Connect4.COLS
    
    def test_bot_move_nonexistent_game(self, client):
        """Test bot move for nonexistent game."""
        response = client.post('/api/bot_move',
                              json={'game_id': 'nonexistent'},
                              content_type='application/json')
        
        assert response.status_code == 404
    
    def test_bot_move_when_not_bots_turn(self, client, game_id):
        """Test bot move when it's not bot's turn."""
        client.post('/api/new_game',
                   json={'game_id': game_id},
                   content_type='application/json')
        
        # It's RED's turn, bot is YELLOW
        response = client.post('/api/bot_move',
                              json={'game_id': game_id},
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_bot_move_when_game_over(self, client, game_id):
        """Test bot move when game is over."""
        client.post('/api/new_game',
                   json={'game_id': game_id},
                   content_type='application/json')
        
        # Create a win
        for i in range(4):
            client.post('/api/move',
                       json={'game_id': game_id, 'col': i},
                       content_type='application/json')
            if i < 3:
                client.post('/api/move',
                           json={'game_id': game_id, 'col': i},
                           content_type='application/json')
        
        response = client.post('/api/bot_move',
                              json={'game_id': game_id},
                              content_type='application/json')
        
        assert response.status_code == 400


class TestGameStateEndpoint:
    """Test the game state endpoint."""
    
    def test_get_game_state(self, client, game_id):
        """Test getting game state."""
        client.post('/api/new_game',
                   json={'game_id': game_id},
                   content_type='application/json')
        
        response = client.get(f'/api/game_state?game_id={game_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] == True
        assert 'board' in data
        assert 'current_player' in data
        assert 'game_over' in data
        assert 'winner' in data
    
    def test_get_game_state_nonexistent(self, client):
        """Test getting state for nonexistent game."""
        response = client.get('/api/game_state?game_id=nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_get_game_state_after_moves(self, client, game_id):
        """Test getting game state after moves."""
        client.post('/api/new_game',
                   json={'game_id': game_id},
                   content_type='application/json')
        
        client.post('/api/move',
                   json={'game_id': game_id, 'col': 0},
                   content_type='application/json')
        
        response = client.get(f'/api/game_state?game_id={game_id}')
        data = json.loads(response.data)
        
        assert data['current_player'] == Player.YELLOW.value
        board = data['board']
        assert board[Connect4.ROWS - 1][0] == Player.RED.value


class TestWinDetection:
    """Test win detection through API."""
    
    def test_horizontal_win_detected(self, client, game_id):
        """Test that horizontal win is detected."""
        client.post('/api/new_game',
                   json={'game_id': game_id},
                   content_type='application/json')
        
        # Create horizontal win
        for i in range(4):
            client.post('/api/move',
                       json={'game_id': game_id, 'col': i},
                       content_type='application/json')
            if i < 3:
                client.post('/api/move',
                           json={'game_id': game_id, 'col': i},
                           content_type='application/json')
        
        response = client.get(f'/api/game_state?game_id={game_id}')
        data = json.loads(response.data)
        
        assert data['game_over'] == True
        assert data['winner'] == Player.RED.value

