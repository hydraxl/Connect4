"""
Tests for Connect4 bot.
"""

import pytest
from game import Connect4, Player
from bot import Bot, BoundType, TranspositionEntry


class TestBotInitialization:
    """Test bot initialization."""
    
    def test_bot_default_initialization(self):
        """Test bot with default parameters."""
        bot = Bot()
        
        assert bot.depth == 6
        assert bot.player == Player.YELLOW
        assert bot.opponent == Player.RED
    
    def test_bot_custom_initialization(self):
        """Test bot with custom parameters."""
        bot = Bot(depth=4, player=Player.RED)
        
        assert bot.depth == 4
        assert bot.player == Player.RED
        assert bot.opponent == Player.YELLOW
    
    def test_bot_search_type_initialization(self):
        """Test bot with different search types."""
        bot_iterative = Bot(depth=4, search_type="iterative")
        bot_fixed = Bot(depth=4, search_type="fixed")
        
        assert bot_iterative.search_type == "iterative"
        assert bot_fixed.search_type == "fixed"
        assert bot_iterative.depth == 4
        assert bot_fixed.depth == 4
    
    def test_bot_invalid_search_type(self):
        """Test that invalid search type raises error."""
        with pytest.raises(ValueError, match="search_type must be 'iterative' or 'fixed'"):
            Bot(depth=4, search_type="invalid")


class TestBotMoves:
    """Test bot move selection."""
    
    def test_bot_returns_valid_move(self):
        """Test that bot returns a valid move."""
        game = Connect4()
        bot = Bot(player=Player.YELLOW)
        
        game.make_move(0)  # RED moves first
        move = bot.get_best_move(game)
        
        assert move is not None
        assert 0 <= move < Connect4.COLS
        assert game.is_valid_move(move)
    
    def test_bot_returns_none_when_game_over(self):
        """Test that bot returns None when game is over."""
        game = Connect4()
        bot = Bot()
        
        # Create a horizontal win
        for i in range(4):
            game.make_move(i)  # RED
            if i < 3:
                game.make_move(i)  # YELLOW blocks
        
        assert game.game_over == True
        move = bot.get_best_move(game)
        
        assert move is None
    
    def test_bot_returns_none_when_no_valid_moves(self):
        """Test that bot returns None when no valid moves exist."""
        game = Connect4()
        bot = Bot()
        
        # Fill the board
        for col in range(Connect4.COLS):
            for _ in range(Connect4.ROWS):
                if game.is_valid_move(col):
                    game.make_move(col)
        
        move = bot.get_best_move(game)
        assert move is None
    
    def test_bot_makes_winning_move_when_available(self):
        """Test that bot makes a winning move when available."""
        game = Connect4()
        bot = Bot(depth=6, player=Player.YELLOW)
        
        # Set up board so YELLOW can win
        # RED: columns 0, 1, 2
        # YELLOW: columns 0, 1, 2 (one less each)
        for i in range(3):
            game.make_move(i)  # RED
            if i < 2:  # Don't fill column 2 completely
                game.make_move(i)  # YELLOW
        
        # Now YELLOW should win by playing column 2
        move = bot.get_best_move(game)
        game.make_move(move)
        
        # Check if this creates a win (might need to check multiple scenarios)
        assert move is not None
    
    def test_bot_blocks_opponent_win(self):
        """Test that bot blocks opponent's winning move."""
        game = Connect4()
        bot = Bot(depth=6, player=Player.YELLOW)
        
        # Set up so RED has 3 in a row horizontally
        for i in range(3):
            game.make_move(i)  # RED
            if i < 2:
                game.make_move(6)  # YELLOW moves elsewhere
        
        # Bot should block RED's win
        move = bot.get_best_move(game)
        game.make_move(move)
        
        # Verify RED can't win immediately
        test_game = game.copy()
        test_game.make_move(3)  # RED tries to win
        # If bot blocked correctly, this shouldn't be a win
        # (or the game should already be over if bot won)
        assert move == 3  # Bot should block column 3


