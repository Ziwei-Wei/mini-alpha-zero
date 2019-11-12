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

    # assume it should be killed by opponent, meaning 0 liberty!
    def __del__(self):
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
        group_positions = np.zeros([self.x, self.x])
        index = 1
        for group in self.groups:
            for position in group.member_positions:
                group_positions[position[0], position[1]] = index
            index += 1
        print(group_positions)

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
            color = self.board[position]
            self.free_map[position] = self.__is_empty_free(
                position[0], position[1], color)

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

    def __is_bound(self, x: int, y: int):
        return x % self.x == x and y % self.y == y

    # assume a position is empty, check if we can put a new stone there
    def __is_empty_free(self, x: int, y: int, color: int):
        # can not place in ko
        if color == BLACK:
            if (x, y) in self.ko[BLACK]:
                return False
        elif color == WHITE:
            if (x, y) in self.ko[BLACK]:
                return False
        else:
            raise ValueError("wrong color")

        # count neighbors
        neighbors_count = self.count_neighbors(x, y)

        # can not suicide
        if neighbors_count["diff"] == neighbors_count["total"]:
            neighbor_groups = self.get_neighbors_groups(x, y)
            for group in neighbor_groups:
                if group.get_liberty() == 1:
                    return True
            return False
        else:
            return True


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
            neighbor_groups = self.board.get_neighbors_groups(x, y)
            same_color_groups = set(new_group)

            # update liberty for neighbor groups with different color, delete 0 liberty groups
            killed = False
            for group in neighbor_groups:
                if group.color == -color:
                    group.liberty_positions.remove((x, y))
                    if len(group.liberty_positions) == 0:
                        killed = True
                        if len(group.member_positions) == 1:
                            self.board.ko[color].append((x, y))
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

    def is_movable(self):
        return self.board.count_free() > 0

    def print(self, free_map=False, ko=False, group_map=False):
        self.board.print(free_map, ko, group_map)

    def start(self, print_process=False):
        pass_count = 0
        free_map = False
        ko = False
        group_map = False
        if print_process == True:
            free_map = True
            ko = True
            group_map = True
        while pass_count < 2:
            self.print(free_map, ko, group_map)
            next_color = ""

            if self.next_move == BLACK:
                next_color = "black"
            elif self.next_move == WHITE:
                next_color = "white"
            else:
                raise ValueError("wrong color")

            if self.is_movable() == True:
                pass_count = 0
                self.print("{} will move next...".format(next_color))
                print("enter x and y for next move in {}:".format(next_color))
                x = input("x = ")
                y = input("y = ")
                while self.move(x, y) == False:
                    print("invalid position!!! please re-enter.")
                    print("re-enter x and y for next move in {}:".format(next_color))
                    x = input("x = ")
                    y = input("y = ")
            else:
                pass_count += 1
                self.print("{} can only pass...".format(next_color))
                self.board.unset_ko(self.next_move)

            self.next_move *= -1

        input("Press Enter to continue...")


if __name__ == "__main__":
    go_game = Game(4, 4)
    go_game.start(True)
