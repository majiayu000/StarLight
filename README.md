# StarLight

Always keep learning and coding.

Personal programming and AI/ML learning notes, Jupyter notebooks, and small code examples.

Browse [design patterns](fundamentals/design-patterns/),
[programming languages](technologies/languages/),
[databases](technologies/databases/), and [AI/ML](ai-ml/).
This is a learning archive: examples have their own dependencies and are not one installable application.

## 从一个具体问题开始

| 想练习什么 | 从哪里开始 | 如何确认自己理解了 |
| --- | --- | --- |
| Python 责任链：请求怎样传到下一个处理器？ | [责任链示例](fundamentals/design-patterns/responsibility_chain.py) | 对比完整链与从 Squirrel 开始的子链：为什么 Banana 在子链中没人处理？ |
| scikit-learn：如何把预处理和分类器放在同一个 Pipeline？ | [入门 notebook](ai-ml/frameworks/scikit-learn/start.ipynb) | 找到 Iris 的训练/测试划分与 StandardScaler + LogisticRegression，解释为什么预处理应跟随训练过程。 |
| RAG Fusion：多查询的结果怎样用 RRF 合并？ | [Fusion notebook](ai-ml/rag/RAG_fusion/fusion.ipynb) | 阅读 generate_queries 与 reciprocal_rank_fusion，观察同一文档出现在多份排名时分数如何累加。 |

责任链示例仅依赖 Python 标准库，在仓库根目录运行：

```bash
python3 fundamentals/design-patterns/responsibility_chain.py
```

完整链会把 Nut 交给 Squirrel、Banana 交给 Monkey；子链不包含 Monkey，所以
Banana 会留下。可以先预测输出，再执行核对。

scikit-learn notebook 需要对应的 Python/Jupyter 依赖，环境配置和 Pipeline 的
说明可参照 [scikit-learn 官方入门](https://scikit-learn.org/stable/getting_started.html)。
各 notebook 的依赖不同，没有适用于整个档案的统一安装命令。

RAG Fusion 的 `vector_search` 使用随机抽样模拟结果，不连接真实向量数据库。
它适合阅读多查询和 RRF 的结构；不能用其输出评估真实检索质量。模型客户端部分
需要自己的服务配置，运行前先检查调用与费用，不要把凭据提交到 notebook。

这里是个人学习档案，不是 Astro 的 [Starlight 文档站点框架](https://starlight.astro.build/)。
内容问题可在 [本仓库 issue](https://github.com/majiayu000/StarLight/issues) 中附上文件路径与具体疑问。

## 🏗️ 新架构

```
StarLight/
├── fundamentals/              # 基础概念
│   └── design-patterns/      # 设计模式
├── technologies/             # 技术栈
│   ├── languages/            # 编程语言
│   │   ├── python/          # Python相关
│   │   ├── golang/          # Go相关
│   │   ├── javascript/      # JavaScript相关
│   │   └── rust/            # Rust相关
│   ├── databases/           # 数据库
│   │   └── Vector-store/    # 向量数据库
│   └── infrastructure/      # 基础设施
│       └── middleware/      # 中间件
└── ai-ml/                   # AI/ML专门领域
    ├── foundations/         # 基础理论
    ├── frameworks/          # ML框架
    ├── nlp/                # 自然语言处理
    ├── recommendation/      # 推荐系统
    ├── rag/                # 检索增强生成
    └── deployment/         # 模型部署
```

## 📁 内容分类

### 基础概念 (fundamentals/)
- 设计模式 ✅

### 编程语言 (technologies/languages/)
- Python: FastAPI, Django, 数据类等 ✅
- Golang: Gin, 文件服务等 ✅
- JavaScript: React, Next.js等 ✅
- Rust: Actix等 ✅

### AI/ML (ai-ml/)
- 基础理论: 机器学习概念 ✅
- 框架: TensorFlow, scikit-learn ✅
- NLP: LangChain, LlamaIndex, OpenAI ✅
- 推荐系统: 协同过滤, 矩阵分解 ✅
- RAG: 检索增强生成 ✅

### 基础设施 (technologies/)
- 数据库: 向量存储 ✅
- 中间件: ELK, Kafka, RocketMQ ✅