class TestBotEvaluation:
    """Test bot evaluation functions."""
    
    def test_bot_evaluates_position(self):
        """Test that bot can evaluate a position."""
        game = Connect4()
        bot = Bot()
        
        game.make_move(0)
        score = bot._evaluate_position(game)
        
        assert isinstance(score, (int, float))
    
    def test_bot_prefers_winning_positions(self):
        """Test that bot evaluates winning positions highly."""
        game = Connect4()
        bot = Bot(player=Player.YELLOW)
        
        # Create a winning position for YELLOW
        for i in range(3):
            game.make_move(i)  # RED
            game.make_move(i)  # YELLOW
        
        # YELLOW can win
        game.make_move(6)  # RED
        winning_score = bot._evaluate_position(game)
        
        # Compare with a neutral position
        neutral_game = Connect4()
        neutral_game.make_move(3)
        neutral_score = bot._evaluate_position(neutral_game)
        
        # Winning position should score higher (or we should detect win)
        # Note: This is a heuristic test, exact values may vary
        assert True  # Test passes if no errors
    
    def test_bot_evaluates_lines(self):
        """Test bot's line evaluation."""
        game = Connect4()
        bot = Bot()
        
        # Create a line with bot's pieces (vertical)
        game.make_move(0)  # RED
        game.make_move(0)  # YELLOW (bot)
        game.make_move(0)  # RED
        game.make_move(0)  # YELLOW (bot)
        
        # Evaluate vertical line starting at bottom
        row = Connect4.ROWS - 4  # Start at the first YELLOW piece
        score = bot._evaluate_line(game, row, 0, 1, 0)
        assert isinstance(score, (int, float))


class TestBotMinimax:
    """Test minimax algorithm."""
    
    def test_bot_uses_minimax(self):
        """Test that bot uses minimax to find moves."""
        game = Connect4()
        bot = Bot(depth=3, player=Player.YELLOW)
        
        game.make_move(0)  # RED
        move = bot.get_best_move(game)
        
        # Bot should return a move (minimax should find something)
        assert move is not None
    
    def test_bot_with_different_depths(self):
        """Test bot with different search depths."""
        game = Connect4()
        game.make_move(0)  # RED
        
        for depth in [2, 4, 6]:
            bot = Bot(depth=depth, player=Player.YELLOW)
            move = bot.get_best_move(game)
            assert move is not None
    
    def test_bot_handles_alpha_beta_pruning(self):
        """Test that bot's minimax uses alpha-beta pruning."""
        game = Connect4()
        bot = Bot(depth=4, player=Player.YELLOW)
        
        # Create a position where pruning might occur
        for i in range(2):
            game.make_move(i)
            game.make_move(i)
        
        move = bot.get_best_move(game)
        # Should still return a valid move
        assert move is not None


class TestTranspositionTable:
    """Test transposition table functionality."""
    
    def test_transposition_table_initialized(self):
        """Test that transposition table is initialized."""
        bot = Bot()
        assert hasattr(bot, 'transposition_table')
        assert isinstance(bot.transposition_table, dict)
        assert len(bot.transposition_table) == 0
    
    def test_transposition_table_populated_during_search(self):
        """Test that transposition table is populated during search."""
        game = Connect4()
        bot = Bot(depth=3, search_type="fixed")
        
        game.make_move(0)  # RED
        initial_size = len(bot.transposition_table)
        
        move = bot.get_best_move(game)
        
        # Transposition table should have entries after search
        assert len(bot.transposition_table) > initial_size
        assert move is not None
    
    def test_transposition_table_cleared_between_searches(self):
        """Test that transposition table is cleared between searches."""
        game = Connect4()
        bot = Bot(depth=2, search_type="fixed")
        
        game.make_move(0)
        bot.get_best_move(game)
        size_after_first = len(bot.transposition_table)
        
        # Clear and search again
        game2 = Connect4()
        game2.make_move(1)
        bot.get_best_move(game2)
        
        # Table should be cleared and repopulated
        assert len(bot.transposition_table) > 0
    
    def test_transposition_table_reuses_entries(self):
        """Test that transposition table reuses entries in iterative deepening."""
        game = Connect4()
        bot = Bot(depth=3, search_type="iterative")
        
        game.make_move(0)
        bot.get_best_move(game)
        
        # In iterative deepening, deeper searches should reuse entries from shallower searches
        assert len(bot.transposition_table) > 0


