import numpy as np
import scipy.io
from nn import *
import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
from torch.autograd import Variable
import skimage.measure
import torch.optim as optim

max_iters = 5

batch_size = 64
learning_rate = 1e-2
hidden_size = 64
# batches = get_random_batches(train_x,train_y,batch_size)
# batch_num = len(batches)

#
# MNIST dataset
train_dataset = torchvision.datasets.MNIST(root='../../data',
                                            train=True,
                                           transform=transforms.ToTensor(),
                                           download=True)

test_dataset = torchvision.datasets.MNIST(root='../../data',
                                           train=False,
                                          transform=transforms.ToTensor())


train_examples = len(train_dataset)
test_examples = len(test_dataset)
# Data loader
train_loader = torch.utils.data.DataLoader(dataset=train_dataset,
                                           batch_size=batch_size,
                                           shuffle=True)

test_loader = torch.utils.data.DataLoader(dataset=test_dataset,
                                          batch_size=batch_size,
                                          shuffle=False)



# print(train_dataset.shape)

# model of nn
class Net(torch.nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = torch.nn.Conv2d(1, 20, 5, 1)
        self.conv2 = torch.nn.Conv2d(20, 50, 5, 1)
        self.fc1 = torch.nn.Linear(4 * 4 * 50, 500) # was 4*4*50, 500 for
        self.fc2 = torch.nn.Linear(500, 36) # was 500,10 for mnist

    def forward(self, x):
        x = torch.nn.functional.relu(self.conv1(x))
        # print(x.size())
        x = torch.nn.functional.max_pool2d(x, 2, 2)
        # print(x.size())

        x = torch.nn.functional.relu(self.conv2(x))
        # print(x.size())

        # print('conv2')
        x = torch.nn.functional.max_pool2d(x, 2, 2)
        x = x.view(-1, 4* 4 * 50)
        # print(x.size())
        x = torch.nn.functional.relu(self.fc1(x))
        x = self.fc2(x)
        return x





model = Net()
training_loss_data = []
valid_loss_data = []
training_acc_data = []
valid_acc_data = []
# torch.nn.init.xavier_uniform(model(Linear.weight))

criterion = torch.nn.CrossEntropyLoss()
# criterion = torch.nn.BCELoss()
# criterion = torch.nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.parameters(),lr = learning_rate)
optimizer = torch.optim.SGD(model.parameters(), lr = learning_rate, momentum=0.9)

for itr in range(max_iters):
    total_loss = 0
    total_acc = 0
    valid_total_loss = 0
    valid_total_acc = 0
    for batch_idx, (x, target) in enumerate(train_loader):
        # x = x.reshape(batch_size,1,32,32) # add if using nist36
        out =  model(x)
        # print(out.size())
        # print(target.size())
        loss = criterion(out,target)
        optimizer.zero_grad()
        loss.backward()

        optimizer.step()
        _, predicted = torch.max(out.data, 1)

        total_acc += ((target==predicted).sum().item())
        # print(total_acc)
        total_loss+=loss
    ave_acc = total_acc/train_examples
    for batch_idx, (valid_x, valid_target) in enumerate(test_loader):
        valid_out =  model(valid_x)
        valid_loss = criterion(valid_out,valid_target)
        _, valid_predicted = torch.max(valid_out.data, 1)
        valid_total_acc += ((valid_target==valid_predicted).sum().item())
        # print(total_acc)
        valid_total_loss+=valid_loss
    valid_acc = valid_total_acc/test_examples

    training_loss_data.append(total_loss/(train_examples/batch_size))
    valid_loss_data.append(valid_loss/(test_examples/batch_size))
    training_acc_data.append(ave_acc)
    valid_acc_data.append(valid_acc)
    print('Validation accuracy: ', valid_acc)
    if itr % 2 == 0:
        print("itr: {:02d} \t loss: {:.2f} \t acc : {:.2f}".format(itr,total_loss,ave_acc))

plt.figure(0)
plt.plot(np.arange(max_iters), training_acc_data, 'r')
plt.plot(np.arange(max_iters), valid_acc_data, 'b')
plt.legend(['training accuracy','valid accuracy'])

plt.show()
plt.figure(1)
plt.plot(np.arange(max_iters),training_loss_data,'r')
plt.plot(np.arange(max_iters),valid_loss_data,'b')
plt.legend(['training loss','valid loss'])

plt.show()