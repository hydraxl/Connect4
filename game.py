"""
Internal representation for Connect 4 game logic.
"""

from enum import Enum
from typing import Optional, List, Tuple


class Player(Enum):
    """Represents the two players in the game."""
    RED = 1
    YELLOW = 2
    NONE = 0


class Connect4:
    """
    Internal representation of a Connect 4 game.
    
    Standard Connect 4 board is 6 rows x 7 columns.
    Players take turns dropping pieces into columns.
    First to get 4 in a row (horizontal, vertical, or diagonal) wins.
    """
    
    ROWS = 6
    COLS = 7
    WIN_LENGTH = 4
    
    def __init__(self):
        """Initialize an empty Connect 4 board."""
        self.board = [[Player.NONE for _ in range(self.COLS)] 
                      for _ in range(self.ROWS)]
        self.current_player = Player.RED
        self.game_over = False
        self.winner = Player.NONE
        self.move_history = []
    
    def get_board(self) -> List[List[int]]:
        """
        Get the current board state as a 2D list of integers.
        Returns: 2D list where 0 = empty, 1 = RED, 2 = YELLOW
        """
        return [[cell.value for cell in row] for row in self.board]
    
    def is_valid_move(self, col: int) -> bool:
        """
        Check if a move is valid (column exists and is not full).
        
        Args:
            col: Column index (0-6)
            
        Returns:
            True if the move is valid, False otherwise
        """
        if col < 0 or col >= self.COLS:
            return False
        return self.board[0][col] == Player.NONE
    
    def get_next_open_row(self, col: int) -> Optional[int]:
        """
        Get the next open row in a column.
        
        Args:
            col: Column index
            
        Returns:
            Row index if column has space, None otherwise
        """
        if not self.is_valid_move(col):
            return None
        
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][col] == Player.NONE:
                return row
        return None
    
    def make_move(self, col: int) -> bool:
        """
        Make a move in the specified column.
        
        Args:
            col: Column index (0-6)
            
        Returns:
            True if move was successful, False otherwise
        """
        if self.game_over:
            return False
        
        if not self.is_valid_move(col):
            return False
        
        row = self.get_next_open_row(col)
        if row is None:
            return False
        
        self.board[row][col] = self.current_player
        self.move_history.append((row, col, self.current_player))
        
        # Check for win
        if self._check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        # Check for draw
        elif self._is_board_full():
            self.game_over = True
            self.winner = Player.NONE
        else:
            # Switch players
            self.current_player = Player.YELLOW if self.current_player == Player.RED else Player.RED
        
        return True
    
    def _check_win(self, row: int, col: int) -> bool:
        """
        Check if the last move resulted in a win.
        
        Args:
            row: Row of the last move
            col: Column of the last move
            
        Returns:
            True if this move wins the game
        """
        player = self.board[row][col]
        
        # Check horizontal, vertical, and both diagonals
        directions = [
            (0, 1),   # horizontal
            (1, 0),   # vertical
            (1, 1),   # diagonal /
            (1, -1)   # diagonal \
        ]
        
        for dr, dc in directions:
            count = 1  # Count the current piece
            
            # Check positive direction
            for i in range(1, self.WIN_LENGTH):
                r, c = row + dr * i, col + dc * i
                if (0 <= r < self.ROWS and 0 <= c < self.COLS and 
                    self.board[r][c] == player):
                    count += 1
                else:
                    break
            
            # Check negative direction
            for i in range(1, self.WIN_LENGTH):
                r, c = row - dr * i, col - dc * i
                if (0 <= r < self.ROWS and 0 <= c < self.COLS and 
                    self.board[r][c] == player):
                    count += 1
                else:
                    break
            
            if count >= self.WIN_LENGTH:
                return True
        
        return False
    
    def _is_board_full(self) -> bool:
        """Check if the board is full (draw condition)."""
        return all(self.board[0][col] != Player.NONE for col in range(self.COLS))
    
    def get_valid_moves(self) -> List[int]:
        """Get a list of all valid column moves."""
        return [col for col in range(self.COLS) if self.is_valid_move(col)]
    
    def copy(self) -> 'Connect4':
        """Create a deep copy of the game state."""
        new_game = Connect4()
        new_game.board = [row[:] for row in self.board]
        new_game.current_player = self.current_player
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.move_history = self.move_history[:]
        return new_game
    
    def undo_move(self) -> bool:
        """
        Undo the last move (useful for bot evaluation).
        
        Returns:
            True if undo was successful, False otherwise
        """
        if not self.move_history:
            return False
        
        row, col, player = self.move_history.pop()
        self.board[row][col] = Player.NONE
        
        # Reset game state
        self.game_over = False
        self.winner = Player.NONE
        self.current_player = player
        
        return True

