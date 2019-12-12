import numpy as np
from board import Board

WHITE = 1
EMPTY = 0
BLACK = -1


class Groups:
    def __init__(self, board: "Board"):
        self.board = board
        self.groups = set()
        self.position_to_group = {}

    def get_all_liberty(self):
        liberty_set = set()
        for group in self.groups:
            liberty_set.update(group.liberty_positions)
        return liberty_set

    # update the free map
    def update_free_map(self, color: int):
        liberty_positions = set()
        for group in self.groups:
            liberty_positions.update(group.liberty_positions)

        for position in liberty_positions:
            self.board.free_map[position] = self.__is_empty_free(
                position[0], position[1], color)

    def add_group(self, new: 'Group'):
        if new not in self.groups:
            self.groups.add(new)
            for position in new.member_positions:
                self.position_to_group[position] = new

    def delete_group(self, old: 'Group'):
        self.remove_group(old)
        old.kill_self()

    def remove_group(self, old: 'Group'):
        if old in self.groups:
            for position in old.member_positions:
                try:
                    del self.position_to_group[position]
                except KeyError:
                    print("Key not found")

        self.groups.discard(old)

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
        for group in self.groups:
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
        for group in self.groups:
            group.print()

    def get_neighbors_groups(self, x: int, y: int):
        neighbors_groups = set()
        for neighbor in self.board.get_neighbors(x, y):
            if self.board.board[neighbor] != EMPTY:
                group = self.position_to_group[neighbor]
                neighbors_groups.add(group)
        return neighbors_groups

    # assume a position is empty, check if we can put a new stone there
    def __is_empty_free(self, x: int, y: int, color: int):
        # can not place in ko
        if color == BLACK:
            if (x, y) in self.board.ko[BLACK]:
                return False
        elif color == WHITE:
            if (x, y) in self.board.ko[WHITE]:
                return False
        else:
            raise ValueError("wrong color")

        count = self.board.count_neighbors(x, y, color)
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
        self.member_positions = set()
        self.liberty_positions = set()

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

    def add_group(self, group: "Group"):
        self.member_positions.update(group.member_positions)
        self.liberty_positions.update(group.liberty_positions)
        self.liberty_positions.difference_update(self.member_positions)

    # add_member assume the new member is free to add, and neighbor to the current group

    def add_member(self, x: int, y: int):
        self.member_positions.add((x, y))
        self.board.add_stone(x, y, self.color)
        for position in self.board.neighbors[(x, y)]:
            if self.board.board[position] == EMPTY:
                self.liberty_positions.add(position)

    def get_liberty(self):
        return len(self.liberty_positions)

    def update_liberty(self):
        self.liberty_positions = set()
        for member in self.member_positions:
            for position in self.board.neighbors[member]:
                if self.board.is_empty(position[0], position[1]):
                    self.liberty_positions.add(position)

    def contains(self, x: int, y: int):
        return (x, y) in self.member_positions

    def kill_self(self):
        for member in self.member_positions:
            self.board.remove_stone(member[0], member[1], self.color)
        for member in self.member_positions:
            self.board.set_free(member)
        if len(self.member_positions) == 1:
            member = self.member_positions.pop()
            self.board.unset_free(member)
            self.board.set_ko(member, self.color)
