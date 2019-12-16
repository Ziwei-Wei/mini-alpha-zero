import math
import numpy as np


class MCTS():
    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args

        # stores initial policy (returned by neural net)
        self.policy = {}

        # average of v value in given state weighted by visit count
        self.Q_for_s_a = {}
        # stores #times edge s,a was visited
        self.N_for_s_a = {}

        # stores #times board s was visited
        self.N_for_s = {}
        # stores game.getGameEnded ended for board s
        self.ends = {}

        # to avoid kos
        self.latest_two_s_a = []
        self.pass_count = 0

        # step count how many times the calculate_p_v is called
        self.count = 0

    def calculate_performance(self):
        total = 0
        for _, num in self.N_for_s.items():
            total += num
        return total/self.count

    def calculate_p_v(self, board, temp=1, exhaust=False, withoutNN=False):
        """
        Returns:
            current true P for nnet to learn
        """
        game_status = self.game.check_is_end(board, 1)

        # game already ended
        if game_status != 0:
            return [1/self.game.get_action_size() for a in range(self.game.get_action_size())], game_status

        self.count += 1
        for _ in range(self.args.tree_search_count):
            self.latest_two_s_a = []
            self.pass_count = 0
            self.search(board)

        s = self.game.to_string(board)

        p_counts = [self.N_for_s_a[(s, a)] if (
            s, a) in self.N_for_s_a else 0 for a in range(self.game.get_action_size())]
        p_counts = [x**(1./temp) for x in p_counts]
        p_sum = float(sum(p_counts))

        if withoutNN == True:
            # current player skipped play need to count from next player! could be ko
            if p_sum == 0:
                next_board = self.game.get_standard_board(board, -1)
                s = self.game.to_string(next_board)
                v_counts = [self.Q_for_s_a[(s, a)]*self.N_for_s_a[(s, a)] if (
                    s, a) in self.Q_for_s_a else 0 for a in range(self.game.get_action_size())]
                v = -float(sum(v_counts))/self.N_for_s[s]
                return [1/self.game.get_action_size() for a in range(self.game.get_action_size())], v
            else:
                v_counts = [self.Q_for_s_a[(s, a)]*self.N_for_s_a[(s, a)] if (
                    s, a) in self.Q_for_s_a else 0 for a in range(self.game.get_action_size())]
                v = float(sum(v_counts))/self.N_for_s[s]

                p_counts = [self.Q_for_s_a[(s, a)] + 1 + 1e-12 if (
                    s, a) in self.Q_for_s_a else 0 for a in range(self.game.get_action_size())]

                p_sum = float(sum(p_counts))
                p = [x/p_sum for x in p_counts]
                return p, v

        # current player skipped play need to count from next player! could be ko
        if p_sum == 0:
            next_board = self.game.get_standard_board(board, -1)
            s = self.game.to_string(next_board)
            v_counts = [self.Q_for_s_a[(s, a)]*self.N_for_s_a[(s, a)] if (
                s, a) in self.Q_for_s_a else 0 for a in range(self.game.get_action_size())]
            v = -float(sum(v_counts))/self.N_for_s[s]
            return [1/self.game.get_action_size() for a in range(self.game.get_action_size())], v
        else:
            p = [x/p_sum for x in p_counts]
            v_counts = [self.Q_for_s_a[(s, a)]*self.N_for_s_a[(s, a)] if (
                s, a) in self.Q_for_s_a else 0 for a in range(self.game.get_action_size())]
            v = float(sum(v_counts))/self.N_for_s[s]
            return p, v

    def search(self, board, depth=0, exhaust=False):
        """
        Run dfs to leaf node. Use U = maximum upper confidence bound.
        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propagated
        up the search path.
        Returns:
            v: the negative of the value of the current board
        """

        s = self.game.to_string(board)

        if s not in self.N_for_s:
            self.N_for_s[s] = 0

        if s not in self.ends:
            self.ends[s] = self.game.check_is_end(board, 1)

        if self.ends[s] != 0 or depth > self.game.get_action_size() or self.pass_count >= 2:
            return -self.game.get_current_win_lose(board, 1)

        valid_vector = self.game.get_valid_moves(board, 1)
        for a_position, _ in np.ndenumerate(valid_vector):
            if (s, a_position[0]) in self.latest_two_s_a:
                valid_vector[a_position] = 0

        if s not in self.policy:
            self.policy[s], v = self.nnet.predict(board)
            if exhaust == False:
                return -v[0]

        curr_policy = self.policy[s]*valid_vector
        p_sum = np.sum(curr_policy)
        if p_sum > 0:
            curr_policy /= p_sum

        best_UCB = -float('inf')
        best_action = -1

        # pick the action with the highest upper confidence bound
        for a in range(self.game.get_action_size()):
            if valid_vector[a]:
                if (s, a) in self.Q_for_s_a:
                    ucb = self.Q_for_s_a[(s, a)] + self.args.cpuct * \
                        (curr_policy[a]*math.sqrt(self.N_for_s[s]) /
                         (1 + self.N_for_s_a[(s, a)]))
                else:
                    ucb = self.args.cpuct * \
                        curr_policy[a]*math.sqrt(self.N_for_s[s] + 1)

                if ucb > best_UCB:
                    best_UCB = ucb
                    best_action = a

        a = best_action

        if a != -1:
            self.latest_two_s_a.append((s, a))
            if len(self.latest_two_s_a) > 2:
                self.latest_two_s_a.pop(0)
            self.pass_count = 0
        else:
            self.pass_count += 1

        next_board, _ = self.game.get_next_state(
            board, 1, best_action)
        next_board = self.game.get_standard_board(
            next_board, -1)

        v = self.search(next_board, depth + 1)

        if (s, a) in self.Q_for_s_a:
            self.Q_for_s_a[(s, a)] = (self.N_for_s_a[(s, a)] *
                                      self.Q_for_s_a[(s, a)] + v)/(self.N_for_s_a[(s, a)] + 1)

            self.N_for_s_a[(s, a)] += 1
        else:
            self.Q_for_s_a[(s, a)] = v
            self.N_for_s_a[(s, a)] = 1

        self.N_for_s[s] += 1
        return -v
