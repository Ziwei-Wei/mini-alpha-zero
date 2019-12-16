from nnet import NNet
import torch.optim as optim
import torch.nn.functional as F
import torch.nn as nn
import torch
import os
import shutil
import time
import random
import numpy as np
import math
import sys
from utils import *


args = dotdict({
    'dropout': 0.8,
    'batch_size': 32,
    'hidden': 512,
})


class Model():
    def __init__(self, game):
        self.epoch_num = 10
        self.nnet = NNet(game, args)
        self.x, self.y = game.get_board_size()
        self.action_size = game.get_action_size()
        self.nnet.cuda()

    def train(self, examples):
        """
        use (board, policy, win rate) to train the nnet
        """
        optimizer = optim.Adam(self.nnet.parameters(),
                               lr=1e-7,
                               weight_decay=1e-7
                               )
        average_loss = 0
        total_batch_num = 0
        for epoch in range(self.epoch_num):
            epoch_loss = 0
            batch_idx = 0
            while batch_idx < int(len(examples)/args.batch_size):
                ids = np.random.randint(len(examples), size=args.batch_size)
                state, policy, v = list(zip(*[examples[i] for i in ids]))

                state = torch.Tensor(np.array(state)).contiguous().cuda()
                target_policy = torch.Tensor(
                    np.array(policy)).contiguous().cuda()
                target_v = torch.Tensor(np.array(v)).contiguous().cuda()

                # predict
                self.nnet.eval()
                out_policy, out_v = self.nnet(state)
                self.nnet.train()

                total_loss = self.loss(
                    target_policy, out_policy, target_v, out_v)
                '''
                print("state:\n {}".format(state[3]))
                print("policy:\n {}".format(target_policy[3]))
                print("nn_policy:\n {}".format(out_policy[3]))
                '''

                average_loss += abs(np.sum(total_loss.cpu().data.numpy()))
                epoch_loss += abs(np.sum(total_loss.cpu().data.numpy()))
                # print("loss in batch {} is {}".format(batch_idx, total_loss.cpu().data.numpy()))

                # compute gradient and do SGD step
                optimizer.zero_grad()
                total_loss.sum().backward()
                optimizer.step()

                batch_idx += 1
                total_batch_num += 1
            print('epoch: {}, loss: {}'.format(epoch, epoch_loss/batch_idx))
        self.nnet.eval()
        return average_loss / total_batch_num

    def predict(self, board):
        """
        board: np array with board
        """
        # preparing input
        board = torch.Tensor(board.astype(np.float64))
        board = board.contiguous().cuda()
        board = board.view(1, self.x, self.y)
        self.nnet.eval()
        with torch.no_grad():
            policy, v = self.nnet(board)
        return policy.data.cpu().numpy()[0], v.data.cpu().numpy()[0]

    def save_checkpoint(self, folder='train', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.mkdir(folder)
        torch.save({
            'state_dict': self.nnet.state_dict(),
        }, filepath)

    def load_checkpoint(self, folder='train', filename='checkpoint.pth.tar'):
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            raise("no model in {}".format(filepath))
        checkpoint = torch.load(filepath)
        self.nnet.load_state_dict(checkpoint['state_dict'])

    def loss(self, targets_p, outputs_p, target_v, outputs_v):
        '''
        print("loss:")
        print(-torch.sum(targets_p*outputs_p, dim=1))
        print((target_v-outputs_v.view(-1))**2)
        print(-torch.sum(targets_p*outputs_p, dim=1) +
              (target_v-outputs_v.view(-1))**2)
        '''
        return -torch.sum(targets_p*torch.log(outputs_p), dim=1) / self.action_size + (target_v-outputs_v.view(-1))**2
