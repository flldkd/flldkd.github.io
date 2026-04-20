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
from pyqpanda3.core import *  
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
    def __init__(self, n_qubits, depth, encoding, vqc_config):
        self.n_qubits = n_qubits  # 量子位数量
        self.depth = depth  # 电路深度
        self.encoding = encoding  # 输入编码方式
        self.vqc_config = vqc_config  # vqc配置，定义使用的量子电路特性

        self.setup()  # 初始化电路

    def setup(self):
        # 定义量子比特（wires）
        self.wires_list = [
            [f"vqc_{j}_{i}" for i in range(self.n_qubits)] for j in range(6)
        ]
        
        # 这里不再使用量子设备，因为 pyvqnet 自带实现
        # self.devs = [qml.device(self.backend, wires=wires) for wires in self.wires_list]
        
        # 定义测量线
        self.measure_wires_inside = slice(0, self.n_qubits)  # 修改为 n_qubits 以处理内部状态
        self.measure_wires_output = 0  # 输出测量的线（通常是第 0 个量子比特）

        # 初始化量子电路的各个部分
        self.vqc1 = self.vqc_setup(self.wires_list[0], self.measure_wires_inside)
        self.vqc2 = self.vqc_setup(self.wires_list[1], self.measure_wires_inside)
        self.vqc3 = self.vqc_setup(self.wires_list[2], self.measure_wires_inside)
        self.vqc4 = self.vqc_setup(self.wires_list[3], self.measure_wires_inside)
        self.vqc5 = self.vqc_setup(self.wires_list[4], self.measure_wires_inside)
        self.vqc6 = self.vqc_setup(self.wires_list[5], self.measure_wires_output)


    def vqc_setup(self, wires, measure_wire_indices):
        measure_wires = wires[measure_wire_indices]
        if not isinstance(measure_wires, list):
            measure_wires = [measure_wires]

        # 创建量子电路
        def circuit(inputs, weights):
            for i, feat in enumerate(inputs):
                # 编码逻辑
                if self.encoding == "original":
                    # Hadamard 编码
                    self.apply_hadamard(wires[i])
                    self.apply_ry(math.atan(feat), wires[i])
                    self.apply_rz(math.atan(feat**2), wires[i])
                elif self.encoding == "No-H":
                    self.apply_ry(math.atan(feat), wires[i])
                    self.apply_rz(math.atan(feat**2), wires[i])
                elif self.encoding == "No-Square":
                    self.apply_hadamard(wires[i])
                    self.apply_rx(math.atan(feat), wires[i])
                elif self.encoding == "arcsin-arccos":
                    self.apply_ry(math.asin(feat), wires[i])
                    self.apply_rz(math.acos(feat), wires[i])

            n_qlayer = weights.shape[0]  # 深度
            n_wire = weights.shape[1]  # 量子比特数量

            # 基于配置应用量子门
            if self.vqc_config == "original":
                for j in range(n_wire):
                    self.apply_cnot(wires[j], wires[(j + 1) % n_wire])
                    self.apply_cnot(wires[j], wires[(j + 2) % n_wire])
                for i in range(n_qlayer):
                    for j in range(n_wire):
                        self.apply_rot(weights[i][j], wires[j])  # Rot 门应用

            elif self.vqc_config == "5":
                remaining = [n_wire - 1] * n_wire
                for i in range(n_qlayer):
                    for j in reversed(range(n_wire)):
                        for k in reversed(range(n_wire)):
                            if k != j:
                                self.apply_crz(weights[i][k][remaining[k]], wires[j], wires[k])
                                remaining[k] -= 1
                    for j in range(n_wire):
                        self.apply_rx(weights[i][j][-2], wires[j])
                        self.apply_rz(weights[i][j][-1], wires[j])

            elif self.vqc_config == "10":
                for i in range(n_qlayer):
                    for j in range(n_wire):
                        self.apply_cnot(wires[j], wires[(j + 1) % n_wire])
                        self.apply_ry(weights[i][j][0], wires[j])

            elif self.vqc_config == "18":
                for i in range(n_qlayer):
                    for j in range(n_wire):
                        self.apply_crz(weights[i][j][0], wires[j], wires[(j + 1) % n_wire])

            return [self.measure(w) for w in measure_wires]  # 返回测量结果

        # 权重形状设置
        if self.vqc_config == "original":
            weight_shapes = {"weights": (self.depth, self.n_qubits, 3)}
        elif self.vqc_config == "5":
            weight_shapes = {"weights": (self.depth, self.n_qubits, self.n_qubits - 1 + 2)}
        elif self.vqc_config == "10":
            weight_shapes = {"weights": (self.depth, self.n_qubits, 1)}
        elif self.vqc_config == "18":
            weight_shapes = {"weights": (self.depth, self.n_qubits, 1)}

        print(f"weight_shapes = (depth, n_qubits, x) = ({self.depth}, {self.n_qubits}, {weight_shapes})")
        return weight_shapes  # 这里可以返回权重形状或电路   
    def apply_hadamard(self, wire):
        # 实现 Hadamard 门
        pass

    def apply_ry(self, theta, wire):
        # 实现 RY 门
        pass

    def apply_rz(self, theta, wire):
        # 实现 RZ 门
        pass

    def apply_cnot(self, control_wire, target_wire):
        # 实现 CNOT 门
        pass

    def apply_crz(self, phi, control_wire, target_wire):
        # 实现 CRZ 门
        pass

    def apply_rot(self, weights, wire):
        # 实现 Rot 门
        pass

    def measure(self, wire):
        # 返回测量结果
        pass     
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
    def __init__(self, input_dim, hidden_dim, n_qubits, depth, batch_first=True, encoding="original", vqc_config="original"):
        super(QuantumNN, self).__init__()

        # 初始化参数
        self.input_dim = input_dim  # 输入特征维度
        self.hidden_dim = hidden_dim  # 隐藏层维度
        self.n_qubits = n_qubits  # 量子比特数量
        self.depth = depth  # 量子电路深度
        self.batch_first = batch_first  # 数据格式的设置
        self.encoding = encoding  # 输入编码方式
        self.vqc_config = vqc_config  # VQC配置
        
        # 初始化量子电路
        self.circuit = VariationQuantumCircuit(
            n_qubits=self.n_qubits,
            depth=self.depth,
            encoding=self.encoding,
            vqc_config=self.vqc_config
        )

        # 全连接层
        self.fc = Linear(self.hidden_dim, 1)  # 输出最终的预测值
    
    def forward(self, x, init_states=None):
        if self.batch_first:
            batch_size, seq_length, features_size = x.size()
        else:
            seq_length, batch_size, features_size = x.size()

        hidden_seq = []

        # 初始化状态
        if init_states is None:
            h_t = QTensor.zeros(batch_size, self.hidden_dim, device=self.device)  # 隐藏状态
            c_t = QTensor.zeros(batch_size, self.hidden_dim, device=self.device)  # 细胞状态
        else:
            h_t, c_t = init_states
            h_t = h_t[0]  # 只取第一个元素
            c_t = c_t[0]  # 只取第一个元素

        # 进行循环以处理序列的每个时间步
        for t in range(seq_length):
            # 获取当前时间步的特征
            x_t = x[:, t, :] if self.batch_first else x[t]

            # 拼接输入和隐藏状态
            v_t = QTensor.concat((h_t, x_t), dim=1)

            # 使用量子电路进行计算
            f_t = QTensor.sigmoid(self.circuit.vqc1(v_t))  # 忘记门
            i_t = QTensor.sigmoid(self.circuit.vqc2(v_t))  # 输入门
            c_tile_t = QTensor.tanh(self.circuit.vqc3(v_t))  # 更新门
            c_t = (f_t * c_t) + (i_t * c_tile_t)  # 更新细胞状态
            o_t = QTensor.sigmoid(self.circuit.vqc4(v_t))  # 输出门
            h_t = self.circuit.vqc5(o_t * QTensor.tanh(c_t))  # 更新隐藏状态
            y_t = self.circuit.vqc6(o_t * QTensor.tanh(c_t))  # 输出结果

            hidden_seq.append(h_t)  # 将当前隐藏状态保存到序列中

        return y_t  # 返回最后的输出结果

def quantum_model_train():
    """
    4. 在这里完成训练量子模型的代码
    """
   # 数据准备 - 获取训练数据集
    X_train, y_train, _, _ = data_process()  # data_process() 函数返回训练特征和标签

    # 模型初始化
    model = QuantumNN(input_dim=10, hidden_dim=32, n_qubits=4, depth=3, batch_first=True, encoding="original", vqc_config="original")
    # 根据输入特征数目设置量子位数
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
