import random

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
        self.token_throws = {color: [] for color in ['Red', 'Green', 'Blue', 'Yellow']} # Track each token's moves

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
                self.token_throws[token.color].append(steps)  # Log the move

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

    def get_positions(self):
        return [(token.color, token.position, token.safe_zone, token.finished, token.token_id) for token in self.players]

    def display_board(self):
        board_display = ['.' for _ in range(self.board_size)]
        for token in self.players:
            if token.position < self.board_size:
                board_display[token.position] = token.color[0]
        print("Board: " + ''.join(board_display))

    def display_dice_rolls(self):
        print("Dice Rolls: ", self.dice_rolls)

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
            file.write(f"Current Player: {self.current_player}\n")
            file.write(f"Winner: {self.winner}\n")
            file.write(f"Dice Rolls: {self.dice_rolls}\n")
            file.write(f"Token Throws: {self.token_throws}\n")
            for idx, token in enumerate(self.players):
                file.write(f"Player {idx} - Color: {token.color}, Position: {token.position}, Home: {token.home}, Finished: {token.finished}\n")

    def load_game(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            self.current_player = int(lines[0].strip().split(": ")[1])
            self.winner = lines[1].strip().split(": ")[1]
            self.dice_rolls = eval(lines[2].strip().split(": ")[1])
            self.token_throws = eval(lines[3].strip().split(": ")[1])
            for idx, line in enumerate(lines[4:]):
                color, position, home, finished = line.split(", ")[1:5]
                color = color.split(": ")[1]
                position = int(position.split(": ")[1])
                home = home.split(": ")[1] == 'True'
                finished = finished.split(": ")[1] == 'True'
                self.players[idx].color = color
                self.players[idx].position = position
                self.players[idx].home = home
                self.players[idx].finished = finished

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
        print(f"Round {rounds}: {game.get_positions()}")
        rounds += 1
    print(f"The winner is {game.winner}!")
    game.save_game('ludo_game_state.txt')
    print("Game state saved.")

if __name__ == "__main__":
    main()
