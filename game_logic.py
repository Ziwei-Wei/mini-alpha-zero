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
                     (x - 1, y - 1), (x - 1, y + 1)]
                )
            ) for x, y in [(i, j) for i in range(x) for j in range(y)]
        }

    '''
    <- methods about positions and ko in board ->
    '''

    def get_score(self):
        white = 0
        black = 0
        for position, color in np.ndenumerate(self.board):
            if color == EMPTY:
                if self.is_eye(position, WHITE) == True:
                    white += 1
                if self.is_eye(position, BLACK) == True:
                    black += 1
            else:
                if color == WHITE:
                    white += 1
                if color == BLACK:
                    black += 1
        return {WHITE: white, BLACK: black}

    def get_valid_moves(self, player: int):
        '''
        return: valid moves for current board
        '''
        groups = Groups(self)
        history = np.zeros([self.x, self.y], dtype=np.int8)
        for position, color in np.ndenumerate(self.board):
            if color != EMPTY and history[position[0], position[1]] == 0:
                group_position_set = set()
                buffer = []
                buffer.append(position)
                while len(buffer) > 0:
                    curr = buffer.pop()
                    group_position_set.add(curr)
                    history[curr] = 1
                    for neighbor in self.neighbors[curr]:
                        if self.board[neighbor] == color and history[neighbor] == 0:
                            buffer.append(neighbor)

                group = Group(self, color)
                group.position_set = group_position_set
                groups.add_group(group)

        groups.update_groups_liberty()
        return groups.calculate_free_map(player)

    def is_alive_eye(self, position: tuple, color: int):
        same = 0
        total = 0
        for p in self.neighbors[position]:
            total += 1
            if self.board[p] == color:
                same += 1
        for p in self.diagonal[position]:
            total += 1
            if self.board[p] == color:
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

    def get_size(self):
        return (self.x, self.y)

    # add a new stone on board, only when there is empty space
    def add_stone(self, position: tuple, color: int):
        self.board[position] = color
        groups = Groups(self)
        history = np.zeros([self.x, self.y], dtype=np.int8)
        for pos, c in np.ndenumerate(self.board):
            if c != EMPTY and history[pos] == 0:
                group_position_set = set()
                buffer = []
                buffer.append(pos)
                while len(buffer) > 0:
                    curr = buffer.pop()
                    group_position_set.add(curr)
                    history[curr] = 1
                    for neighbor in self.neighbors[curr]:
                        if self.board[neighbor] == c and history[neighbor] == 0:
                            buffer.append(neighbor)

                group = Group(self, c)
                group.position_set = group_position_set
                groups.add_group(group)

        groups.update_groups_liberty()
        groups.kill_dead_group()
        self.board[position] = color

    # remove a stone from board(killed)
    def remove_stone(self, position: tuple, color: int):
        self.board[position] = EMPTY

    # set a position to be ko
    def set_ko(self, position: tuple, color: int):
        self.ko[color].add(position)

    # unset a ko position
    def unset_ko(self, color: int):
        self.ko[color].clear()

    '''
    <- methods about neighbors in board ->
    '''

    # assume i will put a stone here
    def count_neighbors(self, position: tuple, color: int):
        same = 0
        diff = 0
        total = 0
        for neighbor in self.neighbors[position]:
            total += 1
            if self.board[neighbor] == color:
                same += 1
            if self.board[neighbor] == -color:
                diff += 1
        return {"same": same, "diff": diff, "total": total}

    '''
    <- utilities ->
    '''

    def __is_bound(self, position: tuple):
        return position[0] % self.x == position[0] and position[1] % self.y == position[1]


