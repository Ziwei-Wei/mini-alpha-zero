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

    def print(self, x, y):
        print_board = np.zeros([x, y], dtype=np.int8)
        for position in self.member_positions:
            print_board[position[0], position[1]] = 1
        print(print_board)

    def is_member(self, x: int, y: int):
        return (x, y) in self.member_positions

    def add_group(self, group: group):
        self.member_positions.update(group.member_positions)
        self.liberty_positions.update(group.liberty_positions)

    # add_member assume the new member is free to add, and neighbor to the current group
    def add_member(self, x: int, y: int):
        self.member_positions.add((x, y))
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


class Board:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.groups = set()
        self.position_to_group = {}
        self.co = {BLACK: [], WHITE: []}

        self.free_map = {(i, j): True for i in range(x) for j in range(y)}
        self.board = np.zeros([x, y], dtype=np.int8)

        self.neighbors = {
            (x, y): list(
                filter(
                    self.__is_bound,
                    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
                )
            ) for x, y in [(i, j) for i in range(x) for j in range(y)]
        }

    def print(self):
        print(self.board)

    def __is_bound(self, x: int, y: int):
        return x % self.x == x and y % self.y == y

    def __is_EMPTY_free(self, x: int, y: int, color: int):
        # can not place in co
        if color == BLACK:
            if (x, y) in self.co[BLACK]:
                return False
        elif color == WHITE:
            if (x, y) in self.co[BLACK]:
                return False
        else:
            raise ValueError("wrong color")

        # count neighbors
        neighbors_count = self.get_neighbors_count(x, y)

        # can not suicide, can not reduce own liberty
        if neighbors_count["diff"] == neighbors_count["total"]:
            neighbor_groups = self.get_neighbor_groups(x, y)
            for group in neighbor_groups:
                if group.get_liberty() == 1:
                    return True
            return False
        else:
            return True

    def is_free(self, x: int, y: int, color: int):
        if self.board[(x, y)] != EMPTY:
            return False
        else:
            return self.__is_EMPTY_free(x, y, color)

    def is_empty(self, x: int, y: int):
        return self.board[x, y] == EMPTY

    def update_groups_liberty(self):
        for group in self.groups:
            group.update_liberty()
        pass

    def update_free_map(self, color: int):
        liberty_positions = set()
        for group in self.groups:
            liberty_positions.update(group.liberty_positions)

        for position in liberty_positions:
            color = self.board[position]
            self.free_map[position] = self.__is_EMPTY_free(
                position[0], position[1], color)

    def add_stone(self, x: int, y: int, color: int):
        self.board[x, y] = color
        self.free_map[(x, y)] = False

    # assume all groups are mergeable
    def merge_groups(self, group_list: list, color: int):
        if len(group_list) == 1:
            return group_list[0]
        merged = Group(self.board, color)
        for curr_group in group_list:
            for position in curr_group.member_positions:
                self.position_to_group[position] = merged
            merged.add_group(curr_group)
            del curr_group
        return merged

    def get_liberty(self, x: int, y: int):
        neighbors_count = self.get_neighbors_count(x, y)
        return 4 - neighbors_count["total"]

    def get_neighbors_count(self, x: int, y: int):
        same = 0
        diff = 0
        total = 0
        for neighbor in self.neighbors[(x, y)]:
            if self.board[neighbor] == self.board[(x, y)]:
                same += 1
            if self.board[neighbor] == -self.board[(x, y)]:
                diff += 1
            total += 1
        return {"same": same, "diff": diff, "total": total}

    def get_neighbor_groups(self, x: int, y: int):
        neighbor_groups = []
        for neighbor in self.neighbors[(x, y)]:
            if self.board[neighbor] != EMPTY:
                group = self.position_to_group[neighbor]
                neighbor_groups.append(group)
        return neighbor_groups

    def get_neighbors_liberty(self, x: int, y: int):
        liberty = []
        for neighbor in self.neighbors[(x, y)]:
            group = self.position_to_group[neighbor]
            if group != None:
                liberty.append(group.get_liberty())
            else:
                liberty.append(4)
        return liberty


class Game:
    def __init__(self, x: int, y: int):
        self.board = Board(x, y)
        self.next_move = BLACK

    # new move will adjust the free_map
    def __move(self, x: int, y: int, color: int):
        if self.board.is_free(x, y, color):
            # create a new group
            new_group = Group(color, self.board)
            new_group.add_member(x, y)

            # find neighbor groups
            neighbor_groups = self.board.get_neighbor_groups(x, y)
            same_color_groups = set(new_group)

            # update liberty for neighbor groups with different color, delete 0 liberty groups
            killed = False
            for group in neighbor_groups:
                if group.color == -color:
                    group.liberty_positions.remove((x, y))
                    if len(group.liberty_positions) == 0:
                        killed = True
                        if len(group.member_positions) == 1:
                            self.board.co[color].append((x, y))
                        del group
                elif group.color == color:
                    same_color_groups.add(group)
                else:
                    raise ValueError("wrong color")

            # merge same groups
            self.board.merge_groups(same_color_groups, color)

            # if there is kill then update all groups liberty board
            if killed == True:
                self.board.update_groups_liberty()

            # update free map with
            self.board.update_free_map(-color)
        else:
            return False

    def move(self, x: int, y: int):
        if self.__move(x, y, self.next_move) == True:
            self.next_move *= -1
            return True
        return False

    def start(self, print: bool = False):
        pass
