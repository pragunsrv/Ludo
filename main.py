import random

class Ludo:
    def __init__(self):
        self.board = [0] * 40
        self.players = [{'position': 0, 'home': True, 'color': color, 'safe_zone': False} for color in ['Red', 'Green', 'Blue', 'Yellow']]
        self.current_player = 0
        self.start_positions = [0, 10, 20, 30]
        self.safe_zones = set([5, 15, 25, 35]) # Example safe zones
        self.winning_positions = [39] * 4
        self.winner = None

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
                if new_position in self.safe_zones:
                    player['safe_zone'] = True
                else:
                    player['safe_zone'] = False
                player['position'] = new_position
                if player['position'] == self.winning_positions[player_index]:
                    player['home'] = True
                    player['position'] = 40 # Considered as finished

    def check_for_landing(self, player_index):
        player = self.players[player_index]
        for index, other_player in enumerate(self.players):
            if index != player_index and other_player['position'] == player['position'] and not other_player['safe_zone']:
                other_player['home'] = True
                other_player['position'] = 0

    def play_turn(self):
        if not self.winner:
            dice_roll = self.roll_dice()
            self.move_player(self.current_player, dice_roll)
            self.check_for_landing(self.current_player)
            self.check_for_winner()
            self.current_player = (self.current_player + 1) % 4

    def check_for_winner(self):
        for player in self.players:
            if player['position'] == 40:
                self.winner = player['color']

    def get_positions(self):
        return [(player['color'], player['position'], player['safe_zone']) for player in self.players]

    def display_board(self):
        board_display = ['.' for _ in range(40)]
        for player in self.players:
            if player['position'] < 40:
                board_display[player['position']] = player['color'][0]
        print("Board: " + ''.join(board_display))

def main():
    game = Ludo()
    rounds = 0
    while not game.winner:
        game.play_turn()
        game.display_board()
        print(f"Round {rounds}: {game.get_positions()}")
        rounds += 1
    print(f"The winner is {game.winner}!")

if __name__ == "__main__":
    main()