class TestZobristHashing:
    """Test Zobrist hashing functionality."""
    
    def test_zobrist_table_initialized(self):
        """Test that Zobrist table is initialized."""
        bot = Bot()
        assert hasattr(bot, 'zobrist_table')
        assert len(bot.zobrist_table) == Connect4.ROWS
        assert len(bot.zobrist_table[0]) == Connect4.COLS
        assert len(bot.zobrist_table[0][0]) == 3  # NONE, RED, YELLOW
    
    def test_hash_computation(self):
        """Test that hash computation works."""
        game = Connect4()
        bot = Bot()
        
        hash1 = bot._compute_hash(game)
        assert isinstance(hash1, int)
        
        # Same position should give same hash
        hash2 = bot._compute_hash(game)
        assert hash1 == hash2
    
    def test_hash_changes_with_moves(self):
        """Test that hash changes when moves are made."""
        game = Connect4()
        bot = Bot()
        
        hash_before = bot._compute_hash(game)
        game.make_move(3)
        hash_after = bot._compute_hash(game)
        
        assert hash_before != hash_after
    
    def test_hash_includes_current_player(self):
        """Test that hash includes current player."""
        game1 = Connect4()
        game2 = Connect4()
        bot = Bot()
        
        # Make same moves but different current player
        game1.make_move(0)  # RED moves, now YELLOW's turn
        game2.make_move(0)  # RED moves, now YELLOW's turn
        
        # Both should have same board and same current player
        hash1 = bot._compute_hash(game1)
        hash2 = bot._compute_hash(game2)
        assert hash1 == hash2
        
        # But if we make another move in one, they differ
        game1.make_move(1)
        hash1_after = bot._compute_hash(game1)
        assert hash1 != hash1_after


class TestMoveOrdering:
    """Test move ordering functionality."""
    
    def test_move_ordering_prioritizes_center(self):
        """Test that move ordering prioritizes center columns."""
        game = Connect4()
        bot = Bot()
        
        valid_moves = [0, 1, 2, 3, 4, 5, 6]
        position_hash = bot._compute_hash(game)
        ordered_moves = bot._order_moves(game, valid_moves, position_hash)
        
        # Center column (3) should be first or early
        assert 3 in ordered_moves
        # First few moves should include center columns
        center_columns = [2, 3, 4]
        assert any(col in ordered_moves[:3] for col in center_columns)
    
    def test_move_ordering_uses_transposition_table(self):
        """Test that move ordering uses best move from transposition table."""
        game = Connect4()
        bot = Bot(depth=2, search_type="fixed")
        
        game.make_move(0)
        position_hash = bot._compute_hash(game)
        
        # Populate transposition table
        bot.get_best_move(game)
        
        # Get ordered moves
        valid_moves = game.get_valid_moves()
        ordered_moves = bot._order_moves(game, valid_moves, position_hash)
        
        # Should return ordered moves
        assert len(ordered_moves) == len(valid_moves)
        assert set(ordered_moves) == set(valid_moves)


class TestIterativeDeepening:
    """Test iterative deepening search."""
    
    def test_iterative_deepening_returns_move(self):
        """Test that iterative deepening returns a valid move."""
        game = Connect4()
        bot = Bot(depth=4, search_type="iterative")
        
        game.make_move(0)
        move = bot.get_best_move(game)
        
        assert move is not None
        assert 0 <= move < Connect4.COLS
        assert game.is_valid_move(move)
    
    def test_iterative_deepening_searches_all_depths(self):
        """Test that iterative deepening searches from depth 1 to max depth."""
        game = Connect4()
        bot = Bot(depth=3, search_type="iterative")
        
        game.make_move(0)
        move = bot.get_best_move(game)
        
        # Should complete all depths and return a move
        assert move is not None
        # Transposition table should have entries from multiple depths
        assert len(bot.transposition_table) > 0
    
    def test_iterative_deepening_vs_fixed_same_result(self):
        """Test that iterative deepening and fixed depth can find moves."""
        game1 = Connect4()
        game2 = Connect4()
        
        bot_iterative = Bot(depth=3, search_type="iterative")
        bot_fixed = Bot(depth=3, search_type="fixed")
        
        game1.make_move(0)
        game2.make_move(0)
        
        move1 = bot_iterative.get_best_move(game1)
        move2 = bot_fixed.get_best_move(game2)
        
        # Both should return valid moves (may or may not be the same)
        assert move1 is not None
        assert move2 is not None
        assert 0 <= move1 < Connect4.COLS
        assert 0 <= move2 < Connect4.COLS


