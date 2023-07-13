import torch
import torch.nn as nn

DEFAULT_DURATION = .1
DEFAULT_SAMPLE_RATE = 48000

class VtuberNet(nn.Module):
    def __init__(self, duration=DEFAULT_DURATION, sample_rate=DEFAULT_SAMPLE_RATE):
        self.duration = duration
        self.sample_rate = sample_rate
        self.segment = int(self.sample_rate*self.duration)
        super(VtuberNet, self).__init__()
        self.fc1 = nn.Linear(self.segment, 2048)
        self.fc2 = nn.Linear(2048, 1024)
        self.fc3 = nn.Linear(1024, 512)
        self.fc4 = nn.Linear(512, 256)
        self.fc5 = nn.Linear(256, 128)
        self.fc6 = nn.Linear(128, 64)
        self.fc7 = nn.Linear(64, 17)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = torch.tensor(x, dtype=torch.float32)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        x = self.relu(x)
        x = self.fc4(x)
        x = self.relu(x)
        x = self.fc5(x)
        x = self.relu(x)
        x = self.fc6(x)
        x = self.relu(x)
        x = self.fc7(x)
        x = self.sigmoid(x)
        return x