from group import Groups, Group
from board import Board
import random
import copy

WHITE = 1
EMPTY = 0
BLACK = -1


class Game:
    def __init__(self, x: int, y: int):
        self.board = Board(x, y)
        self.groups = Groups(self.board)
        self.curr_color = BLACK
        self.score = {WHITE: 0, BLACK: 0}

    # state
    def get_state(self, color: int):
        return self.board.get_state(color)

    def get_current_free_map(self):
        return self.board.get_current_free_map()

    def get_score(self):
        liberty_set = self.groups.get_all_liberty()
        score = copy.deepcopy(self.score)
        for position in liberty_set:
            if self.board.is_eye(position, BLACK) == True:
                score[BLACK] += 1
            if self.board.is_eye(position, WHITE) == True:
                score[WHITE] += 1
        return score

    # new move will adjust the free_map
    def __move(self, x: int, y: int, color: int):
        # create a new group
        new_group = Group(self.board, color)
        new_group.add_member(x, y)

        # find neighbors
        neighbors = self.board.get_neighbors(x, y)
        neighbor_groups = set()
        for position in neighbors:
            neighbor = self.groups.find_group(position)
            if neighbor != None:
                neighbor_groups.add(neighbor)
        same_color_groups = set([new_group])

        # update liberty for neighbor groups with different color, delete 0 liberty groups
        killed = False
        for group in neighbor_groups:
            if group.color == -color:
                group.liberty_positions.remove((x, y))
                # will kill
                if len(group.liberty_positions) == 0:
                    killed = True
                    if len(group.member_positions) == 1:
                        self.board.ko[color].add((x, y))
                    self.score[-color] -= len(group.member_positions)
                    self.groups.delete_group(group)
                    del group
            elif group.color == color:
                same_color_groups.add(group)
            else:
                raise ValueError("wrong color")

        # merge same groups
        self.groups.merge_groups(same_color_groups, color)

        # if there is kill then update all groups liberty board
        if killed == True:
            self.groups.update_groups_liberty()

        # update free map with
        self.groups.update_free_map(-color)
        self.score[color] += 1
        return True

    def __calculate_final_score(self):
        pass

    def move(self, x: int, y: int):
        if self.__move(x, y, self.curr_color) == True:
            self.curr_color *= -1
            return True
        return False

    def random_move(self):
        free_positions = self.board.get_free_positions()
        index = random.randint(0, len(free_positions) - 1)

        if self.__move(free_positions[index][0], free_positions[index][1], self.curr_color) == True:
            self.curr_color *= -1
            return True
        return False

    def is_movable(self):
        return self.board.count_free() > 0

    def print(self, free_map=False, ko=False, group_map=False):
        self.board.print(free_map, ko)
        if group_map == True:
            self.groups.print()

    def start(self, print_process=True, random=False):
        pass_count = 0
        while pass_count < 2:

            if print_process == True:
                self.print(True, False, False)

            next_color = ""
            if self.curr_color == BLACK:
                next_color = "black"
            elif self.curr_color == WHITE:
                next_color = "white"
            else:
                raise ValueError("wrong color")
            print("{} will move next...".format(next_color))

            if self.is_movable() == True:
                pass_count = 0
                if random == False:
                    pass_count = 0
                    print("enter x and y for next move in {}:".format(next_color))
                    x = int(input("x = "))
                    y = int(input("y = "))
                    while self.move(x, y) == False:
                        print("invalid position!!! please re-enter.")
                        print(
                            "re-enter x and y for next move in {}:".format(next_color))
                        x = int(input("x = "))
                        y = int(input("y = "))
                    print("----------------------------------------------")

                else:
                    print("next move in {}:".format(next_color))
                    while self.random_move() == False:
                        print("invalid position!!! please re-enter.")
                        print(
                            "re-enter x and y for next move in {}:".format(next_color))
                        x = int(input("x = "))
                        y = int(input("y = "))
                    print("----------------------------------------------")

            else:
                print("{} can only pass...".format(next_color))
                pass_count += 1
                self.groups.update_free_map(-self.curr_color)
                self.curr_color *= -1

            self.board.unset_ko(self.curr_color)

        # calculate score
        print(self.get_score())
        input("Press Enter to continue...")


if __name__ == "__main__":
    go_game = Game(4, 4)
    go_game.start(True, True)
