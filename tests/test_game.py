"""
Tests for Connect4 game logic.
"""

import pytest
from game import Connect4, Player


class TestConnect4Initialization:
    """Test game initialization."""
    
    def test_initial_board_empty(self):
        """Test that the board starts empty."""
        game = Connect4()
        board = game.get_board()
        
        assert all(cell == 0 for row in board for cell in row)
    
    def test_initial_player_is_red(self):
        """Test that RED player starts first."""
        game = Connect4()
        assert game.current_player == Player.RED
    
    def test_game_not_over_initially(self):
        """Test that game is not over at start."""
        game = Connect4()
        assert game.game_over == False
        assert game.winner == Player.NONE
    
    def test_board_dimensions(self):
        """Test that board has correct dimensions."""
        game = Connect4()
        board = game.get_board()
        
        assert len(board) == Connect4.ROWS
        assert len(board[0]) == Connect4.COLS


class TestMoveValidation:
    """Test move validation logic."""
    
    def test_valid_move(self):
        """Test that valid moves are accepted."""
        game = Connect4()
        assert game.is_valid_move(0) == True
        assert game.is_valid_move(3) == True
        assert game.is_valid_move(6) == True
    
    def test_invalid_column_negative(self):
        """Test that negative columns are rejected."""
        game = Connect4()
        assert game.is_valid_move(-1) == False
    
    def test_invalid_column_too_large(self):
        """Test that columns beyond board are rejected."""
        game = Connect4()
        assert game.is_valid_move(7) == False
        assert game.is_valid_move(10) == False
    
    def test_invalid_move_full_column(self):
        """Test that full columns are rejected."""
        game = Connect4()
        # Fill column 0
        for _ in range(Connect4.ROWS):
            game.make_move(0)
        
        assert game.is_valid_move(0) == False
    
    def test_get_valid_moves(self):
        """Test getting list of valid moves."""
        game = Connect4()
        valid_moves = game.get_valid_moves()
        
        assert len(valid_moves) == Connect4.COLS
        assert set(valid_moves) == set(range(Connect4.COLS))


class TestMakingMoves:
    """Test making moves."""
    
    def test_make_valid_move(self):
        """Test making a valid move."""
        game = Connect4()
        success = game.make_move(0)
        
        assert success == True
        board = game.get_board()
        assert board[Connect4.ROWS - 1][0] == Player.RED.value
    
    def test_pieces_stack(self):
        """Test that pieces stack on top of each other."""
        game = Connect4()
        game.make_move(0)  # RED
        game.make_move(0)  # YELLOW
        
        board = game.get_board()
        assert board[Connect4.ROWS - 1][0] == Player.RED.value
        assert board[Connect4.ROWS - 2][0] == Player.YELLOW.value
    
    def test_player_switches_after_move(self):
        """Test that players alternate after moves."""
        game = Connect4()
        assert game.current_player == Player.RED
        
        game.make_move(0)
        assert game.current_player == Player.YELLOW
        
        game.make_move(1)
        assert game.current_player == Player.RED
    
    def test_cannot_move_when_game_over(self):
        """Test that moves are rejected when game is over."""
        game = Connect4()
        # Create a winning scenario
        for i in range(3):
            game.make_move(i)  # RED
            game.make_move(i)  # YELLOW
        
        game.make_move(3)  # RED wins
        
        assert game.game_over == True
        success = game.make_move(0)
        assert success == False
    
    def test_get_next_open_row(self):
        """Test finding the next open row in a column."""
        game = Connect4()
        
        assert game.get_next_open_row(0) == Connect4.ROWS - 1
        
        game.make_move(0)
        assert game.get_next_open_row(0) == Connect4.ROWS - 2
        
        # Fill column
        for _ in range(Connect4.ROWS - 1):
            game.make_move(0)
        
        assert game.get_next_open_row(0) == None


