"""
Optimal Connect 4 bot using minimax algorithm with alpha-beta pruning.
"""

import random
from typing import Optional, Tuple, Dict
from enum import Enum
from game import Connect4, Player


class BoundType(Enum):
    """Type of bound stored in transposition table."""
    EXACT = 0
    LOWER_BOUND = 1
    UPPER_BOUND = 2


class TranspositionEntry:
    """Entry in the transposition table."""
    def __init__(self, score: float, depth: int, bound: BoundType, best_move: Optional[int] = None):
        self.score = score
        self.depth = depth
        self.bound = bound
        self.best_move = best_move


class Bot:
    """
    Optimal Connect 4 bot that uses minimax with alpha-beta pruning.
    """
    
    def __init__(self, depth: int = 6, player: Player = Player.YELLOW, 
                 search_type: str = "iterative"):
        """
        Initialize the bot.
        
        Args:
            depth: Maximum depth for minimax search (default: 6)
            player: Which player the bot represents (default: YELLOW)
            search_type: Type of search to use - "iterative" or "fixed" (default: "iterative")
        """
        self.depth = depth
        self.player = player
        self.opponent = Player.RED if player == Player.YELLOW else Player.YELLOW
        self.search_type = search_type
        
        if search_type not in ["iterative", "fixed"]:
            raise ValueError("search_type must be 'iterative' or 'fixed'")
        
        # Initialize Zobrist hashing table
        self.zobrist_table = self._init_zobrist_table()
        
        # Initialize transposition table
        self.transposition_table: Dict[int, TranspositionEntry] = {}
        
        # Player hash key (to distinguish positions with same board but different current player)
        self.player_key = random.getrandbits(64)
        
        # Cache for valid moves (keyed by position hash)
        self.valid_moves_cache: Dict[int, list] = {}
        
        # Cache for evaluation scores (keyed by position hash)
        self.evaluation_cache: Dict[int, float] = {}
    
    def _init_zobrist_table(self) -> list:
        """
        Initialize Zobrist hash table with random 64-bit integers.
        
        Returns:
            3D list: zobrist_table[row][col][player_index]
        """
        table = []
        for row in range(Connect4.ROWS):
            table_row = []
            for col in range(Connect4.COLS):
                # 3 players: NONE (0), RED (1), YELLOW (2)
                table_row.append([
                    random.getrandbits(64),
                    random.getrandbits(64),
                    random.getrandbits(64)
                ])
            table.append(table_row)
        return table
    
    def _compute_hash(self, game: Connect4) -> int:
        """
        Compute Zobrist hash for the current board position.
        
        Args:
            game: Current game state
            
        Returns:
            64-bit hash value
        """
        hash_value = 0
        
        # XOR all pieces on the board
        for row in range(Connect4.ROWS):
            for col in range(Connect4.COLS):
                player = game.board[row][col]
                player_index = player.value
                hash_value ^= self.zobrist_table[row][col][player_index]
        
        # Include current player in hash
        current_player_index = game.current_player.value
        hash_value ^= (self.player_key * current_player_index)
        
        return hash_value
    
    def _update_hash(self, hash_value: int, row: int, col: int, 
                    old_player: Player, new_player: Player) -> int:
        """
        Incrementally update hash when a piece is placed or removed.
        
        Args:
            hash_value: Current hash value
            row: Row of the changed cell
            col: Column of the changed cell
            old_player: Previous player at this position
            new_player: New player at this position
            
        Returns:
            Updated hash value
        """
        # Remove old piece
        hash_value ^= self.zobrist_table[row][col][old_player.value]
        # Add new piece
        hash_value ^= self.zobrist_table[row][col][new_player.value]
        return hash_value
    
    def _update_hash_for_move(self, hash_value: int, row: int, col: int, 
                              old_player: Player, new_player: Player, 
                              old_current_player: Player, new_current_player: Player) -> int:
        """
        Update hash for a move (piece placement + player change).
        
        Args:
            hash_value: Current hash value
            row: Row of the changed cell
            col: Column of the changed cell
            old_player: Previous player at this position (should be NONE)
            new_player: New player at this position
            old_current_player: Previous current player
            new_current_player: New current player
            
        Returns:
            Updated hash value
        """
        # Update piece
        hash_value = self._update_hash(hash_value, row, col, old_player, new_player)
        # Update current player
        hash_value ^= (self.player_key * old_current_player.value)
        hash_value ^= (self.player_key * new_current_player.value)
        return hash_value
    
    def _order_moves(self, game: Connect4, valid_moves: list, 
                    position_hash: int) -> list:
        """
        Order moves to maximize alpha-beta pruning efficiency.
        
        Args:
            game: Current game state
            valid_moves: List of valid column moves
            position_hash: Hash of current position (for transposition table lookup)
            
        Returns:
            Ordered list of moves (best moves first)
        """
        # Check transposition table for best move
        best_move = None
        if position_hash in self.transposition_table:
            entry = self.transposition_table[position_hash]
            if entry.best_move is not None and entry.best_move in valid_moves:
                best_move = entry.best_move
        
        # Center columns are more valuable (order: 3, 2, 4, 1, 5, 0, 6)
        center_order = [3, 2, 4, 1, 5, 0, 6]
        
        # Separate moves into ordered groups
        ordered_moves = []
        
        # First: best move from transposition table (if available)
        if best_move is not None:
            ordered_moves.append(best_move)
        
        # Then: order remaining moves by center preference
        remaining_moves = [m for m in valid_moves if m != best_move]
        
        # Sort remaining moves by center order
        remaining_moves.sort(key=lambda m: center_order.index(m) if m in center_order else 999)
        
        ordered_moves.extend(remaining_moves)
        
        return ordered_moves
    
    def get_best_move(self, game: Connect4) -> Optional[int]:
        """
        Get the best move for the bot using either iterative deepening or fixed depth.
        
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
        
        # Clear transposition table and caches for new search
        self.transposition_table.clear()
        self.valid_moves_cache.clear()
        self.evaluation_cache.clear()
        
        if self.search_type == "iterative":
            return self._get_best_move_iterative(game, valid_moves)
        else:
            return self._get_best_move_fixed(game, valid_moves)
    
    def _get_best_move_iterative(self, game: Connect4, valid_moves: list) -> Optional[int]:
        """
        Get best move using iterative deepening.
        
        Args:
            game: Current Connect4 game instance
            valid_moves: List of valid column moves
            
        Returns:
            Column index of the best move, or None if no valid moves
        """
        best_move = None
        position_hash = self._compute_hash(game)
        
        # Iterative deepening: search from depth 1 to max depth
        for current_depth in range(1, self.depth + 1):
            best_value = float('-inf')
            current_best_move = None
            
            # Get ordered moves for this iteration (with symmetry)
            ordered_moves = self._order_moves(game, valid_moves, position_hash)
            
            for move in ordered_moves:
                # Check for immediate win
                row = game.get_next_open_row(move)
                if row is not None:
                    # Make the move
                    game.make_move(move)
                    
                    # Early win detection
                    if game.game_over and game.winner == self.player:
                        game.undo_move()
                        return move  # Immediate win found
                    
                    # Evaluate the position
                    new_hash = self._update_hash_for_move(
                        position_hash, row, move, 
                        Player.NONE, self.player,
                        self.player, self.opponent
                    )
                    value = self._minimax_with_hash(game, current_depth - 1, False, 
                                                   float('-inf'), float('inf'), new_hash)
                    
                    # Undo the move
                    game.undo_move()
                    
                    if value > best_value:
                        best_value = value
                        current_best_move = move
            
            # Update best move for this depth
            if current_best_move is not None:
                best_move = current_best_move
        
        return best_move
    
    def _get_best_move_fixed(self, game: Connect4, valid_moves: list) -> Optional[int]:
        """
        Get best move using fixed depth search.
        
        Args:
            game: Current Connect4 game instance
            valid_moves: List of valid column moves
            
        Returns:
            Column index of the best move, or None if no valid moves
        """
        best_move = None
        best_value = float('-inf')
        position_hash = self._compute_hash(game)
        
        # Get ordered moves (with symmetry)
        ordered_moves = self._order_moves(game, valid_moves, position_hash)
        
        for move in ordered_moves:
            # Check for immediate win
            row = game.get_next_open_row(move)
            if row is not None:
                # Make the move
                game.make_move(move)
                
                # Early win detection
                if game.game_over and game.winner == self.player:
                    game.undo_move()
                    return move  # Immediate win found
                
                # Evaluate the position at fixed depth
                new_hash = self._update_hash_for_move(
                    position_hash, row, move,
                    Player.NONE, self.player,
                    self.player, self.opponent
                )
                value = self._minimax_with_hash(game, self.depth - 1, False, 
                                               float('-inf'), float('inf'), new_hash)
                
                # Undo the move
                game.undo_move()
                
                if value > best_value:
                    best_value = value
                    best_move = move
        
        return best_move
    
    def _minimax(self, game: Connect4, depth: int, maximizing: bool, 
                 alpha: float, beta: float) -> float:
        """
        Minimax algorithm wrapper that computes hash and calls internal version.
        
        Args:
            game: Current game state
            depth: Remaining search depth
            maximizing: True if maximizing (bot's turn), False if minimizing
            alpha: Best value for maximizing player
            beta: Best value for minimizing player
            
        Returns:
            Evaluation score of the position
        """
        position_hash = self._compute_hash(game)
        return self._minimax_with_hash(game, depth, maximizing, alpha, beta, position_hash)
    
    def _minimax_with_hash(self, game: Connect4, depth: int, maximizing: bool, 
                          alpha: float, beta: float, position_hash: int) -> float:
        """
        Minimax algorithm with alpha-beta pruning, transposition tables, move ordering,
        Principal Variation Search, and incremental hashing.
        
        Args:
            game: Current game state
            depth: Remaining search depth
            maximizing: True if maximizing (bot's turn), False if minimizing
            alpha: Best value for maximizing player
            beta: Best value for minimizing player
            position_hash: Pre-computed hash for this position
            
        Returns:
            Evaluation score of the position
        """
        # Check transposition table
        if position_hash in self.transposition_table:
            entry = self.transposition_table[position_hash]
            if entry.depth >= depth:
                if entry.bound == BoundType.EXACT:
                    return entry.score
                elif entry.bound == BoundType.LOWER_BOUND:
                    if entry.score >= beta:
                        return entry.score
                    alpha = max(alpha, entry.score)
                elif entry.bound == BoundType.UPPER_BOUND:
                    if entry.score <= alpha:
                        return entry.score
                    beta = min(beta, entry.score)
        
        # Terminal conditions
        if game.game_over:
            if game.winner == self.player:
                score = 1000 + depth  # Prefer faster wins
            elif game.winner == self.opponent:
                score = -1000 - depth  # Prefer slower losses
            else:
                score = 0  # Draw
            
            # Store in transposition table
            self.transposition_table[position_hash] = TranspositionEntry(
                score, depth, BoundType.EXACT
            )
            return score
        
        if depth == 0:
            # Check evaluation cache
            if position_hash in self.evaluation_cache:
                score = self.evaluation_cache[position_hash]
            else:
                score = self._evaluate_position(game)
                self.evaluation_cache[position_hash] = score
            
            # Store in transposition table
            self.transposition_table[position_hash] = TranspositionEntry(
                score, depth, BoundType.EXACT
            )
            return score
        
        # Get cached or compute valid moves
        if position_hash in self.valid_moves_cache:
            valid_moves = self.valid_moves_cache[position_hash]
        else:
            valid_moves = game.get_valid_moves()
            self.valid_moves_cache[position_hash] = valid_moves
        
        ordered_moves = self._order_moves(game, valid_moves, position_hash)
        
        if not ordered_moves:
            # No moves available (shouldn't happen if depth > 0 and not game_over)
            score = 0
            self.transposition_table[position_hash] = TranspositionEntry(
                score, depth, BoundType.EXACT
            )
            return score
        
        best_move = None
        original_alpha = alpha
        
        if maximizing:
            # Principal Variation Search: first move uses full window, others use null window
            first_move = True
            
            for move in ordered_moves:
                row = game.get_next_open_row(move)
                if row is None:
                    continue
                
                # Early win detection
                game.make_move(move)
                if game.game_over and game.winner == self.player:
                    game.undo_move()
                    score = 1000 + depth
                    self.transposition_table[position_hash] = TranspositionEntry(
                        score, depth, BoundType.EXACT, move
                    )
                    return score
                
                # Update hash incrementally
                new_hash = self._update_hash_for_move(
                    position_hash, row, move,
                    Player.NONE, self.player,
                    self.player, self.opponent
                )
                
                if first_move:
                    # Full window search for first move
                    eval_score = self._minimax_with_hash(
                        game, depth - 1, False, alpha, beta, new_hash
                    )
                    first_move = False
                else:
                    # Null window search (Principal Variation Search)
                    eval_score = self._minimax_with_hash(
                        game, depth - 1, False, alpha, alpha + 1, new_hash
                    )
                    
                    # If null window search fails high, do full search
                    if eval_score > alpha and eval_score < beta:
                        eval_score = self._minimax_with_hash(
                            game, depth - 1, False, alpha, beta, new_hash
                        )
                
                game.undo_move()
                
                if eval_score > alpha:
                    alpha = eval_score
                    best_move = move
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            max_eval = alpha
            
            # Store in transposition table
            if max_eval <= original_alpha:
                bound = BoundType.UPPER_BOUND
            elif max_eval >= beta:
                bound = BoundType.LOWER_BOUND
            else:
                bound = BoundType.EXACT
            
            self.transposition_table[position_hash] = TranspositionEntry(
                max_eval, depth, bound, best_move
            )
            
            return max_eval
        else:
            # Minimizing player
            first_move = True
            
            for move in ordered_moves:
                row = game.get_next_open_row(move)
                if row is None:
                    continue
                
                # Early loss detection
                game.make_move(move)
                if game.game_over and game.winner == self.opponent:
                    game.undo_move()
                    score = -1000 - depth
                    self.transposition_table[position_hash] = TranspositionEntry(
                        score, depth, BoundType.EXACT, move
                    )
                    return score
                
                # Update hash incrementally
                new_hash = self._update_hash_for_move(
                    position_hash, row, move,
                    Player.NONE, self.opponent,
                    self.opponent, self.player
                )
                
                if first_move:
                    # Full window search for first move
                    eval_score = self._minimax_with_hash(
                        game, depth - 1, True, alpha, beta, new_hash
                    )
                    first_move = False
                else:
                    # Null window search (Principal Variation Search)
                    eval_score = self._minimax_with_hash(
                        game, depth - 1, True, beta - 1, beta, new_hash
                    )
                    
                    # If null window search fails low, do full search
                    if eval_score < beta and eval_score > alpha:
                        eval_score = self._minimax_with_hash(
                            game, depth - 1, True, alpha, beta, new_hash
                        )
                
                game.undo_move()
                
                if eval_score < beta:
                    beta = eval_score
                    best_move = move
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            min_eval = beta
            
            # Store in transposition table
            if min_eval <= original_alpha:
                bound = BoundType.UPPER_BOUND
            elif min_eval >= beta:
                bound = BoundType.LOWER_BOUND
            else:
                bound = BoundType.EXACT
            
            self.transposition_table[position_hash] = TranspositionEntry(
                min_eval, depth, bound, best_move
            )
            
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

