import torch.nn.functional as F
import torch.nn as nn
import torch


class NNet(nn.Module):
    def __init__(self, game, args):
        self.x, self.y = game.get_board_size()
        self.action_size = game.get_action_size()
        self.args = args

        super(NNet, self).__init__()

        self.conv1 = nn.Conv2d(1, args.hidden, 3,  padding=1)
        self.conv2 = nn.Conv2d(args.hidden, args.hidden, 3, padding=1)
        self.conv3 = nn.Conv2d(args.hidden, args.hidden, 3)
        self.conv4 = nn.Conv2d(args.hidden, args.hidden, 1)

        self.bn1 = nn.BatchNorm2d(args.hidden)
        self.bn2 = nn.BatchNorm2d(args.hidden)
        self.bn3 = nn.BatchNorm2d(args.hidden)
        self.bn4 = nn.BatchNorm2d(args.hidden)

        self.fc1 = nn.Linear(args.hidden*(self.x-2)*(self.y-2), 1024)
        self.fc_bn1 = nn.BatchNorm1d(1024)

        self.fc2 = nn.Linear(1024, 512)
        self.fc_bn2 = nn.BatchNorm1d(512)

        self.fc3 = nn.Linear(512, self.action_size)
        self.fc4 = nn.Linear(512, 1)

    def forward(self, s):
        s = s.view(-1, 1, self.x, self.y)
        s = F.relu(self.bn1(self.conv1(s)))
        s = F.relu(self.bn2(self.conv2(s)))
        s = F.relu(self.bn3(self.conv3(s)))
        s = F.relu(self.bn4(self.conv4(s)))
        s = s.view(-1, self.args.hidden * (self.x-2)*(self.y-2))

        s = F.dropout(F.relu(self.fc_bn1(self.fc1(s))), p=self.args.dropout,
                      training=self.training)
        s = F.dropout(F.relu(self.fc_bn2(self.fc2(s))), p=self.args.dropout,
                      training=self.training)

        p = self.fc3(s)
        v = self.fc4(s)

        return F.softmax(p, dim=1), torch.tanh(v)
