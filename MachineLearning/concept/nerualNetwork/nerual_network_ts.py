import tensorflow as ts
from tensorflow.keras import layers, models


model = models.Sequential(
    [
        # 添加第一个隐藏层（输入层），使用ReLU激活函数
        layers.Dense(64, activation="relu", input_shape=(10,)),
        # 添加第二个隐藏层
        layers.Dense(64, activation="relu"),
        # 添加输出层，使用sigmoid激活函数进行分类
        layers.Dense(1, activation="sigmoid"),
    ]
)
# 编译模型
# 使用adam优化器，二元交叉熵作为损失函数，同时跟踪准确率
model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

# 查看模型概况
model.summary()

# 制造一些假数据进行训练
import numpy as np

# 生成1000个样本，每个样本10个特征
x_train = np.random.random((1000, 10))
# 生成1000个随机标签（0或1）
y_train = np.random.randint(2, size=(1000, 1))

# 训练模型
model.fit(x_train, y_train, epochs=10, batch_size=32)

# 评估模型
loss, accuracy = model.evaluate(x_train, y_train)
print(f"Loss: {loss}, Accuracy: {accuracy}")
