import random
import json

class Token:
    def __init__(self, color):
        self.position = 0
        self.home = True
        self.color = color
        self.safe_zone = False
        self.finished = False
        self.token_id = f"{color}_{id(self)}"

class Ludo:
    def __init__(self):
        self.board_size = 40
        self.board = [0] * self.board_size
        self.players = [Token(color) for color in ['Red', 'Green', 'Blue', 'Yellow']]
        self.current_player = 0
        self.start_positions = [0, 10, 20, 30]
        self.safe_zones = set([5, 15, 25, 35])
        self.winning_positions = [39] * 4
        self.winner = None
        self.dice_rolls = []
        self.custom_board = [i for i in range(self.board_size)]
        self.special_spaces = {10: 'Skip', 20: 'Reverse', 30: 'Extra'}
        self.token_choices = {color: 0 for color in ['Red', 'Green', 'Blue', 'Yellow']}
        self.token_throws = {color: [] for color in ['Red', 'Green', 'Blue', 'Yellow']}
        self.turn_history = []
        self.player_profiles = {color: {'games_played': 0, 'games_won': 0} for color in ['Red', 'Green', 'Blue', 'Yellow']}
        self.game_settings = {'show_dice_rolls': True, 'show_turn_history': True}

    def roll_dice(self, num_rolls=1):
        rolls = [random.randint(1, 6) for _ in range(num_rolls)]
        self.dice_rolls.append(rolls)
        return rolls

    def move_token(self, token, steps):
        if token.home:
            if steps == 6:
                token.home = False
                token.position = self.start_positions[self.players.index(token)]
        else:
            new_position = token.position + steps
            if new_position < self.board_size:
                token.position = new_position
                token.safe_zone = new_position in self.safe_zones
                if new_position in self.special_spaces:
                    self.handle_special_space(token, self.special_spaces[new_position])
                if new_position == self.winning_positions[self.players.index(token)]:
                    token.finished = True
                    token.position = self.board_size
                self.token_throws[token.color].append(steps)
        self.turn_history.append((self.players[self.current_player].color, steps, token.position))

    def handle_special_space(self, token, action):
        if action == 'Skip':
            self.current_player = (self.current_player + 1) % 4
        elif action == 'Reverse':
            self.players.reverse()
        elif action == 'Extra':
            extra_rolls = self.roll_dice(1)
            self.move_token(token, extra_rolls[0])

    def check_for_landing(self, token):
        for other_token in self.players:
            if other_token != token and other_token.position == token.position and not other_token.safe_zone:
                other_token.home = True
                other_token.position = 0

    def player_turn(self):
        token = self.players[self.current_player]
        print(f"{token.color}'s turn.")
        dice_rolls = self.roll_dice()
        for roll in dice_rolls:
            self.move_token(token, roll)
            self.check_for_landing(token)
        self.check_for_winner()

    def play_turn(self):
        if not self.winner:
            self.player_turn()
            self.current_player = (self.current_player + 1) % 4

    def check_for_winner(self):
        for player in self.players:
            if player.finished:
                self.winner = player.color
                self.player_profiles[player.color]['games_won'] += 1
                return

    def get_positions(self):
        return [(token.color, token.position, token.safe_zone, token.finished, token.token_id) for token in self.players]

    def display_board(self):
        board_display = ['.' for _ in range(self.board_size)]
        for token in self.players:
            if token.position < self.board_size:
                board_display[token.position] = token.color[0]
        print("Board: " + ''.join(board_display))

    def display_dice_rolls(self):
        if self.game_settings['show_dice_rolls']:
            print("Dice Rolls: ", self.dice_rolls)

    def display_turn_history(self):
        if self.game_settings['show_turn_history']:
            print("Turn History:")
            for entry in self.turn_history:
                print(f"Player {entry[0]} rolled {entry[1]} and moved to position {entry[2]}")

    def configure_board(self, new_board):
        if len(new_board) == self.board_size:
            self.custom_board = new_board
            self.board = new_board
        else:
            print("New board configuration does not match the current board size.")

    def choose_token(self, color, token_index):
        if 0 <= token_index < len(self.players):
            self.token_choices[color] = token_index
            print(f"Token {color} selected.")

    def display_token_throws(self):
        for color, throws in self.token_throws.items():
            print(f"Token {color} throws: {throws}")

    def reset_game(self):
        self.__init__()
        print("Game reset.")

    def save_game(self, filename):
        with open(filename, 'w') as file:
            json.dump({
                'current_player': self.current_player,
                'winner': self.winner,
                'dice_rolls': self.dice_rolls,
                'token_throws': self.token_throws,
                'turn_history': self.turn_history,
                'player_profiles': self.player_profiles,
                'game_settings': self.game_settings,
                'players': [
                    {
                        'color': token.color,
                        'position': token.position,
                        'home': token.home,
                        'finished': token.finished
                    } for token in self.players
                ]
            }, file, indent=4)

    def load_game(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            self.current_player = data['current_player']
            self.winner = data['winner']
            self.dice_rolls = data['dice_rolls']
            self.token_throws = data['token_throws']
            self.turn_history = data['turn_history']
            self.player_profiles = data['player_profiles']
            self.game_settings = data['game_settings']
            for idx, token_data in enumerate(data['players']):
                self.players[idx].color = token_data['color']
                self.players[idx].position = token_data['position']
                self.players[idx].home = token_data['home']
                self.players[idx].finished = token_data['finished']

def main():
    game = Ludo()
    custom_board = [i * 2 % 40 for i in range(40)]
    game.configure_board(custom_board)
    rounds = 0
    while not game.winner:
        game.play_turn()
        game.display_board()
        game.display_dice_rolls()
        game.display_token_throws()
        game.display_turn_history()
        print(f"Round {rounds}: {game.get_positions()}")
        rounds += 1
    print(f"The winner is {game.winner}!")
    game.save_game('ludo_game_state.json')
    print("Game state saved.")

if __name__ == "__main__":
    main()