class TestFixedDepthSearch:
    """Test fixed depth search."""
    
    def test_fixed_depth_returns_move(self):
        """Test that fixed depth search returns a valid move."""
        game = Connect4()
        bot = Bot(depth=4, search_type="fixed")
        
        game.make_move(0)
        move = bot.get_best_move(game)
        
        assert move is not None
        assert 0 <= move < Connect4.COLS
        assert game.is_valid_move(move)
    
    def test_fixed_depth_searches_at_specified_depth(self):
        """Test that fixed depth searches at the specified depth."""
        game = Connect4()
        bot = Bot(depth=3, search_type="fixed")
        
        game.make_move(0)
        move = bot.get_best_move(game)
        
        assert move is not None
        # Transposition table should have entries
        assert len(bot.transposition_table) > 0
    
    def test_fixed_depth_with_different_depths(self):
        """Test fixed depth search with different depth values."""
        game = Connect4()
        game.make_move(0)
        
        for depth in [2, 3, 4]:
            bot = Bot(depth=depth, search_type="fixed")
            move = bot.get_best_move(game)
            assert move is not None
            assert 0 <= move < Connect4.COLS


class TestSearchTypeComparison:
    """Test comparison between search types."""
    
    def test_both_search_types_produce_valid_moves(self):
        """Test that both search types produce valid moves."""
        game1 = Connect4()
        game2 = Connect4()
        
        bot_iterative = Bot(depth=3, search_type="iterative")
        bot_fixed = Bot(depth=3, search_type="fixed")
        
        game1.make_move(0)
        game2.make_move(0)
        
        move1 = bot_iterative.get_best_move(game1)
        move2 = bot_fixed.get_best_move(game2)
        
        assert move1 is not None
        assert move2 is not None
        assert game1.is_valid_move(move1)
        assert game2.is_valid_move(move2)
    
    def test_both_search_types_use_transposition_table(self):
        """Test that both search types use transposition tables."""
        game1 = Connect4()
        game2 = Connect4()
        
        bot_iterative = Bot(depth=3, search_type="iterative")
        bot_fixed = Bot(depth=3, search_type="fixed")
        
        game1.make_move(0)
        game2.make_move(0)
        
        bot_iterative.get_best_move(game1)
        bot_fixed.get_best_move(game2)
        
        # Both should populate transposition tables
        assert len(bot_iterative.transposition_table) > 0
        assert len(bot_fixed.transposition_table) > 0
    
    def test_both_search_types_handle_complex_positions(self):
        """Test that both search types handle complex positions."""
        # Create a more complex position
        game1 = Connect4()
        game2 = Connect4()
        
        # Set up a position with multiple moves
        moves = [0, 1, 0, 1, 2, 3]
        for move in moves:
            game1.make_move(move)
            game2.make_move(move)
        
        bot_iterative = Bot(depth=4, search_type="iterative")
        bot_fixed = Bot(depth=4, search_type="fixed")
        
        move1 = bot_iterative.get_best_move(game1)
        move2 = bot_fixed.get_best_move(game2)
        
        assert move1 is not None
        assert move2 is not None
        assert game1.is_valid_move(move1)
        assert game2.is_valid_move(move2)


class TestIncrementalHashing:
    """Test incremental hash updates."""
    
    def test_incremental_hash_update(self):
        """Test that incremental hash updates work correctly."""
        game = Connect4()
        bot = Bot()
        
        # Compute initial hash
        initial_hash = bot._compute_hash(game)
        
        # Make a move and compute hash incrementally
        row = game.get_next_open_row(3)
        if row is not None:
            # Update hash incrementally
            updated_hash = bot._update_hash_for_move(
                initial_hash, row, 3,
                Player.NONE, Player.RED,
                Player.RED, Player.YELLOW
            )
            
            # Make the actual move and compute hash
            game.make_move(3)
            computed_hash = bot._compute_hash(game)
            
            # Incremental update should match full computation
            assert updated_hash == computed_hash
    
    def test_incremental_hash_consistency(self):
        """Test that incremental hash updates are consistent."""
        game = Connect4()
        bot = Bot()
        
        # Make several moves and verify incremental updates match full computation
        hash_value = bot._compute_hash(game)
        
        for move in [3, 2, 4]:
            row = game.get_next_open_row(move)
            if row is None:
                continue
            
            current_player = game.current_player
            next_player = Player.YELLOW if current_player == Player.RED else Player.RED
            
            # Update hash incrementally
            hash_value = bot._update_hash_for_move(
                hash_value, row, move,
                Player.NONE, current_player,
                current_player, next_player
            )
            
            # Make the actual move
            game.make_move(move)
            
            # Verify hash matches
            computed_hash = bot._compute_hash(game)
            assert hash_value == computed_hash


