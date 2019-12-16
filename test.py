from battle import BattleGround
from game import Game
from model import Model
from mcts import MCTS

import pandas as pd
import numpy as np
from utils import *


class RandomPlayer():
    def __init__(self, game: "Game"):
        self.game = game

    def play(self, board):
        p = np.random.random_sample(self.game.get_action_size())
        valids = self.game.get_valid_moves(board, 1)
        p *= valids
        return p, 0.5


def test_MCTS(n, num_iter=100):
    print("Test MCTS on {}X{} with {} search on each step:".format(n, n, 2*n**2))
    print("player1 = {}, player2 = {}".format("MCTS", "Baseline"))
    game = Game(n)
    random_player = RandomPlayer(game)
    model = Model(game)
    args = dotdict({'tree_search_count': 2*n**2, 'cpuct': 1.0})
    mcts = MCTS(game, model, args)
    def nnet_player(board): return mcts.calculate_p_v(
        board, exhaust=True, withoutNN=True)

    bg = BattleGround(nnet_player, random_player.play, game)

    ai, baseline, draw = bg.playGames(int(num_iter/2))
    perf = mcts.calculate_performance()
    print("--> Performance: {} node/step".format(perf))
    print("--> Result: MCTS/Baseline wins = {}/{}, MCTS win rate = {}\n".format(ai,
                                                                                baseline, ai/(ai + baseline + draw)))
    return (perf, ai/(ai + baseline + draw))


def test_MCTS_with_NNet(n, num_iter=100):
    print("Test AI with CNN on {}X{} with {} search on each step:".format(n, n, 2*n**2))
    print("player1 = {}, player2 = {}".format("AI", "Baseline"))
    game = Game(n)
    random_player = RandomPlayer(game)
    model = Model(game)
    model.load_checkpoint('models', 'model_{}x{}.pth.tar'.format(n, n))
    args = dotdict({'tree_search_count': 2*n**2, 'cpuct': 1.0})
    mcts = MCTS(game, model, args)
    def nnet_player(board): return mcts.calculate_p_v(board)

    bg = BattleGround(nnet_player, random_player.play, game)

    ai, baseline, draw = bg.playGames(int(num_iter/2))
    perf = mcts.calculate_performance()
    print("--> Performance: {} node/step".format(perf))
    print("--> Result: AI/Baseline wins = {}/{}, AI win rate = {}\n".format(ai,
                                                                            baseline, ai/(ai + baseline + draw)))
    return (perf, ai/(ai + baseline + draw))


if __name__ == "__main__":
    print("-- Going to test all models against baseline")
    print("-- Adjust search amount of MCST in test.py")
    print("-- Default: will play 100 games for each case")
    print("-- Note: recorded data will be saved to ./plots")
    print("--       MCST with low tree_search count might not be consistant for every run even for default 2*n**2")
    print("-- Warning: go rules are complicated in order to beat random MCST need to have enough search amount")
    print("--          and it will be slow to play so many games...\n")

    perf_and_win_rate = {}

    perf_and_win_rate["4x4 mcts"] = test_MCTS(4)
    perf_and_win_rate["4x4 nnet"] = test_MCTS_with_NNet(4)

    perf_and_win_rate["5x5 mcts"] = test_MCTS(5)
    perf_and_win_rate["5x5 nnet"] = test_MCTS_with_NNet(5)

    perf_and_win_rate["6x6 mcts"] = test_MCTS(6)
    perf_and_win_rate["6x6 nnet"] = test_MCTS_with_NNet(6)

    perf_and_win_rate["7x7 mcts"] = test_MCTS(7)
    perf_and_win_rate["7x7 nnet"] = test_MCTS_with_NNet(7)

    perf_and_win_rate["8x8 mcts"] = test_MCTS(8)
    perf_and_win_rate["8x8 nnet"] = test_MCTS_with_NNet(8)

    df = pd.DataFrame.from_dict(
        perf_and_win_rate, orient='index').reset_index()
    df.columns = ['type', 'performance', 'win rate']
    df.to_csv('./plots/test_data.csv', sep=',')
