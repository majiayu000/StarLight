# 手写Transformer实现

这是一个从零开始手写的Transformer模型实现，用于深入理解Transformer架构的每个组件。

## 项目结构

```
handwritten/
├── README.md                 # 项目说明
├── requirements.txt          # 依赖包
├── components/              # 核心组件
│   ├── __init__.py
│   ├── attention.py         # 注意力机制
│   ├── embedding.py         # 嵌入层和位置编码
│   ├── feedforward.py       # 前馈神经网络
│   ├── layer_norm.py        # 层归一化
│   └── utils.py            # 工具函数
├── models/                  # 模型定义
│   ├── __init__.py
│   ├── encoder.py          # Encoder层
│   ├── decoder.py          # Decoder层
│   └── transformer.py     # 完整Transformer
├── examples/               # 使用示例
│   ├── __init__.py
│   ├── training.py         # 训练示例
│   ├── inference.py        # 推理示例
│   └── simple_demo.py      # 简单演示
└── tests/                  # 测试文件
    ├── __init__.py
    ├── test_attention.py
    ├── test_components.py
    └── test_models.py
```

## 实现步骤

1. **基础数学工具** - 位置编码、缩放点积注意力
2. **多头注意力机制** - Q、K、V矩阵变换和多头处理
3. **前馈神经网络** - Position-wise Feed-Forward Networks
4. **层归一化和残差连接** - Layer Normalization机制
5. **Encoder层** - 组合各组件构建Encoder
6. **Decoder层** - 实现带masked attention的Decoder
7. **完整Transformer** - 组装完整架构
8. **训练和测试** - 实际使用示例

## 特点

- 纯PyTorch实现，不依赖transformers库
- 详细的代码注释和数学原理解释
- 模块化设计，便于理解和修改
- 包含完整的测试和使用示例

## 开始使用

按照步骤逐个实现每个组件，每个文件都包含详细的注释和使用示例。