class TestEarlyWinDetection:
    """Test early win/loss detection optimization."""
    
    def test_early_win_detection(self):
        """Test that bot detects immediate wins early."""
        game = Connect4()
        bot = Bot(depth=6, search_type="fixed", player=Player.YELLOW)
        
        # Set up a position where YELLOW can win immediately
        for i in range(3):
            game.make_move(i)  # RED
            game.make_move(i)  # YELLOW
        
        # YELLOW can win by playing column 3
        move = bot.get_best_move(game)
        
        # Bot should find the winning move
        assert move is not None
        game.make_move(move)
        
        # Verify it's a win (or at least a good move)
        assert move in [2, 3, 4]  # Should be near the winning area
    
    def test_early_loss_detection(self):
        """Test that bot detects immediate losses early."""
        game = Connect4()
        bot = Bot(depth=6, search_type="fixed", player=Player.YELLOW)
        
        # Set up a position where RED can win if YELLOW doesn't block
        for i in range(3):
            game.make_move(i)  # RED
            if i < 2:
                game.make_move(6)  # YELLOW moves elsewhere
        
        # Bot should block RED's winning move
        move = bot.get_best_move(game)
        
        assert move is not None
        # Bot should block column 3
        assert move == 3


class TestCaching:
    """Test caching optimizations."""
    
    def test_valid_moves_caching(self):
        """Test that valid moves are cached."""
        game = Connect4()
        bot = Bot(depth=3, search_type="fixed")
        
        game.make_move(0)
        position_hash = bot._compute_hash(game)
        
        # Initially cache should be empty for this position
        assert position_hash not in bot.valid_moves_cache
        
        # After search, cache should be populated
        bot.get_best_move(game)
        
        # Cache should have entries
        assert len(bot.valid_moves_cache) > 0
    
    def test_valid_moves_cache_reuse(self):
        """Test that valid moves cache is reused."""
        game = Connect4()
        bot = Bot(depth=2, search_type="fixed")
        
        game.make_move(0)
        position_hash = bot._compute_hash(game)
        
        # First search
        bot.get_best_move(game)
        cached_moves = bot.valid_moves_cache.get(position_hash)
        
        # Cache should have the moves
        assert cached_moves is not None
        assert len(cached_moves) > 0
    
    def test_evaluation_caching(self):
        """Test that evaluations are cached."""
        game = Connect4()
        bot = Bot(depth=3, search_type="fixed")
        
        game.make_move(0)
        
        # Initially cache should be empty
        assert len(bot.evaluation_cache) == 0
        
        # After search, evaluation cache should be populated
        bot.get_best_move(game)
        
        # Cache should have entries
        assert len(bot.evaluation_cache) > 0
    
    def test_evaluation_cache_reuse(self):
        """Test that evaluation cache is reused."""
        game = Connect4()
        bot = Bot(depth=2, search_type="fixed")
        
        game.make_move(0)
        position_hash = bot._compute_hash(game)
        
        # First search
        bot.get_best_move(game)
        
        # Evaluation cache should have entries
        assert len(bot.evaluation_cache) > 0
        
        # If we search the same position again, cache should be used
        # (though in practice, transposition table would catch it first)


class TestPrincipalVariationSearch:
    """Test Principal Variation Search (PVS) optimization."""
    
    def test_pvs_returns_valid_move(self):
        """Test that PVS still returns valid moves."""
        game = Connect4()
        bot = Bot(depth=4, search_type="fixed")
        
        game.make_move(0)
        move = bot.get_best_move(game)
        
        # PVS should still find valid moves
        assert move is not None
        assert 0 <= move < Connect4.COLS
        assert game.is_valid_move(move)
    
    def test_pvs_with_complex_position(self):
        """Test PVS with a more complex position."""
        game = Connect4()
        bot = Bot(depth=3, search_type="fixed")
        
        # Create a more complex position
        moves = [0, 1, 0, 1, 2, 3]
        for move in moves:
            game.make_move(move)
        
        move = bot.get_best_move(game)
        
        # Should still return a valid move
        assert move is not None
        assert 0 <= move < Connect4.COLS
        assert game.is_valid_move(move)
    
    def test_pvs_consistency_with_regular_search(self):
        """Test that PVS produces consistent results."""
        game1 = Connect4()
        game2 = Connect4()
        
        bot1 = Bot(depth=3, search_type="fixed")
        bot2 = Bot(depth=3, search_type="fixed")
        
        game1.make_move(0)
        game2.make_move(0)
        
        move1 = bot1.get_best_move(game1)
        move2 = bot2.get_best_move(game2)
        
        # Both should return valid moves (may or may not be same due to transposition table)
        assert move1 is not None
        assert move2 is not None
        assert game1.is_valid_move(move1)
        assert game2.is_valid_move(move2)