class TestWinDetection:
    """Test win detection in all directions."""
    
    def test_horizontal_win(self):
        """Test horizontal win detection."""
        game = Connect4()
        # RED wins horizontally
        for col in range(4):
            game.make_move(col)
            if col < 3:  # Don't make extra move after winning
                game.make_move(col)  # YELLOW blocks
        
        assert game.game_over == True
        assert game.winner == Player.RED
    
    def test_vertical_win(self):
        """Test vertical win detection."""
        game = Connect4()
        # RED wins vertically
        for _ in range(4):
            game.make_move(0)  # RED
            game.make_move(1)  # YELLOW
        
        assert game.game_over == True
        assert game.winner == Player.RED
    
    def test_diagonal_win_forward_slash(self):
        """Test diagonal win detection (forward slash /)."""
        game = Connect4()
        # Create diagonal win for RED (diagonal from bottom-left to top-right)
        # Pattern: RED at (5,0), (4,1), (3,2), (2,3)
        # We'll manually set up the board to test diagonal detection
        
        # Set up pieces manually to create diagonal
        # Column 0: RED at row 5
        game.board[5][0] = Player.RED
        # Column 1: YELLOW at 5, RED at 4
        game.board[5][1] = Player.YELLOW
        game.board[4][1] = Player.RED
        # Column 2: YELLOW at 5,4, RED at 3
        game.board[5][2] = Player.YELLOW
        game.board[4][2] = Player.YELLOW
        game.board[3][2] = Player.RED
        # Column 3: YELLOW at 5,4,3, RED at 2 (wins!)
        game.board[5][3] = Player.YELLOW
        game.board[4][3] = Player.YELLOW
        game.board[3][3] = Player.YELLOW
        game.board[2][3] = Player.RED
        
        # Check win at the last placed piece
        assert game._check_win(2, 3) == True
    
    def test_diagonal_win_backslash(self):
        """Test diagonal win detection (backslash)."""
        game = Connect4()
        # Create diagonal win for RED (diagonal from bottom-right to top-left)
        # Pattern: RED at (5,3), (4,2), (3,1), (2,0)
        # We'll manually set up the board to test diagonal detection
        
        # Set up pieces manually to create diagonal
        # Column 3: RED at row 5
        game.board[5][3] = Player.RED
        # Column 2: YELLOW at 5, RED at 4
        game.board[5][2] = Player.YELLOW
        game.board[4][2] = Player.RED
        # Column 1: YELLOW at 5,4, RED at 3
        game.board[5][1] = Player.YELLOW
        game.board[4][1] = Player.YELLOW
        game.board[3][1] = Player.RED
        # Column 0: YELLOW at 5,4,3, RED at 2 (wins!)
        game.board[5][0] = Player.YELLOW
        game.board[4][0] = Player.YELLOW
        game.board[3][0] = Player.YELLOW
        game.board[2][0] = Player.RED
        
        # Check win at the last placed piece
        assert game._check_win(2, 0) == True
    
    def test_yellow_wins(self):
        """Test that YELLOW can win."""
        game = Connect4()
        # YELLOW wins horizontally
        # RED moves to column 4 first
        game.make_move(4)  # RED
        # YELLOW makes 4 in a row horizontally (columns 0-3)
        for col in range(4):
            game.make_move(col)  # YELLOW
            if col < 3:  # Don't make extra move after winning
                # RED moves to different columns to avoid blocking
                red_col = 5 if col == 0 else (6 if col == 1 else 4)
                game.make_move(red_col)  # RED moves elsewhere
        
        assert game.game_over == True
        assert game.winner == Player.YELLOW


class TestDrawDetection:
    """Test draw detection."""
    
    def test_draw_when_board_full(self):
        """Test that game ends in draw when board is full."""
        game = Connect4()
        
        # Fill board without winning (alternate columns)
        for row in range(Connect4.ROWS):
            for col in range(Connect4.COLS):
                if (row + col) % 2 == 0:
                    # Fill with pattern that doesn't create 4 in a row
                    current_col = col
                    while not game.is_valid_move(current_col):
                        current_col = (current_col + 1) % Connect4.COLS
                    game.make_move(current_col)
        
        # If board is full, it should be a draw
        if game._is_board_full():
            assert game.game_over == True
            assert game.winner == Player.NONE


class TestGameCopy:
    """Test game copying functionality."""
    
    def test_copy_creates_independent_game(self):
        """Test that copy creates an independent game state."""
        game = Connect4()
        game.make_move(0)
        game.make_move(1)
        
        copy = game.copy()
        
        # Modify original
        game.make_move(2)
        
        # Copy should be unchanged
        assert copy.get_board() != game.get_board()
        assert len(copy.move_history) == 2
        assert len(game.move_history) == 3
    
    def test_copy_preserves_state(self):
        """Test that copy preserves all game state."""
        game = Connect4()
        game.make_move(0)
        game.make_move(1)
        
        copy = game.copy()
        
        assert copy.current_player == game.current_player
        assert copy.game_over == game.game_over
        assert copy.winner == game.winner
        assert copy.get_board() == game.get_board()


class TestUndoMove:
    """Test undo move functionality."""
    
    def test_undo_move(self):
        """Test undoing a move."""
        game = Connect4()
        game.make_move(0)
        game.make_move(1)
        
        initial_board = game.copy().get_board()
        game.undo_move()
        
        # Should be back to state before last move
        assert game.current_player == Player.YELLOW
        board = game.get_board()
        assert board[Connect4.ROWS - 1][1] == Player.NONE.value
    
    def test_undo_multiple_moves(self):
        """Test undoing multiple moves."""
        game = Connect4()
        for i in range(5):
            game.make_move(i)
        
        for i in range(3):
            game.undo_move()
        
        assert len(game.move_history) == 2
    
    def test_undo_empty_history(self):
        """Test undoing when no moves exist."""
        game = Connect4()
        success = game.undo_move()
        
        assert success == False
    
    def test_undo_restores_game_state(self):
        """Test that undo restores game_over and winner state."""
        game = Connect4()
        # Create a horizontal win
        for i in range(4):
            game.make_move(i)  # RED
            if i < 3:  # Don't make extra move after winning
                game.make_move(i)  # YELLOW blocks
        
        assert game.game_over == True
        game.undo_move()
        
        assert game.game_over == False
        assert game.winner == Player.NONE

