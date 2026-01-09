"""
Flask web server for Connect 4 game with GUI.
"""

from flask import Flask, render_template, jsonify, request
from game import Connect4, Player
from bot import Bot
import json

app = Flask(__name__)

# Store game instances in memory (in production, use a proper session store)
games = {}
bot = Bot(depth=6, player=Player.YELLOW)


@app.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Create a new game."""
    game_id = request.json.get('game_id', 'default')
    game = Connect4()
    games[game_id] = game
    return jsonify({
        'success': True,
        'board': game.get_board(),
        'current_player': game.current_player.value,
        'game_over': game.game_over,
        'winner': game.winner.value
    })


@app.route('/api/move', methods=['POST'])
def make_move():
    """Make a player move."""
    data = request.json
    game_id = data.get('game_id', 'default')
    col = data.get('col')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'}), 404
    
    game = games[game_id]
    
    if col is None or col < 0 or col >= Connect4.COLS:
        return jsonify({'success': False, 'error': 'Invalid column'}), 400
    
    if not game.is_valid_move(col):
        return jsonify({'success': False, 'error': 'Invalid move'}), 400
    
    success = game.make_move(col)
    
    if not success:
        return jsonify({'success': False, 'error': 'Move failed'}), 400
    
    response = {
        'success': True,
        'board': game.get_board(),
        'current_player': game.current_player.value,
        'game_over': game.game_over,
        'winner': game.winner.value
    }
    
    return jsonify(response)


@app.route('/api/bot_move', methods=['POST'])
def bot_move():
    """Get and make the bot's move."""
    data = request.json
    game_id = data.get('game_id', 'default')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'}), 404
    
    game = games[game_id]
    
    if game.game_over:
        return jsonify({
            'success': False,
            'error': 'Game is over',
            'board': game.get_board(),
            'winner': game.winner.value
        }), 400
    
    if game.current_player != bot.player:
        return jsonify({
            'success': False,
            'error': 'Not bot\'s turn'
        }), 400
    
    # Get bot's move
    bot_col = bot.get_best_move(game)
    
    if bot_col is None:
        return jsonify({'success': False, 'error': 'No valid moves'}), 400
    
    # Make the move
    success = game.make_move(bot_col)
    
    if not success:
        return jsonify({'success': False, 'error': 'Bot move failed'}), 400
    
    return jsonify({
        'success': True,
        'col': bot_col,
        'board': game.get_board(),
        'current_player': game.current_player.value,
        'game_over': game.game_over,
        'winner': game.winner.value
    })


@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    """Get the current game state."""
    game_id = request.args.get('game_id', 'default')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'}), 404
    
    game = games[game_id]
    
    return jsonify({
        'success': True,
        'board': game.get_board(),
        'current_player': game.current_player.value,
        'game_over': game.game_over,
        'winner': game.winner.value
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

