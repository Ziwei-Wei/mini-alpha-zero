import numpy as np

WHITE = 1
EMPTY = 0
BLACK = -1


class Board:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.ko = {BLACK: set(), WHITE: set()}
        self.board = np.zeros([x, y], dtype=np.int8)
        self.free_map = {(i, j): True for i in range(x) for j in range(y)}
        self.neighbors = {
            (x, y): list(
                filter(
                    self.__is_bound,
                    [(x, y + 1), (x + 1, y),
                     (x, y - 1), (x - 1, y)]
                )
            ) for x, y in [(i, j) for i in range(x) for j in range(y)]
        }
        self.diagonal = {
            (x, y): list(
                filter(
                    self.__is_bound,
                    [(x + 1, y + 1), (x + 1, y - 1),
                     (x - 1, y - 1), (x - 1, y - 1)]
                )
            ) for x, y in [(i, j) for i in range(x) for j in range(y)]
        }

    '''
    <- methods about positions and ko in board ->
    '''

    # check if the position is empty

    def is_empty(self, x: int, y: int):
        return self.board[x, y] == EMPTY

    def is_alive_eye(self, position: tuple, color: int):
        same = 0
        total = 0
        for position in self.neighbors[position]:
            total += 1
            if self.board[position] == color:
                same += 1
        for position in self.diagonal[position]:
            total += 1
            if self.board[position] == color:
                same += 1
        if total == same:
            return True
        elif total == 8 and same == 7:
            return True
        else:
            return False

    def is_eye(self, position: tuple, color: int):
        same = 0
        total = 0
        for position in self.neighbors[position]:
            total += 1
            if self.board[position] == color:
                same += 1
        if total == same:
            return True
        else:
            return False

    def is_suiside(self, position: tuple, color: int):
        diff = 0
        total = 0
        for position in self.neighbors[position]:
            total += 1
            if self.board[position] == -color:
                diff += 1
        return total == diff

    # add a new stone on board, only when there is empty space
    def add_stone(self, x: int, y: int, color: int):
        if self.free_map[(x, y)] == True:
            self.board[x, y] = color
            self.free_map[(x, y)] = False
            return True
        else:
            return False

    # remove a stone from board(killed)
    def remove_stone(self, x: int, y: int, color: int):
        self.board[x, y] = EMPTY

    # set a position to be ko
    def set_ko(self, position: tuple, color: int):
        self.ko[color].add(position)

    # unset a ko position
    def unset_ko(self, color: int):
        self.ko[color].clear()

    '''
    <- methods about free position in board ->
    '''

    # set a position to be free
    def set_free(self, position: tuple):
        self.free_map[position] = True

    # set a position to be invalid
    def unset_free(self, position: tuple):
        self.free_map[position] = False

    # count left free space to be filled
    def count_free(self):
        count = 0
        for _, is_free in self.free_map.items():
            if is_free == True:
                count += 1
        return count

    '''
    <- methods about neighbors in board ->
    '''

    def get_neighbors(self, x: int, y: int):
        return self.neighbors[(x, y)]

    # assume i will put a stone here
    def count_neighbors(self, x: int, y: int, color: int):
        same = 0
        diff = 0
        total = 0
        for neighbor in self.get_neighbors(x, y):
            if self.board[neighbor] == color:
                same += 1
            if self.board[neighbor] == -color:
                diff += 1
            total += 1
        return {"same": same, "diff": diff, "total": total}

    '''
    <- utilities ->
    '''

    def __is_bound(self, position: tuple):
        return position[0] % self.x == position[0] and position[1] % self.y == position[1]

    '''
    <- methods about printing the board ->
    '''

    def get_state(self, color: int):
        if color == BLACK:
            return self.board
        elif color == WHITE:
            return -1*self.board
        else:
            print("error color")

    def get_current_free_map(self):
        return self.free_map

    def get_free_positions(self):
        free_positions = []
        for key, value in self.free_map.items():
            if value == True:
                free_positions.append(key)
        return free_positions

    def print_board(self):
        print("-- current board:")
        print(self.board)

    def print_free_map(self):
        print("-- free positions:")
        free_map = np.ones([self.x, self.x], dtype=np.int8)
        for key, value in self.free_map.items():
            if value == False:
                free_map[key[0], key[1]] = 0
        print(free_map)

    def print_co(self):
        print("-- ko positions:")
        print(self.ko)

    def print(self, free_map=False, ko=False):
        self.print_board()
        if free_map == True:
            self.print_free_map()
        if ko == True:
            self.print_co()
