from game_logic import Group
from game_logic import Board

WHITE = 1
EMPTY = 0
BLACK = -1


class Game:
    def __init__(self, x: int, y: int):
        self.board = Board(x, y)
        self.next_move = BLACK

    # new move will adjust the free_map
    def __move(self, x: int, y: int, color: int):
        if self.board.is_free(x, y, color):
            # create a new group
            self.board.add_stone(x, y, color)
            new_group = Group(self.board, color)
            new_group.add_member(x, y)

            # find neighbor groups
            neighbor_groups = self.board.get_neighbors_groups(x, y)
            same_color_groups = set([new_group])

            # update liberty for neighbor groups with different color, delete 0 liberty groups
            killed = False
            for group in neighbor_groups:
                if group.color == -color:
                    group.liberty_positions.remove((x, y))
                    group.print()
                    if len(group.liberty_positions) == 0:
                        print("here")
                        killed = True
                        if len(group.member_positions) == 1:
                            self.board.ko[color].add((x, y))
                        group.remove_self()
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
            self.board.update_free_map(color)
            return True
        else:
            return False

    def __calculate_final_score(self):
        pass

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
            print("----------------------------------------------")
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
                print("{} will move next...".format(next_color))
                print("enter x and y for next move in {}:".format(next_color))
                x = int(input("x = "))
                y = int(input("y = "))
                while self.move(x, y) == False:
                    print("invalid position!!! please re-enter.")
                    print("re-enter x and y for next move in {}:".format(next_color))
                    x = int(input("x = "))
                    y = int(input("y = "))
            else:
                pass_count += 1
                self.print("{} can only pass...".format(next_color))

            self.board.unset_ko(self.next_move)

        # calculate score

        input("Press Enter to continue...")


if __name__ == "__main__":
    go_game = Game(4, 4)
    go_game.start(True)