class Groups:
    def __init__(self, board: "Board"):
        self.board = board
        self.group_set = set()
        self.position_to_group = {}

    def kill_dead_group(self):
        groups_to_kill = set()
        for group in self.group_set:
            if len(group.liberty_positions) == 0:
                groups_to_kill.add(group)
        self.group_set.difference_update(groups_to_kill)
        for group in groups_to_kill:
            group.kill_self()
        del groups_to_kill

    def get_all_liberty(self):
        liberty_set = set()
        for group in self.group_set:
            liberty_set.update(group.liberty_positions)
        return liberty_set

    # update the free map
    def update_free_map(self, color: int):
        liberty_positions = set()
        for group in self.group_set:
            liberty_positions.update(group.liberty_positions)

        for position in liberty_positions:
            self.board.free_map[position] = self.__is_empty_free(
                position, color)

    def calculate_free_map(self, color: int):
        free_map = np.ones([self.board.x, self.board.y], dtype=np.int8)
        for position in self.position_to_group:
            free_map[position] = 0

        liberty_positions = set()
        for group in self.group_set:
            liberty_positions.update(group.liberty_positions)

        for position in liberty_positions:
            free_map[position] = self.__is_empty_free(
                position, color)
        return free_map

    def add_group(self, new: 'Group'):
        if new not in self.group_set:
            self.group_set.add(new)
            for position in new.position_set:
                self.position_to_group[position] = new

    def delete_group(self, old: 'Group'):
        self.remove_group(old)
        old.kill_self()

    def remove_group(self, old: 'Group'):
        if old in self.group_set:
            for position in old.position_set:
                try:
                    del self.position_to_group[position]
                except KeyError:
                    print("Key not found")

        self.group_set.discard(old)

    def find_group(self, position):
        return self.position_to_group.get(position)

    # assume all groups are mergeable, merge them to one group
    def merge_groups(self, group_list: set, color: int):
        if len(group_list) == 1:
            group = group_list.pop()
            self.add_group(group)
            return
        else:
            merged = Group(self.board, color)
            for curr_group in group_list:
                merged.add_group(curr_group)
                self.remove_group(curr_group)
            self.add_group(merged)
            return

    # update all groups liberty positions
    def update_groups_liberty(self):
        for group in self.group_set:
            group.update_liberty()

    def get_neighbors_liberties(self, x: int, y: int):
        liberties = []
        for neighbor in self.board.get_neighbors(x, y):
            group = self.position_to_group[neighbor]
            if group != None:
                liberties.append(group.get_liberty())
            else:
                liberties.append(4)
        return liberties

    def print(self):
        print("---> groups:")
        for group in self.group_set:
            group.print()

    def get_neighbors_groups(self, x: int, y: int):
        neighbors_groups = set()
        for neighbor in self.board.neighbors[x, y]:
            if self.board.board[neighbor] != EMPTY:
                group = self.position_to_group[neighbor]
                neighbors_groups.add(group)
        return neighbors_groups

    # assume a position is empty, check if we can put a new stone there
    def __is_empty_free(self, position: tuple, color: int):
        x = position[0]
        y = position[1]
        # can not place in ko
        if color == BLACK:
            if (x, y) in self.board.ko[BLACK]:
                return False
        elif color == WHITE:
            if (x, y) in self.board.ko[WHITE]:
                return False
        else:
            raise ValueError("wrong color")

        count = self.board.count_neighbors(position, color)
        neighbor_groups = self.get_neighbors_groups(x, y)
        same_color_count = 0
        same_color_liberty = 0
        for group in neighbor_groups:
            # can not suiside
            if group.color == color:
                same_color_count += 1
                same_color_liberty += group.get_liberty()
            # can kill
            elif group.color == -color:
                if group.get_liberty() == 1:
                    return True
            else:
                print("error color")

        # can not suicide and can not be eye
        if count["diff"] == count["total"] or (same_color_count == same_color_liberty and count["total"] == count["diff"] + count["same"]) or self.board.is_alive_eye((x, y), color):
            return False
        else:
            return True


class Group:
    def __init__(self, board: "Board", color: int):
        self.board = board
        self.color = color
        self.position_set = set()
        self.liberty_positions = set()

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __hash__(self):
        return hash(self.__repr__())

    def print(self):
        print_board = np.zeros([self.board.x, self.board.y], dtype=np.int8)
        for position in self.position_set:
            print_board[position[0], position[1]] = 1
        for position in self.liberty_positions:
            print_board[position[0], position[1]] = -1
        print(print_board)

    def is_member(self, x: int, y: int):
        return (x, y) in self.position_set

    def add_group(self, group: "Group"):
        self.position_set.update(group.position_set)
        self.liberty_positions.update(group.liberty_positions)
        self.liberty_positions.difference_update(self.position_set)

    # add_member assume the new member is free to add, and neighbor to the current group

    def add_position(self, position: tuple):
        self.position_set.add(position)
        for position in self.board.neighbors[position]:
            if self.board.board[position] == EMPTY:
                self.liberty_positions.add(position)

    def get_liberty(self):
        return len(self.liberty_positions)

    def update_liberty(self):
        self.liberty_positions = set()
        for member in self.position_set:
            for position in self.board.neighbors[member]:
                if self.board.board[position] == EMPTY:
                    self.liberty_positions.add(position)

    def contains(self, x: int, y: int):
        return (x, y) in self.position_set

    def kill_self(self):
        for member in self.position_set:
            self.board.remove_stone(member, self.color)
        if len(self.position_set) == 1:
            member = self.position_set.pop()
            self.board.set_ko(member, self.color)
