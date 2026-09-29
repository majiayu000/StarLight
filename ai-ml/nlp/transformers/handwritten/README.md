# 手写Transformer实现

这是一份从零开始学习 Transformer 的笔记。当前已经写好的计算只有缩放点积注意力，放在 `examples/simple_transformer.py`，并由 `examples` 包导出。`components` 和 `models` 仍是空包。

## 项目结构

```
handwritten/
├── README.md
├── know.md
├── softmax.md
├── components/
│   └── __init__.py
├── models/
│   └── __init__.py
├── examples/
│   ├── __init__.py
│   └── simple_transformer.py
└── tests/
    └── __init__.py
```

`know.md` 记录词向量等基础概念，`softmax.md` 记录 softmax 的计算。`tests` 目录里还没有测试模块。

## 学习路线

下面是后续可以补上的内容，不是已经写好的文件：

1. **基础数学工具** - 位置编码、缩放点积注意力
2. **多头注意力机制** - Q、K、V矩阵变换和多头处理
3. **前馈神经网络** - Position-wise Feed-Forward Networks
4. **层归一化和残差连接** - Layer Normalization机制
5. **Encoder层** - 组合各组件构建Encoder
6. **Decoder层** - 实现带masked attention的Decoder
7. **完整Transformer** - 组装完整架构
8. **训练和测试** - 实际使用示例

## 特点

- 缩放点积注意力使用 PyTorch
- `scaled_dot_product_attention` 带有逐步注释
- 包的导入与仓库里实际存在的文件一致

## 开始使用

把 `ai-ml/nlp/transformers/handwritten` 加入 `sys.path` 后，可以从 `examples` 导入 `scaled_dot_product_attention`。
