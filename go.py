import numpy as np

WHITE = 1
EMPTY = 0
BLACK = -1


class group:
    def __init__(self, color):
        self.group_positions = {}
        self.liberty_positions = {}
        self.color = color

    def is_member(self, x, y):
        return (x, y) in self.group_positions

    def add_stone(self, x, y):
        self.group_positions[(x, y)] = True

    def get_liberty(self):
        return len(self.liberty_positions)*color

    def add_liberty_position(self, x, y):
        self.liberty_positions[(x, y)] = True

    def contains(self, x, y):
        return (x, y) in self.group_positions


class board:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.black_groups = []
        self.white_groups = []
        self.map = {(i, j): None for i in range(x) for j in range(y)}

        self.co = []

        self.positions = {(i, j): EMPTY for i in range(x) for j in range(y)}
        self.neighbors = {
            (x, y): list(
                filter(
                    self.__is_bound,
                    [(x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)]
                )
            ) for x, y in [(i, j) for i in range(x) for j in range(y)]
        }
        self.diagonals = {
            (x, y): list(
                filter(
                    self.__is_bound,
                    [(x - 1, y + 1), (x + 1, y + 1),
                     (x + 1, y - 1), (x - 1, y - 1)]
                )
            ) for x, y in [(i, j) for i in range(x) for j in range(y)]
        }

        self.board = np.zeros([x, y], dtype=np.int8)

    def print(self):
        print(self.board)

    def which_group(self, x, y):
        return self.map[(x, y)]

    def __is_bound(self, x, y):
        return x % self.x == x and y % self.y == y

    def get_neighbors_count(self, x, y):
        same = 0
        diff = 0
        for neighbor in self.neighbors[(x, y)]:
            if self.positions[neighbor] == self.positions[(x, y)]:
                same += 1
            if self.positions[neighbor] == -self.positions[(x, y)]:
                diff += 1
        return [same, diff]

    def get_diagonals_count(self, x, y):
        same = 0
        diff = 0
        for diagonal in self.diagonals[(x, y)]:
            if self.diagonals[neighbor] == self.diagonals[(x, y)]:
                same += 1
            if self.diagonals[neighbor] == -self.diagonals[(x, y)]:
                diff += 1
        return [same, diff]

    def get_neighbors_liberty(self, x, y):
        liberty = []
        for neighbor in self.neighbors[(x, y)]:
            group = self.which_group(x, y)
            if group != None:
                liberty.append(group.get_liberty())
            else:
                liberty.append(4)
        return liberty


class game:
    def __init__(self, x, y):
        self.board = board(x, y)
        self.next_move = BLACK

    def __is_movable(self, x, y):
        neighbors_count = self.board.get_neighbors_count(x, y)
        if neighbors_count[1] == 4:
            diagonals_count = self.board.get_diagonals_count(x, y)
            if diagonals_count[0] == 2:
        pass

    def __black_move(self, x, y):
        if self.board.positions[(x, y)] == EMPTY:

            return True
        else:
            return False
        pass

    def __white_move(self, x, y):
        pass

    def move(self, x, y):
        if self.next_move == BLACK:
            if self.__black_move(x, y) == True:
                self.next_move *= -1
                return True
        elif self.next_move == WHITE:
            if self.__white_move(x, y) == True:
                self.next_move *= -1
                return True
        else:
            raise ValueError("should be black or white move")
        return False

    def start(self):
        pass
