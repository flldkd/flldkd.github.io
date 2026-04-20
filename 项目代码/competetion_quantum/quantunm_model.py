from pyvqnet.dtype import *
from pyvqnet.tensor.tensor import QTensor
from pyvqnet.tensor import tensor
import numpy as np
import pandas as pd
from pyvqnet.data.data import data_generator
from pyvqnet.nn.module import Module
from pyvqnet.nn import Linear, ReLu
from pyvqnet.optim.adam import Adam
from pyvqnet.nn.loss import CrossEntropyLoss
#help(Linear)

def data_process():
    """
    1. 读取数据并完成数据处理
    """
    """
    读取数据并完成数据处理
    返回处理后的特征和标签
    """
    # 1. 读取数据
    train_data = pd.read_csv('train.csv')
    test_data = pd.read_csv('test.csv')

    # 2. 数据预览
    print("训练集基本信息:")
    print(train_data.info())
    print("测试集基本信息:")
    print(test_data.info())
    
    # 3. 检查缺失值
    print("训练集缺失值情况:")
    print(train_data.isnull().sum())
    print("测试集缺失值情况:")
    print(test_data.isnull().sum())

    # 4. 特征与标签分离
    X_train = train_data[['age', 'sex', 'bmi', 'children', 'smoker', 'region']]
    y_train = train_data['charges'].to_numpy()  # 转为numpy数组
    X_test = test_data[['age', 'sex', 'bmi', 'children', 'smoker', 'region']]
    y_test = test_data['charges'].to_numpy()

    # 5. 类别型特征的独热编码
    X_train = pd.get_dummies(X_train, columns=['sex', 'smoker', 'region'], drop_first=True)
    X_test = pd.get_dummies(X_test, columns=['sex', 'smoker', 'region'], drop_first=True)

    # 6. 将数据转换为pyvqnet的tensor格式
    X_train_tensor = QTensor(X_train.values.astype(np.float64))  # 特征张量, 使用 QTensor
    y_train_tensor = QTensor(y_train.astype(np.float64))          # 标签张量, 使用 QTensor
    X_test_tensor = QTensor(X_test.values.astype(np.float64))     # 测试特征张量
    y_test_tensor = QTensor(y_test.astype(np.float64))
    return X_train_tensor, y_train_tensor, X_test_tensor, y_test_tensor

class VariationQuantumCircuit():
    """
    2. 在这里完成量子线路的设计
    """
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.qubits = None  # 这里可以存储量子比特的状态（例如，可用 numpy 数组或其他结构）

    def construct_circuit(self, input_data):
        """
        构建量子电路
        这个方法可以根据输入数据设置量子门和量子态。
        :param input_data: 输入数据，用于量子电路的构建
        """
        # TODO: 添加量子门的逻辑
        # 例如，设置量子比特状态，应用量子门
        pass
    
    def get_output(self):
        """
        获取量子电路的输出
        :return: 量子比特的状态
        """
        if self.qubits is not None:
            return self.qubits  # 返回量子比特的当前状态
        else:
            raise ValueError("量子电路尚未计算输出，请先调用 construct_circuit。")

class QuantumNN(Module):
    """
    3. 在这里完成初始化量子神经网络模型的代码
    """
    def __init__(self, n_qubits):
        super(QuantumNN, self).__init__()  # 初始化父类
        self.circuit = VariationQuantumCircuit(n_qubits)  # 初始化量子电路
        self.fc = Linear(
            input_channels=n_qubits,        # 输入特征数
            output_channels=1,              # 输出特征数
            weight_initializer=None,         # 权重初始化器，使用默认
            bias_initializer=None,           # 偏置初始化器，使用默认
            use_bias=True                    # 使用偏置
        )
    
    def forward(self, x):
        """
        前向传播方法
        :param x: 输入数据
        :return: 模型输出
        """
        self.circuit.construct_circuit(x)  # 构建量子电路
        quantum_output = self.circuit.get_output()  # 获取量子电路的输出
        output = self.fc(quantum_output)  # 全连接层的输出
        return output

def quantum_model_train():
    """
    4. 在这里完成训练量子模型的代码
    """
   # 数据准备 - 获取训练数据集
    X_train, y_train, _, _ = data_process()  # data_process() 函数返回训练特征和标签

    # 模型初始化
    model = QuantumNN(n_qubits=X_train.shape[1])  # 根据输入特征数目设置量子位数
    optimizer = Adam(model.parameters(), lr=0.01)  # 使用 Adam 优化器
    loss_fn = CrossEntropyLoss()  # 使用交叉熵损失函数

    # 训练过程
    num_epochs = 100  # 设置训练轮数
    for epoch in range(num_epochs):
        model.train()  # 切换到训练模式
        optimizer.zero_grad()  # 梯度清零
        
        # 前向传播
        output = model(X_train)  # 模型前向传播
        
        # 计算损失
        loss = loss_fn(output, y_train)  # 计算损失
        loss.backward()  # 反向传播
        optimizer.step()  # 更新参数
        
        # 打印损失信息
        if (epoch + 1) % 10 == 0:  # 每10轮打印一次
            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {loss.item()}")  # 输出当前轮次和损失值

    return model  # 返回训练好的模型

def quantum_model_test(model):
    """
    5. 使用测试数据集验证模型
    """
   # 数据准备 - 获取测试数据集
    _, _, X_test, y_test = data_process()  # 获取处理后的测试集特征和标签

    model.eval()  # 切换到评估模式
    with QTensor.no_grad():  # 禁用梯度计算以节省内存
        predictions = model(X_test)  # 使用模型进行预测

    # 计算 RMSE
    rmse = np.sqrt(np.mean((predictions.numpy() - y_test.numpy()) ** 2))
    print("Test RMSE:", rmse)

    # 保存 RMSE 结果到文件
    with open("results.txt", "w") as f:
        f.write(f"RMSE: {rmse}\n")

if __name__ == "__main__":
    model=quantum_model_train()

    quantum_model_test(model)
