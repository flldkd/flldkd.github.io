from pyqpanda3.core import *
import numpy as np
import pandas as pd

from pyqpanda3.core import *
import numpy as np

class SecondOrderPauliZEncoder:
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.qc = QCircuit()  # 初始化量子电路

    def distance_measure(self, features):
        # 计算特征矩阵之间的距离（使用欧几里得距离）
        distance_matrix = np.zeros((len(features), len(features)))
        for i in range(len(features)):
            for j in range(len(features)):
                # 计算第 i 行和第 j 行特征向量之间的距离
                distance_matrix[i][j] = np.linalg.norm(features[i] - features[j])
        return distance_matrix

    def encode(self, features):
        # 初始化量子比特
        self.qc << BARRIER([self.n_qubits])  # 在所有量子比特上施加障碍门
        for i in range(self.n_qubits):
            self.qc << H(i)  # 对每个量子比特应用 Hadamard 门

        # 计算特征的距离矩阵
        distance_matrix = self.distance_measure(features)

        # 根据距离矩阵编码数据
        for i in range(self.n_qubits):
            for j in range(self.n_qubits):
                if i != j:
                    angle = distance_matrix[i][j]  # 获取距离值
                    angle = float(angle) * np.pi  # 确保是浮点数，角度单位化
                    self.qc << RZ(i, angle)  # 在第 i 个量子比特上应用 RZ 门
        print(draw_qprog(self.qc))
        # 使用 measure 进行量子比特测量
        for i in range(self.n_qubits):
            self.qc << measure(i, i)  # 测量第 i 个量子比特并将结果存储到经典比特

        return self.qc

# 读取你的数据集
data = {
    'age': [46, 47, 52, 39, 54, 63],
    'sex': ['female', 'female', 'female', 'female', 'female', 'male'],
    'bmi': [19.95, 24.32, 24.86, 34.32, 21.47, 41.47],
    'children': [2, 0, 0, 5, 3, 0],
    'smoker': ['no', 'no', 'no', 'no', 'no', 'no'], 
    'region': ['northwest', 'northeast', 'southeast', 'southeast', 'northwest', 'southeast'],
    'charges': [9193.8385, 8534.6718, 27117.99378, 8596.8278, 12475.3513, 13405.3903]
}

# 创建 DataFrame 并对类别型特征进行独热编码
df = pd.DataFrame(data)
df_encoded = pd.get_dummies(df, columns=['sex', 'smoker', 'region'], drop_first=True)

# 特征和标签选择
features = df_encoded.drop(columns=['charges']).values  # 获取特征值
print("原始特征数据:")
print(features)  # 打印原始特征数据以调试

# 确保所有特征都是数值型后进行标准化
features = features.astype(float)  # 强制转换为浮点型
features_mean = np.mean(features, axis=0)
features_std = np.std(features, axis=0)

# 打印标准化前的均值和标准差以调试
print("均值:", features_mean)
print("标准差:", features_std)

# 标准化特征
features = (features - features_mean) / features_std

# 创建量子比特数目
n_qubit = features.shape[1]  # 特征数作为量子比特数

# 创建编码器并对特征进行编码
encoder = SecondOrderPauliZEncoder(n_qubit)
quantum_circuit = encoder.encode(features)

# 运行量子程序
qvm = CPUQVM()  # 初始化 CPU 量子虚拟机
prog = QProg()   # 初始化量子程序
prog << quantum_circuit  # 将量子电路添加到程序中

# 打印生成的量子电路
print("生成的量子电路:")
print(draw_qprog(quantum_circuit))

# 运行程序并获取结果
requests = qvm.run(prog, 1024)  # 运行1024次
print("概率字典:", qvm.result().get_prob_dict())
print("状态向量:", qvm.result().get_state_vector())