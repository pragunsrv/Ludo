import random
import json
import os

class Token:
    def __init__(self, color):
        self.position = 0
        self.home = True
        self.color = color
        self.safe_zone = False
        self.finished = False
        self.token_id = f"{color}_{id(self)}"

class Ludo:
    def __init__(self, num_players=4):
        self.board_size = 40
        self.board = [0] * self.board_size
        self.players = [Token(color) for color in ['Red', 'Green', 'Blue', 'Yellow'][:num_players]]
        self.num_players = num_players
        self.current_player = 0
        self.start_positions = [0, 10, 20, 30][:num_players]
        self.safe_zones = set([5, 15, 25, 35])
        self.winning_positions = [39] * self.num_players
        self.winner = None
        self.dice_rolls = []
        self.custom_board = [i for i in range(self.board_size)]
        self.special_spaces = {10: 'Skip', 20: 'Reverse', 30: 'Extra'}
        self.token_choices = {color: 0 for color in ['Red', 'Green', 'Blue', 'Yellow'][:num_players]}
        self.token_throws = {color: [] for color in ['Red', 'Green', 'Blue', 'Yellow'][:num_players]}
        self.turn_history = []
        self.player_profiles = {color: {'games_played': 0, 'games_won': 0, 'average_roll': 0, 'longest_turn': 0} for color in ['Red', 'Green', 'Blue', 'Yellow'][:num_players]}
        self.token_history = {color: [] for color in ['Red', 'Green', 'Blue', 'Yellow'][:num_players]}
        self.custom_rules = {'extra_dice_roll': False, 'reverse_order': False, 'double_move': False}
        self.ongoing_turns = []
        self.current_turn = {'player': None, 'dice_roll': 0, 'moves': []}
        self.challenge_mode = False

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
                self.token_history[token.color].append((steps, token.position))
                self.update_player_profile(token.color, steps)
        self.turn_history.append((self.players[self.current_player].color, steps, token.position))

    def handle_special_space(self, token, action):
        if action == 'Skip':
            self.current_player = (self.current_player + 1) % self.num_players
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
        self.current_turn = {'player': token.color, 'dice_roll': sum(dice_rolls), 'moves': []}
        for roll in dice_rolls:
            self.move_token(token, roll)
            self.check_for_landing(token)
            self.current_turn['moves'].append((roll, token.position))
        self.ongoing_turns.append(self.current_turn)
        self.check_for_winner()

    def update_player_profile_(self, color, steps):
        profile = self.player_profiles[color]
        profile['games_played'] += 1
        profile['average_roll'] = ((profile['average_roll'] * (profile['games_played'] - 1)) + steps) / profile['games_played']
        longest_turn = max(max(self.current_turn['moves'], key=lambda x: x[0])[0], profile['longest_turn'])
        profile['longest_turn'] = longest_turn
    def load_game_(self, filename):
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

    def show_main_menu_(self):
        print("Main Menu:")
        print("1. Start New Game")
        print("2. Load Game")
        print("3. Settings")
        print("4. Quit")

    def show_save_load_menu_(self):
        print("Save/Load Menu:")
        print("1. Save Game")
        print("2. Load Game")
        print("3. Back to Main Menu")
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
        if self.game_settings['show_board_graphics']:
            self.display_board_graphics()

    def display_board_graphics(self):
        graphics = ""
        for i in range(self.board_size):
            if i % 10 == 0:
                graphics += "\n"
            if i in self.start_positions:
                graphics += f"[{self.players[self.start_positions.index(i)].color[0]}]"
            else:
                graphics += "[ ]"
        print("Board Graphics:" + graphics)

    def display_dice_rolls(self):
        if self.game_settings['show_dice_rolls']:
            print("Dice Rolls: ", self.dice_rolls)

    def display_turn_history(self):
        if self.game_settings['show_turn_history']:
            print("Turn History:")
            for entry in self.turn_history:
                print(f"Player {entry[0]} rolled {entry[1]} and moved to position {entry[2]}")

    def display_player_profiles(self):
        if self.game_settings['show_player_profiles']:
            print("Player Profiles:")
            for color, profile in self.player_profiles.items():
                print(f"Player {color} - Games Played: {profile['games_played']}, Games Won: {profile['games_won']}, Average Roll: {profile['average_roll']:.2f}, Longest Turn: {profile['longest_turn']}")

    def display_token_history(self):
        print("Token History:")
        for color, history in self.token_history.items():
            print(f"Token {color} history: {history}")

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
        self.__init__(self.num_players)
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
    def move_token_(self, token, steps):
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
                self.token_history[token.color].append((steps, token.position))
                self.update_player_profile(token.color, steps)
        self.turn_history.append((self.players[self.current_player].color, steps, token.position))

    def handle_special__space(self, token, action):
        if action == 'Skip':
            self.current_player = (self.current_player + 1) % self.num_players
        elif action == 'Reverse':
            self.players.reverse()
        elif action == 'Extra':
            extra_rolls = self.roll_dice(1)
            self.move_token(token, extra_rolls[0])

    def check_for_landing_(self, token):
        for other_token in self.players:
            if other_token != token and other_token.position == token.position and not other_token.safe_zone:
                other_token.home = True
                other_token.position = 0

    def show_main_menu(self):
        print("Main Menu:")
        print("1. Start New Game")
        print("2. Load Game")
        print("3. Settings")
        print("4. Quit")

    def show_save_load_menu(self):
        print("Save/Load Menu:")
        print("1. Save Game")
        print("2. Load Game")
        print("3. Back to Main Menu")

    def show_settings_menu(self):
        print("Settings Menu:")
        print("1. Toggle Show Dice Rolls")
        print("2. Toggle Show Turn History")
        print("3. Toggle Show Player Profiles")
        print("4. Toggle Show Board Graphics")
        print("5. Toggle Extra Dice Roll")
        print("6. Toggle Reverse Order")
        print("7. Toggle Challenge Mode")
        print("8. Back to Main Menu")

    def handle_main_menu(self):
        while True:
            self.show_main_menu()
            choice = input("Enter choice: ")
            if choice == '1':
                self.start_new_game()
            elif choice == '2':
                self.load_game_menu()
            elif choice == '3':
                self.settings_menu()
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")

    def handle_save_load_menu(self):
        while True:
            self.show_save_load_menu()
            choice = input("Enter choice: ")
            if choice == '1':
                filename = input("Enter filename to save: ")
                self.save_game(filename)
            elif choice == '2':
                filename = input("Enter filename to load: ")
                self.load_game(filename)
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")

    def settings_menu(self):
        while True:
            self.show_settings_menu()
            choice = input("Enter choice: ")
            if choice == '1':
                self.game_settings['show_dice_rolls'] = not self.game_settings['show_dice_rolls']
            elif choice == '2':
                self.game_settings['show_turn_history'] = not self.game_settings['show_turn_history']
            elif choice == '3':
                self.game_settings['show_player_profiles'] = not self.game_settings['show_player_profiles']
            elif choice == '4':
                self.game_settings['show_board_graphics'] = not self.game_settings['show_board_graphics']
            elif choice == '5':
                self.custom_rules['extra_dice_roll'] = not self.custom_rules['extra_dice_roll']
            elif choice == '6':
                self.custom_rules['reverse_order'] = not self.custom_rules['reverse_order']
            elif choice == '7':
                self.custom_rules['challenge_mode'] = not self.custom_rules['challenge_mode']
            elif choice == '8':
                break
            else:
                print("Invalid choice. Please try again.")

    def start_new_game(self):
        num_players = int(input("Enter number of players (2-4): "))
        self.__init__(num_players)
        self.play_game()

    def load_game_menu(self):
        self.handle_save_load_menu()
        self.play_game()

    def play_game(self):
        rounds = 0
        while not self.winner:
            self.player_turn()
            self.display_board()
            self.display_dice_rolls()
            self.display_turn_history()
            self.display_player_profiles()
            self.display_token_history()
            print(f"Round {rounds}: {self.get_positions()}")
            rounds += 1
        print(f"The winner is {self.winner}!")
        self.save_game('ludo_game_state.json')
        print("Game state saved.")

def main():
    game = Ludo()
    game.handle_main_menu()

if __name__ == "__main__":
    main()
