import random

class Ludo:
    def __init__(self):
        self.board = [0] * 40
        self.players = [0, 0, 0, 0]
        self.current_player = 0

    def roll_dice(self):
        return random.randint(1, 6)

    def move_player(self, player_index, steps):
        new_position = self.players[player_index] + steps
        if new_position < len(self.board):
            self.players[player_index] = new_position

    def play_turn(self):
        dice_roll = self.roll_dice()
        self.move_player(self.current_player, dice_roll)
        self.current_player = (self.current_player + 1) % 4

    def get_positions(self):
        return self.players

def main():
    game = Ludo()
    for _ in range(10):
        game.play_turn()
        print(game.get_positions())

if __name__ == "__main__":
    main()
