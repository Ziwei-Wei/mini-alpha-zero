from battle import BattleGround
from game import Game
from model import Model
from mcts import MCTS
import numpy as np
import os
import sys
from pickle import Pickler, Unpickler
from random import shuffle
from utils import *
import pandas as pd
import datetime


class Trainer():
    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.pnet = self.nnet.__class__(self.game)  # the competitor network
        self.args = args
        self.mcts = MCTS(self.game, self.nnet, self.args)

        self.trainExamplesHistory = []
        self.loss_list = []
        self.win_rate_list = []
        self.self_play_count = 0

    def self_play(self, training=False):
        """
        go through one run of self play and return training examples for nnet
        Returns: training examples of (standard_board, policy, win rate) 
        """
        # to avoid kos
        latest_two_s_a = []
        pass_count = 0

        training_examples = []
        episodeStep = 0
        board = self.game.get_init_board()

        while True:
            # check if game end
            r = self.game.check_is_end(board, 1)
            if r != 0 or pass_count >= 2 or episodeStep > self.game.get_action_size()*2:
                return training_examples

            episodeStep += 1

            # run mcts to get the training example from this root node
            policy, v = self.mcts.calculate_p_v(board, temp=1)

            # get all symmetry board for robustness
            symmetrics = self.game.get_all_perspectives(board, policy)
            for b, p in symmetrics:
                training_examples.append([b, p, v])

            # stop if exceed max step
            if episodeStep > self.game.get_action_size()*2:
                return training_examples

            # filter out ko actions
            s = self.game.to_string(board)
            valid_vector = self.game.get_valid_moves(board, 1)
            for a_position, _ in np.ndenumerate(valid_vector):
                if (s, a_position[0]) in latest_two_s_a:
                    valid_vector[a_position] = 0

            # re_normalize
            policy *= valid_vector
            p_sum = np.sum(policy)
            if p_sum > 0:
                policy /= p_sum

            # must be movable
            if np.array(policy).sum() == 0:
                pass_count += 1
                board, curr_player = self.game.get_next_state(
                    board, 1, -1)
                continue
            else:
                # to encourage the model to explore
                if training == True:
                    policy = np.array(policy) + 0.5/self.game.get_action_size()
                    p_sum = np.sum(policy)
                    policy /= p_sum
                action = np.random.choice(len(policy), p=policy)

            # record recent s to a
            latest_two_s_a.append((s, action))
            if len(latest_two_s_a) > 2:
                latest_two_s_a.pop(0)

            board, curr_player = self.game.get_next_state(
                board, 1, action)
            board = self.game.get_standard_board(
                board, curr_player)

            pass_count = 0

    def learn(self):
        self.loss_list = []
        self.win_rate_list = []
        for i in range(1, self.args.iter_num+1):
            print(str(i) + 'th iteration at {} ->'.format(datetime.datetime.now().time()))
            iterationTrainExamples = []
            self.self_play_count = 0
            for j in range(self.args.self_play_num):
                print("self-play: {}".format(j))
                self.self_play_count += 1
                self.mcts = MCTS(self.game, self.nnet, self.args)
                if self.self_play_count > 7:
                    iterationTrainExamples += self.self_play()
                else:
                    self.self_play()

            # save the iteration examples to the history
            self.trainExamplesHistory.append(iterationTrainExamples)

            # shuffle examples before training
            trainExamples = []
            for e in self.trainExamplesHistory:
                trainExamples.extend(e)
            shuffle(trainExamples)

            loss = self.nnet.train(trainExamples)
            self.loss_list.append(loss)

            result = test_MCTS_with_NNet(self.game, self.nnet,
                                         self.game.get_board_size()[0])
            self.win_rate_list.append(result)

            self.trainExamplesHistory = []
            print("current loss = {}".format(loss))
            self.nnet.save_checkpoint(
                folder=self.args.checkpoint, filename='model_{}x{}.pth.tar'.format(*self.game.get_board_size()))

        df_loss = pd.DataFrame({'loss': self.loss_list})
        df_loss.to_csv('./plots/loss_{}x{}.csv'.format(
            *self.game.get_board_size()), sep=',')
        df_win_rate = pd.DataFrame({'win_rate': self.win_rate_list})
        df_win_rate.to_csv('./plots/win_rate_{}x{}.csv'.format(
            *self.game.get_board_size()), sep=',')


def test_MCTS_with_NNet(game, nnet, n):
    '''
    Returns:
        win rate for ai
    '''
    print("Test MCTS with CNN on {}X{} with {} search on each step:".format(n, n, n*n))
    random_player = RandomPlayer(game)
    model = nnet
    local_args = dotdict({'tree_search_count': n*n, 'cpuct': 1.0})
    mcts = MCTS(game, model, local_args)
    def nnet_player(board): return mcts.calculate_p_v(board)
    bg = BattleGround(nnet_player, random_player.play, game)
    ai_win, random_win, draw = bg.playGames(5)
    return ai_win/(ai_win + random_win + draw)


class RandomPlayer():
    def __init__(self, game: "Game"):
        self.game = game

    def play(self, board):
        p = np.random.random_sample(self.game.get_action_size())
        valids = self.game.get_valid_moves(board, 1)
        p *= valids
        return p, 0.5


# adjust params here
args = dotdict({
    'iter_num': 100,
    'self_play_num': 32,
    'tree_search_count': 32,
    'cpuct': 1,
    'checkpoint': './train'
})


if __name__ == "__main__":
    print("-- Going to retrain all models")
    print("-- Adjust params of trainer in train.py")
    print("-- Default: will go through 100 iteration for each model")
    print("-- Note: trained model will be saved to ./train")
    print("-- Warning: it will be very slow to train to accelerate decrease self_play_num, tree_search_count, or iter_num")

    print("-- train 4X4")
    game = Game(4)
    model = Model(game)
    T = Trainer(game, model, args)
    T.learn()

    print("-- train 5X5")
    game = Game(5)
    model = Model(game)
    T = Trainer(game, model, args)
    T.learn()

    print("-- train 6X6")
    game = Game(6)
    model = Model(game)
    T = Trainer(game, model, args)
    T.learn()

    print("-- train 7X7")
    game = Game(7)
    model = Model(game)
    T = Trainer(game, model, args)
    T.learn()

    print("-- train 8X8")
    game = Game(8)
    model = Model(game)
    T = Trainer(game, model, args)
    T.learn()
