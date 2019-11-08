import numpy as np
import math

WHITE = 1
EMPTY = 0
BLACK = -1


class group:
    def __init__(self, board, color):
        self.board = board
        self.group_positions = {}
        self.liberty_positions = {}
        self.color = color

    def is_member(self, x, y):
        return (x, y) in self.group_positions

    def add_member(self, x, y):
        self.group_positions[(x, y)] = True

    def get_liberty(self):
        return len(self.liberty_positions)*color

    def add_liberty_position(self, x, y):
        self.liberty_positions[(x, y)] = True

    def test_liberty_change(self, x, y):
        # find same color neighbor
        neighbors = self.board.neighbors[(x, y)]
        free_positions = []
        neighbor_groups = []
        min_liberty = self.board.x * self.board.y
        for neighbor in neighbors:
            if self.board.positions[neighbor] == EMPTY:
                free_positions.append(neighbor)
            if self.board.positions[neighbor] == self.board.positions[(x, y)]:
                neighbor_groups.append(
                    self.board.map[neighbor].liberty_positions[neighbor])
                min_liberty = math.min(
                    len(self.board.map[neighbor].liberty_positions), min_liberty)

        # calculate liberty after merge
        new_liberty_positions = {}
        liberty_change = len(new_liberty_positions) - min_liberty

        for group in neighbor_groups:
            new_liberty_positions.update(group.liberty_positions)
        for position in free_positions:
            if position in new_liberty_positions:
                liberty_change -= 1
        if (x, y) in new_liberty_positions:
            liberty_change -= 1
        return liberty_change

    def contains(self, x, y):
        return (x, y) in self.group_positions


class board:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.map = {(i, j): None for i in range(x) for j in range(y)}
        self.co = {BLACK: [], WHITE: []}
        self.positions = {(i, j): EMPTY for i in range(x) for j in range(y)}
        self.neighbors = {
            (x, y): list(
                filter(
                    self.__is_bound,
                    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
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
        total = 0
        for neighbor in self.neighbors[(x, y)]:
            if self.positions[neighbor] == self.positions[(x, y)]:
                same += 1
            if self.positions[neighbor] == -self.positions[(x, y)]:
                diff += 1
            total += 1
        return {"same": same, "diff": diff, "total": total}

    def get_neighbors_by_group(self, x, y):
        neighbor_groups = []
        for neighbor in self.neighbors[(x, y)]:
            neighbor_groups.append(neighbor)
        return neighbor_groups

    def get_diagonals_count(self, x, y):
        same = 0
        diff = 0
        total = 0
        for diagonal in self.diagonals[(x, y)]:
            if self.diagonals[diagonal] == self.diagonals[(x, y)]:
                same += 1
            if self.diagonals[diagonal] == -self.diagonals[(x, y)]:
                diff += 1
            total += 1
        return {"same": same, "diff": diff, "total": total}

    def get_neighbors_liberty(self, x, y):
        liberty = []
        for neighbor in self.neighbors[(x, y)]:
            group = self.which_group(neighbor[0], neighbor[1])
            if group != None:
                liberty.append(group.get_liberty())
            else:
                liberty.append(4)
        return liberty


class game:
    def __init__(self, x, y):
        self.board = board(x, y)
        self.position_to_group = {
            (i, j): None for i in range(x) for j in range(y)
        }
        self.group_to_position = {}
        self.next_move = BLACK

    def __get_neighbor_groups(self, x, y):
        neighbor_groups = []
        for neighbor in self.board.neighbors[(x, y)]:
            if self.position_to_group[neighbor] != None:
                neighbor_groups.append(self.position_to_group[neighbor])
        return neighbor_groups

    def __is_free_for_black(self, x, y):
        # can not place in co
        if (x, y) in self.board.co[BLACK]:
            return False

        # count neighbors
        neighbors_count = self.board.get_neighbors_count(x, y)

        # can not suicide
        if neighbors_count["diff"] == neighbors_count["total"]:
            neighbor_groups = self.__get_neighbor_groups(x, y)
            for group in neighbor_groups:
                if group != None and group.get_liberty() == 1:
                    return True
            return False

        # can not reduce own liberty
        if neighbors_count["same"] = 1:
            neighbor_groups = self.__get_neighbor_groups(x, y)
            for group in neighbor_groups:
                if group != None and group.color == BLACK:

                    return True

        # when there is merge, can not reduce own liberty after merge

        return True

    def __is_free_for_white(self, x, y):
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

    def start(self, print=False):
        pass
