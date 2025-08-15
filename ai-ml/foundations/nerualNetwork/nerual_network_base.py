import numpy as np


# sigmoid激活函数及其导数
def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)


# 神经网络类定义
class NeuralNetwork:
    def __init__(self, x, y):
        self.input = x
        self.weights1 = np.random.rand(self.input.shape[1], 4)  # 输入层到隐藏层的权重
        self.weights2 = np.random.rand(4, 1)  # 隐藏层到输出层的权重
        self.y = y
        self.output = np.zeros(y.shape)

    def feedforward(self):
        self.layer1 = sigmoid(np.dot(self.input, self.weights1))
        self.output = sigmoid(np.dot(self.layer1, self.weights2))

    def backprop(self):
        # 使用链式法则计算梯度
        d_weights2 = np.dot(
            self.layer1.T,
            (2 * (self.y - self.output) * sigmoid_derivative(self.output)),
        )
        d_weights1 = np.dot(
            self.input.T,
            (
                np.dot(
                    2 * (self.y - self.output) * sigmoid_derivative(self.output),
                    self.weights2.T,
                )
                * sigmoid_derivative(self.layer1)
            ),
        )

        # 更新权重
        self.weights1 += d_weights1
        self.weights2 += d_weights2

    def train(self, iterations):
        for i in range(iterations):
            self.feedforward()
            self.backprop()


# 输入数据和输出数据
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])  # XOR问题

# 创建神经网络对象
nn = NeuralNetwork(X, y)

# 训练网络
nn.train(1500)

# 输出结果
print(nn.output)
