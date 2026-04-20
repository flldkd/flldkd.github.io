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
from sklearn.preprocessing import OneHotEncoder, StandardScaler  
from pyvqnet.qnn.vqc import QMachine, RY, CNOT, MeasureAll, Probability
from pyvqnet.nn.loss import MeanSquaredError
from pyvqnet.device import DEV_CPU
from pyvqnet.nn import Parameter  
from pyvqnet.qnn.vqc import QModule, QMachine, rx, ry, rz, cnot, MeasureAll
from pyvqnet.nn import Parameter
from pyvqnet import tensor as vtensor  # 使用别名避免命名冲突
from pyvqnet import no_grad  
#help(Linear)
class QuantumFeatureMap:  
    @staticmethod  
    def encode(qm, x):  
        """  
        使用角度编码将经典数据编码到量子态  
        """  
        # 如果输入是 QTensor，先转换为 NumPy 数组  
        if isinstance(x, vtensor.QTensor):  
            x = x.numpy()  
        
        # 确保输入数据是2D NumPy数组  
        if not isinstance(x, np.ndarray):  
            x = np.array(x)  
        
        # 如果数据是高维的，展平或截取  
        if x.ndim > 2:  
            x = x.reshape(x.shape[0], -1)  
        
        # 转换为QTensor  
        x = vtensor.QTensor(x, dtype=vtensor.kfloat64)  
    
        for i in range(x.shape[1]):  
            # 使用实数参数  
            ry(qm, i, x[:, i].reshape((x.shape[0], 1)))  
            rz(qm, i, x[:, i].reshape((x.shape[0], 1)))

def data_process():
    """
    1. 读取数据并完成数据处理
    """  
    """  
    读取数据并完成数据处理  
    """  
    train_data = pd.read_csv('train.csv')  
    test_data = pd.read_csv('test.csv')  

    # 分离特征和目标变量  
    X_train = train_data[['age', 'sex', 'bmi', 'children', 'smoker', 'region']]  
    y_train = train_data['charges'].to_numpy()  
    X_test = test_data[['age', 'sex', 'bmi', 'children', 'smoker', 'region']]  
    y_test = test_data['charges'].to_numpy()  

    # 分类和连续变量处理  
    categorical_cols = ['sex', 'smoker', 'region']  
    continuous_cols = ['age', 'bmi', 'children']  

    # 使用 try-except 处理不同版本的 scikit-learn  
    try:  
        encoder = OneHotEncoder(sparse_output=False)  # 较新版本  
    except TypeError:  
        encoder = OneHotEncoder(sparse=False)  # 早期版本  

    encoded = encoder.fit_transform(X_train[categorical_cols])  
    X_train_encoded = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))  

    # 标准化连续变量  
    scaler = StandardScaler()  
    X_train_continuous = scaler.fit_transform(X_train[continuous_cols])  
    X_train_continuous_df = pd.DataFrame(X_train_continuous, columns=continuous_cols)  

    # 合并特征  
    X_train_preprocessed = pd.concat([X_train_encoded, X_train_continuous_df], axis=1)  

    # 处理测试集（使用训练集的编码器和缩放器）  
    encoded_test = encoder.transform(X_test[categorical_cols])  
    X_test_encoded = pd.DataFrame(encoded_test, columns=encoder.get_feature_names_out(categorical_cols))  
    X_test_continuous = scaler.transform(X_test[continuous_cols])  
    X_test_continuous_df = pd.DataFrame(X_test_continuous, columns=continuous_cols)  
    X_test_preprocessed = pd.concat([X_test_encoded, X_test_continuous_df], axis=1)  

    # 转换为QTensor  
    X_train = tensor.QTensor(X_train_preprocessed.to_numpy(), requires_grad=True)  
    y_train = tensor.QTensor(y_train.reshape(-1, 1), requires_grad=True)  
    X_test = tensor.QTensor(X_test_preprocessed.to_numpy(), requires_grad=True)  
    y_test = tensor.QTensor(y_test.reshape(-1, 1), requires_grad=True)  

    return X_train, y_train, X_test, y_test        
    
