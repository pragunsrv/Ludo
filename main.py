import random

class Ludo:
    def __init__(self):
        self.board = [0] * 40
        self.players = [{'position': 0, 'home': True, 'color': color} for color in ['Red', 'Green', 'Blue', 'Yellow']]
        self.current_player = 0
        self.start_positions = [0, 10, 20, 30]

    def roll_dice(self):
        return random.randint(1, 6)

    def move_player(self, player_index, steps):
        player = self.players[player_index]
        if player['home']:
            if steps == 6:
                player['home'] = False
                player['position'] = self.start_positions[player_index]
        else:
            new_position = player['position'] + steps
            if new_position < len(self.board):
                player['position'] = new_position

    def check_for_landing(self, player_index):
        player = self.players[player_index]
        for index, other_player in enumerate(self.players):
            if index != player_index and other_player['position'] == player['position']:
                other_player['home'] = True
                other_player['position'] = 0

    def play_turn(self):
        dice_roll = self.roll_dice()
        self.move_player(self.current_player, dice_roll)
        self.check_for_landing(self.current_player)
        self.current_player = (self.current_player + 1) % 4

    def get_positions(self):
        return [(player['color'], player['position']) for player in self.players]

    def is_winner(self):
        for player in self.players:
            if player['position'] == len(self.board) - 1:
                return player['color']
        return None

def main():
    game = Ludo()
    rounds = 0
    while not game.is_winner():
        game.play_turn()
        print(f"Round {rounds}: {game.get_positions()}")
        rounds += 1
    winner = game.is_winner()
    print(f"The winner is {winner}!")

if __name__ == "__main__":
    main()
