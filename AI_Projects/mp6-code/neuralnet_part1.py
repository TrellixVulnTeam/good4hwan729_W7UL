import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class NeuralNet(torch.nn.Module):
    def __init__(self, lrate,loss_fn,in_size,out_size):
        super(NeuralNet, self).__init__()
        self.loss_fn = loss_fn
        self.lrate = lrate
        self.in_size = in_size
        self.out_size = out_size
        self.fc1 = nn.Linear(self.in_size, 64)
        self.fc2 = nn.Linear(64, self.out_size)
        self.optimizer = optim.SGD(self.parameters(), lr=self.lrate)


    def forward(self, x):
        x = x.view(-1, self.in_size)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

    def step(self, x,y):
        self.optimizer.zero_grad()
        loss = self.loss_fn(self.forward(x), y)
        loss.backward()
        self.optimizer.step()
        return loss.item()


def fit(train_set,train_labels,dev_set,n_iter,batch_size=100):
    net = NeuralNet(0.015, nn.CrossEntropyLoss(), 3072, 2)
    losses = []
    yhats = []
    totloss = 0
    print(train_set.size())
    means = train_set.mean(dim=1, keepdim=True)         #Standardization on training set
    stds = train_set.std(dim=1, keepdim=True)
    normalized_data = (train_set - means) / stds

    means = dev_set.mean(dim=1, keepdim=True)           #Stabdardization on dev set
    stds = dev_set.std(dim=1, keepdim=True)
    normalized_data2 = (dev_set - means) / stds

    for i in range(n_iter):
        if n_iter*batch_size > len(train_set):
            start = np.mod(i*batch_size, len(train_set))
            output = net.step(normalized_data[start: start + batch_size], train_labels[start: start + batch_size])
        else:
            output = net.step(normalized_data[i*batch_size:i*(batch_size+1)], train_labels[i*batch_size:i*(batch_size+1)])
        totloss += output
        losses.append(totloss)

    net(dev_set)

    for data in normalized_data2:
        output = net.forward(data)
        output = output.detach().numpy()
        yhats.append(np.argmax(output))

    return losses, yhats, net
