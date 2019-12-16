
import numpy as np
import time


class BattleGround():
    def __init__(self, player1, player2, game, display=None):

        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.display = display

    def playGame(self, verbose=False):
        """
        Returns: (1,or -1, or 0) for player1 win, lose, draw
        """
        # to avoid kos
        latest_two_s_a = []
        pass_count = 0

        players = [None, self.player1, self.player2]
        curr_player = 1
        board = self.game.get_init_board()
        it = 0
        while self.game.check_is_end(board, curr_player) == 0:
            it += 1
            if it > self.game.get_action_size()*2 or pass_count >= 2:
                return self.game.get_current_win_lose(board, 1)
            if verbose:
                assert(self.display)
                print("Turn ", str(it), "Player ", str(curr_player))
                self.display(board)

            standard_b = self.game.get_standard_board(board, curr_player)
            s = self.game.to_string(standard_b)
            policy, _ = players[curr_player](standard_b)

            # filter out ko actions
            valid_vector = self.game.get_valid_moves(standard_b, 1)
            for a_position, _ in np.ndenumerate(valid_vector):
                if (s, a_position[0]) in latest_two_s_a:
                    valid_vector[a_position] = 0
            policy *= valid_vector

            # must be movable
            if policy.sum() == 0:
                pass_count += 1
                board, curr_player = self.game.get_next_state(
                    board, curr_player, -1)
                continue
            else:
                action = np.argmax(policy)

            # record recent s to a
            latest_two_s_a.append((s, action))
            if len(latest_two_s_a) > 2:
                latest_two_s_a.pop(0)

            board, curr_player = self.game.get_next_state(
                board, curr_player, action)

        if verbose:
            assert(self.display)
            print("Game over: Turn ", str(it), "Result ",
                  str(self.game.check_is_end(board, 1)))
            self.display(board)
        return self.game.check_is_end(board, 1)

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.
        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """
        oneWon = 0
        twoWon = 0
        draws = 0
        print("Player1 as First, Player2 as Second")
        for _ in range(num):
            print((oneWon, twoWon, draws))
            gameResult = self.playGame(verbose=verbose)
            if gameResult == 1:
                oneWon += 1
            elif gameResult == -1:
                twoWon += 1
            else:
                draws += 1

        self.player1, self.player2 = self.player2, self.player1
        print("Player1 as Second, Player2 as First")
        for i in range(num):
            print((oneWon, twoWon, draws))
            gameResult = self.playGame(verbose=verbose)
            if gameResult == -1:
                oneWon += 1
            elif gameResult == 1:
                twoWon += 1
            else:
                draws += 1

        print((oneWon, twoWon, draws))
        return oneWon, twoWon, draws
