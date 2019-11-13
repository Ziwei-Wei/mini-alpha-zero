import numpy as np

WHITE = 1
EMPTY = 0
BLACK = -1


class Group:
    def __init__(self, board: "Board", color: int):
        self.board = board
        self.color = color
        self.member_positions = set()
        self.liberty_positions = set()
        self.board.groups.add(self)

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __hash__(self):
        return hash(self.__repr__())

    def print(self):
        print_board = np.zeros([self.board.x, self.board.y], dtype=np.int8)
        for position in self.member_positions:
            print_board[position[0], position[1]] = 1
        for position in self.liberty_positions:
            print_board[position[0], position[1]] = -1
        print(print_board)

    def is_member(self, x: int, y: int):
        return (x, y) in self.member_positions

    def merge_group(self, group: "Group"):
        print("merge:")
        print(self)
        print(group)
        print(self.board.groups)
        self.member_positions.update(group.member_positions)
        self.liberty_positions.update(group.liberty_positions)
        self.liberty_positions.difference_update(self.member_positions)

        for position in group.member_positions:
            self.board.position_to_group[position] = self
        self.board.groups.remove(group)
        print("after merge:")
        print(self.board.groups)

    # add_member assume the new member is free to add, and neighbor to the current group
    def add_member(self, x: int, y: int):
        self.member_positions.add((x, y))
        self.map_to_board((x, y))
        for position in self.board.neighbors[(x, y)]:
            if self.board.board[position] == EMPTY:
                self.liberty_positions.add(position)

    def get_liberty(self):
        return len(self.liberty_positions)*self.color

    def update_liberty(self):
        self.liberty_positions = set()
        for member in self.member_positions:
            for position in self.board.neighbors[member]:
                if self.board.is_empty(position[0], position[1]):
                    self.liberty_positions.add(position)

    def contains(self, x: int, y: int):
        return (x, y) in self.member_positions

    def map_to_board(self, position: tuple):
        self.board.position_to_group[position] = self

    def remove_self(self):
        self.board.groups.remove(self)
        for member in self.member_positions:
            self.board.remove_stone(member[0], member[1], self.color)
        for member in self.member_positions:
            self.board.set_free(member)
        if len(self.member_positions) == 1:
            member = self.member_positions.pop()
            self.board.unset_free(member)
            self.board.set_ko(member, self.color)


class Board:
    def __init__(self, x: int, y: int):
        # meta data
        self.x = x
        self.y = y

        # groups and utility
        self.groups = set()
        self.position_to_group = {}
        self.ko = {BLACK: set(), WHITE: set()}
        self.eyes = {BLACK: set(), WHITE: set()}

        # core data structure
        self.free_map = {(i, j): True for i in range(x) for j in range(y)}

        self.board = np.zeros([x, y], dtype=np.int8)

        # for reference
        self.neighbors = {
            (x, y): list(
                filter(
                    self.__is_bound,
                    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
                )
            ) for x, y in [(i, j) for i in range(x) for j in range(y)]
        }

    '''
    <- methods about printing the board ->
    '''

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

    def print_groups(self):
        print("-- group positions:")
        print(self.groups)
        group_positions = np.zeros([self.x, self.x], dtype=np.int8)
        index = 1
        for group in self.groups:
            for position in group.member_positions:
                group_positions[position[0], position[1]] = index
            index += 1
        print(group_positions)

    def print_each_groups(self):
        index = 0
        for group in self.groups:
            group.print()
            index += 1

    def print(self, free_map=False, ko=False, group_map=False):
        self.print_board()
        if free_map == True:
            self.print_free_map()
        if ko == True:
            self.print_co()
        if group_map == True:
            self.print_groups()

    '''
    <- methods about positions and ko in board ->
    '''

    # check if the position is empty

    def is_empty(self, x: int, y: int):
        return self.board[x, y] == EMPTY

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

    # check if we can put a new stone in the position
    def is_free(self, x: int, y: int, color: int):
        if self.is_empty(x, y):
            return self.__is_empty_free(x, y, color)
        else:
            return False

    # update the free map
    def update_free_map(self, color: int):
        liberty_positions = set()
        for group in self.groups:
            liberty_positions.update(group.liberty_positions)

        for position in liberty_positions:
            self.free_map[position] = self.__is_empty_free(
                position[0], position[1], -color)

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
    def estimate_neighbors(self, x: int, y: int, color: int):
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

    def count_neighbors(self, x: int, y: int):
        same = 0
        diff = 0
        total = 0
        for neighbor in self.get_neighbors(x, y):
            if self.board[neighbor] == self.board[(x, y)]:
                same += 1
            if self.board[neighbor] == -self.board[(x, y)]:
                diff += 1
            total += 1
        return {"same": same, "diff": diff, "total": total}

    def get_neighbors_groups(self, x: int, y: int):
        neighbors_groups = []
        for neighbor in self.get_neighbors(x, y):
            if self.board[neighbor] != EMPTY:
                group = self.position_to_group[neighbor]
                neighbors_groups.append(group)
        return neighbors_groups

    '''
    <- methods about groups in board ->
    '''

    # assume all groups are mergeable, merge them to one group
    def merge_groups(self, group_list: set, color: int):
        if len(group_list) == 1:
            return group_list.pop()
        merged = Group(self, color)
        for curr_group in group_list:
            curr_group.print()
            merged.merge_group(curr_group)
        return merged

    # update all groups liberty positions
    def update_groups_liberty(self):
        for group in self.groups:
            group.update_liberty()

    def get_neighbors_liberties(self, x: int, y: int):
        liberties = []
        for neighbor in self.get_neighbors(x, y):
            group = self.position_to_group[neighbor]
            if group != None:
                liberties.append(group.get_liberty())
            else:
                liberties.append(4)
        return liberties

    '''
    <- utilities ->
    '''

    def __get_liberty(self, x: int, y: int):
        neighbors_count = self.count_neighbors(x, y)
        return 4 - neighbors_count["total"]

    def __is_bound(self, position: tuple):
        return position[0] % self.x == position[0] and position[1] % self.y == position[1]

    # assume a position is empty, check if we can put a new stone there
    def __is_empty_free(self, x: int, y: int, color: int):
        # can not place in ko
        if color == BLACK:
            if (x, y) in self.ko[BLACK]:
                return False
        elif color == WHITE:
            if (x, y) in self.ko[WHITE]:
                return False
        else:
            raise ValueError("wrong color")

        # count neighbors
        neighbors_count = self.estimate_neighbors(x, y, color)

        # can not suicide
        if neighbors_count["diff"] == neighbors_count["total"]:
            neighbor_groups = self.get_neighbors_groups(x, y)
            for group in neighbor_groups:
                if group.get_liberty() == 1:
                    return True
            return False
        else:
            return True
