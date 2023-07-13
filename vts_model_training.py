import torch
import torch.nn as nn
import torch.optim as optim
from scipy import signal
import scipy.io.wavfile as wav
import numpy as np
from vtubernet import VtuberNet

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = VtuberNet().to(device)

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

sample_rate, audio_data = wav.read("training_data.wav")
resampled_audio = np.float32(signal.resample(audio_data, int(len(audio_data) * model.segment / sample_rate)))
num_segments = len(resampled_audio) // model.segment
total_length = num_segments * model.segment
adjusted_audio = np.resize(resampled_audio, total_length)
segments = np.split(adjusted_audio, num_segments)

train_data = torch.tensor(segments).unsqueeze(1).to(device)

with open("training_data.txt", "r") as file:
    lines = file.readlines()

labels = []
for line in lines:
    values = line.strip().split(",")
    values = [float(value) for value in values]
    values = [max(value, 0) for value in values] #bug where values are below 0, probably an issue with the logic in vts.py
    labels.append(values)

train_labels = torch.tensor(labels, dtype=torch.float32).to(device)

num_epochs = 10000

#main training loop
for epoch in range(num_epochs):
    model.train()
    optimizer.zero_grad()

    outputs = model(train_data)
    loss = criterion(outputs, train_labels)

    loss.backward()
    optimizer.step()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item()}")

torch.save(model.state_dict(), "vtuber_model.pth")