class VariationQuantumCircuit():
    """
    2. 在这里完成量子线路的设计
    """
    def __init__(self, n_qubits, n_layers=2):  
        super().__init__()  
        self.n_qubits = n_qubits  
        self.n_layers = n_layers  
        
        # Initialize QMachine with the correct dtype  
        self.qm = QMachine(n_qubits, dtype=tensor.kcomplex128)  
        
        # Define trainable parameters  
        self.weights = Parameter((n_layers, n_qubits, 3), dtype=tensor.kcomplex128)  

    def forward(self, x):
        # Reset quantum machine states for the batch size
        self.qm.reset_states(x.shape[0])

        # Encode classical data into quantum states
        QuantumFeatureMap.encode(self.qm, x)

        # Apply the variational quantum circuit
        for layer in range(self.n_layers):
            for qubit in range(self.n_qubits):
                # Obtain parameters directly, ensuring they are numeric values
                # Call real() method to get the real part of the parameter
                rx_param = self.weights[layer, qubit, 0].real()  # 调用方法获取值
                ry_param = self.weights[layer, qubit, 1].real()  # 调用方法获取值
                rz_param = self.weights[layer, qubit, 2].real()  # 调用方法获取值

                # 确保参数是标量值
                # 检查 rx_param 是否是标量
                if not np.isscalar(rx_param):
                    # 如果是数组，提取第一个元素
                    rx_param = rx_param.item()
                if not np.isscalar(ry_param):
                    ry_param = ry_param.item()
                if not np.isscalar(rz_param):
                    rz_param = rz_param.item()

                # 将参数转换为 NumPy 数组
                rx_param = np.asarray(rx_param, dtype=np.float64)
                ry_param = np.asarray(ry_param, dtype=np.float64)
                rz_param = np.asarray(rz_param, dtype=np.float64)

                # 确保参数在传递给 QTensor 时是正确的形状
                rx_param_tensor = tensor.QTensor(rx_param.reshape(1), dtype=tensor.kfloat64)
                ry_param_tensor = tensor.QTensor(ry_param.reshape(1), dtype=tensor.kfloat64)
                rz_param_tensor = tensor.QTensor(rz_param.reshape(1), dtype=tensor.kfloat64)

                # 应用量子操作
                rx(self.qm, qubit, rx_param_tensor)  
                ry(self.qm, qubit, ry_param_tensor)  
                rz(self.qm, qubit, rz_param_tensor)  

            # Entanglement layer
            for i in range(self.n_qubits - 1):
                cnot(self.qm, [i, i + 1])

        # Measure the quantum state
        return MeasureAll(obs={'Z0': 1})(self.qm)


class QuantumNN(Module):
    """
    3. 在这里完成初始化量子神经网络模型的代码
    """
    """  
    量子神经网络模型  
    """  
    def __init__(self, input_size, output_size, n_qubits, n_layers=2):  
        super().__init__()  
        self.vqc = VariationQuantumCircuit(n_qubits, n_layers)  
        self.fc = Linear(n_qubits, output_size, dtype=tensor.kfloat64)  

    def forward(self, x):  
        # 打印输入的形状以便调试  
        print("Input shape before fc:", x.shape)  

        # 执行全连接层  
        x = self.fc(x)  

        return x    
         

def quantum_model_train():
    """  
    4. 在这里完成训练量子模型的代码  
    """  
    """  
    训练量子模型  
    """  
    X_train, y_train, X_test, y_test = data_process()  
    
    # 初始化模型  
    model = QuantumNN(  
        input_size=X_train.shape[1],   
        output_size=1,   
        n_qubits=X_train.shape[1],  
        n_layers=2  
    )  
    
    # 优化器和损失函数  
    optimizer = Adam(model.parameters(), lr=0.001)  
    loss_fn = MeanSquaredError()  
    
    # 训练过程  
    num_epochs = 100  
    for epoch in range(num_epochs):  
        optimizer.zero_grad()  
        
        # 前向传播  
        output = model(X_train)  
        
        # 计算损失  
        loss = loss_fn(output, y_train)  
        
        # 反向传播  
        loss.backward()  
        optimizer.step()  
        
        if (epoch + 1) % 10 == 0:  
            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {loss.item()}")  
    
    return model   

def quantum_model_test(model):
    """  
    5. 使用测试数据集验证模型  
    """  
    _, _, X_test, y_test = data_process()  # 获取处理后的测试集特征和标签  

    model.eval()  # 切换到评估模式  
    with no_grad():  # 使用模块级的 no_grad 上下文管理器  
        predictions = model(X_test)  # 使用模型进行预测  

    # 计算RMSE  
    rmse = np.sqrt(np.mean((predictions.numpy() - y_test.numpy()) ** 2))  
    print("Test RMSE:", rmse)  

    # 保存RMSE结果到文件  
    with open("results.txt", "w") as f:  
        f.write(f"RMSE: {rmse}\n")

if __name__ == "__main__":
    model=quantum_model_train()

    quantum_model_test(model)