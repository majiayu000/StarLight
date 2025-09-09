### 手写Transformer实现
### Attention(Q,K,V) = softmax(QK^T / √d_k)V


import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import numpy

def scaled_dot_product_attention(Q, K, V, mask=None):
    """缩放点积注意力函数
    
    Q (查询)：表示"爱"想要关注什么信息
    K (键)：每个词("我"、"爱"、"吃"、"苹果")提供的索引信息
    V (值)：每个词的实际语义内容
    
    步骤1：计算注意力分数: scores = Q x k ^ T
        T 表示转置 (Transpose)
        Q的形状：(batch_size, seq_len, d_k)
        K的形状：(batch_size, seq_len, d_k)
        K^T的形状：(batch_size, d_k, seq_len)
        scores的形状：(batch_size, seq_len, seq_len)
    
    步骤2：缩放: scaled_scores = scores / √d_k
        d_k 是 K 的最后一个维度大小
        为什么要缩放？防止softmax饱和
    步骤3：应用mask（如果有）: scaled_scores += (mask * -1e9)
        Mask用来"遮蔽"某些位置，让模型不要关注这些位置
        两种常见的Mask：
        1. Padding Mask（填充遮蔽）
        2. Look-ahead Mask（前瞻遮蔽）
    步骤4：计算注意力权重: attention_weights = softmax(scaled_scores, dim=-1)
    步骤5：加权求和: output = attention_weights x V
    """
    
    d_k = Q.shape[-1]
    # 步骤1：计算注意力分数 Q × K^T
    scores = Q.matmul(K.transpose(-2, -1))

    # 步骤2：缩放
    scores = scores / math.sqrt(d_k)
    
    # 步骤3：应用mask（如果有）
    if mask is not None:
        scores = scores + (mask * -1e9)
        
    # 步骤4：计算注意力权重
    attention_weights = F.softmax(scores, dim=-1)
    
    # 步骤5：加权求和
    output = torch.matmul(attention_weights, V)
    
    return output
