"""
Optimal Connect 4 bot using minimax algorithm with alpha-beta pruning.
"""

from typing import Optional, Tuple
from game import Connect4, Player


class Bot:
    """
    Optimal Connect 4 bot that uses minimax with alpha-beta pruning.
    """
    
    def __init__(self, depth: int = 6, player: Player = Player.YELLOW):
        """
        Initialize the bot.
        
        Args:
            depth: Maximum depth for minimax search (default: 6)
            player: Which player the bot represents (default: YELLOW)
        """
        self.depth = depth
        self.player = player
        self.opponent = Player.RED if player == Player.YELLOW else Player.YELLOW
    
    def get_best_move(self, game: Connect4) -> Optional[int]:
        """
        Get the best move for the bot given the current game state.
        
        Args:
            game: Current Connect4 game instance
            
        Returns:
            Column index of the best move, or None if no valid moves
        """
        if game.game_over:
            return None
        
        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None
        
        best_move = None
        best_value = float('-inf')
        
        for move in valid_moves:
            # Make the move
            game.make_move(move)
            
            # Evaluate the position
            value = self._minimax(game, self.depth - 1, False, 
                                 float('-inf'), float('inf'))
            
            # Undo the move
            game.undo_move()
            
            if value > best_value:
                best_value = value
                best_move = move
        
        return best_move
    
    def _minimax(self, game: Connect4, depth: int, maximizing: bool, 
                 alpha: float, beta: float) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            game: Current game state
            depth: Remaining search depth
            maximizing: True if maximizing (bot's turn), False if minimizing
            alpha: Best value for maximizing player
            beta: Best value for minimizing player
            
        Returns:
            Evaluation score of the position
        """
        # Terminal conditions
        if game.game_over:
            if game.winner == self.player:
                return 1000 + depth  # Prefer faster wins
            elif game.winner == self.opponent:
                return -1000 - depth  # Prefer slower losses
            else:
                return 0  # Draw
        
        if depth == 0:
            return self._evaluate_position(game)
        
        valid_moves = game.get_valid_moves()
        
        if maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                game.make_move(move)
                eval_score = self._minimax(game, depth - 1, False, alpha, beta)
                game.undo_move()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                game.make_move(move)
                eval_score = self._minimax(game, depth - 1, True, alpha, beta)
                game.undo_move()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return min_eval
    
    def _evaluate_position(self, game: Connect4) -> float:
        """
        Evaluate a position without terminal conditions.
        Heuristic: count potential winning lines for each player.
        
        Args:
            game: Game state to evaluate
            
        Returns:
            Evaluation score (positive favors bot, negative favors opponent)
        """
        score = 0
        
        # Evaluate all possible 4-in-a-row lines
        for row in range(game.ROWS):
            for col in range(game.COLS):
                # Check horizontal
                if col <= game.COLS - game.WIN_LENGTH:
                    score += self._evaluate_line(game, row, col, 0, 1)
                # Check vertical
                if row <= game.ROWS - game.WIN_LENGTH:
                    score += self._evaluate_line(game, row, col, 1, 0)
                # Check diagonal /
                if row <= game.ROWS - game.WIN_LENGTH and col <= game.COLS - game.WIN_LENGTH:
                    score += self._evaluate_line(game, row, col, 1, 1)
                # Check diagonal \
                if row <= game.ROWS - game.WIN_LENGTH and col >= game.WIN_LENGTH - 1:
                    score += self._evaluate_line(game, row, col, 1, -1)
        
        return score
    
    def _evaluate_line(self, game: Connect4, row: int, col: int, 
                      dr: int, dc: int) -> float:
        """
        Evaluate a potential 4-in-a-row line.
        
        Args:
            game: Game state
            row: Starting row
            col: Starting column
            dr: Row direction
            dc: Column direction
            
        Returns:
            Score contribution from this line
        """
        bot_count = 0
        opponent_count = 0
        empty_count = 0
        
        for i in range(game.WIN_LENGTH):
            r = row + dr * i
            c = col + dc * i
            cell = game.board[r][c]
            
            if cell == self.player:
                bot_count += 1
            elif cell == self.opponent:
                opponent_count += 1
            else:
                empty_count += 1
        
        # Score based on potential
        if bot_count > 0 and opponent_count == 0:
            # Bot has pieces here, score based on count
            return 10 ** bot_count
        elif opponent_count > 0 and bot_count == 0:
            # Opponent has pieces here, negative score
            return -(10 ** opponent_count)
        else:
            # Mixed or empty, neutral
            return 0

