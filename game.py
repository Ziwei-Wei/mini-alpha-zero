from game_logic import Board, Groups, Group
import numpy as np

WHITE = 1
EMPTY = 0
BLACK = -1


class Game():
    symbol = {
        -1: "X",
        +0: "-",
        +1: "O"
    }

    def __init__(self, n: int):
        self.n = n

    def get_init_board(self):
        """
        Returns:
            startBoard: a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
        return np.zeros([self.n, self.n], dtype=np.int8)

    def get_board_size(self):
        """
        Returns:
            (x,y): a tuple of board dimensions
        """
        return (self.n, self.n)

    def get_action_size(self):
        """
        Returns:
            actionSize: number of all possible actions
        """
        return self.n*self.n

    def get_next_state(self, board: np.ndarray, player: int, action: int):
        """
        Returns:
            nextBoard: board after applying the move
            nextPlayer: -player
        """
        if action == -1:
            return (board, -player)

        b = Board(self.n, self.n)
        b.board = np.copy(board)
        move = (int(action/self.n), action % self.n)
        b.add_stone(move, player)
        return b.board, -player

    def get_valid_moves(self, board: np.ndarray, player: int):
        """
        Returns:
            valid move vector
        """
        b = Board(self.n, self.n)
        b.board = np.copy(board)
        return b.get_valid_moves(player).ravel()

    def check_is_end(self, board: np.ndarray, player: int):
        """
        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.

        """
        b = Board(self.n, self.n)
        b.board = np.copy(board)

        if b.get_valid_moves(player).ravel().sum() == 0 and b.get_valid_moves(-player).ravel().sum() == 0:
            score = b.get_score()
            if score[player] > score[-player]:
                return 1
            elif score[player] < score[-player]:
                return -1
            else:
                return 1e-12
        else:
            return 0

    def get_current_win_lose(self, board: np.ndarray, player: int):
        """
        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.

        """
        b = Board(self.n, self.n)
        b.board = np.copy(board)

        score = b.get_score()
        if score[player] > score[-player]:
            return 1
        elif score[player] < score[-player]:
            return -1
        else:
            return 1e-12

    def get_standard_board(self, board: np.ndarray, player: int):
        """
        Returns:
            a standard board for that player
        """
        return player*board

    def get_all_perspectives(self, board: np.ndarray, p: np.ndarray):
        """
        Returns:
            all sides of the board (board, p)
        """
        assert(len(p) == self.n**2)
        P = np.reshape(p, (self.n, self.n))
        l = []

        for i in range(4):
            newRotB = np.rot90(board, i)
            newRotP = np.rot90(P, i)
            l += [(newRotB, newRotP.ravel())]

            newSymB = np.fliplr(newRotB)
            newSymP = np.fliplr(newRotP)
            l += [(newSymB, newSymP.ravel())]

        return l

    def to_string(self, board: np.ndarray):
        """
        Returns: 
            board's string marshall
        """
        return board.tostring()

    @staticmethod
    def display(board):
        n = board.shape[0]
        print("   ", end="")
        for y in range(n):
            print(y, end=" ")
        print("")
        for y in range(n):
            print(y, "|", end="")
            for x in range(n):
                piece = board[y][x]
                print(Game.symbol[piece], end=" ")
            print("|")


if __name__ == "__main__":
    print("start testing")
    g = Game(4)
    b = g.get_init_board()
    Game.display(b)
    b, p = g.get_next_state(b, -1, 8)
    Game.display(b)
    b, p = g.get_next_state(b, 1, 12)
    Game.display(b)
    b, p = g.get_next_state(b, -1, 13)

    v = g.get_valid_moves(b, 1)
    print(v)
    v = g.get_valid_moves(b, -1)
    print(v)
    print(g.get_current_win_lose(b, 1))
    Game.display(b)
