from game import Game
import numpy as np
import random


class RandomPlayer:
    def __init__(self, game: 'Game', player: int):
        self.player = player
        self.game = game

    def play(self, board):
        if self.game.check_is_end(board, self.player) == 0:
            moves = self.game.get_valid_moves(board, self.player)
            valids = []
            for move, validity in np.ndenumerate(moves):
                if validity == 1:
                    valids += move
            if len(valids) > 1:
                next_move = random.randint(0, len(valids) - 1)
            elif len(valids) == 1:
                next_move = 0
            else:
                return board

            board, _ = self.game.get_next_state(
                board, self.player, valids[next_move])
            return board
        else:
            return None


if __name__ == "__main__":
    g = Game(4)
    p1 = RandomPlayer(g, 1)
    p2 = RandomPlayer(g, -1)
    b = g.get_init_board()
    while True:
        curr_board = p1.play(b)
        if curr_board is None:
            break
        else:
            b = curr_board

        curr_board = p2.play(b)
        if curr_board is None:
            break
        else:
            b = curr_board

        Game.display(b)
    Game.display(b)
    print("winner:")
    print(g.check_is_end(b, 1))
