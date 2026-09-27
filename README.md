# 基于LoRA微调的大语言模型中文金融情感分类研究

> 应用统计学本科毕业论文项目

## 研究简介

本项目以中文金融社交媒体文本情感分类（消极 / 中性 / 积极）为任务，系统比较传统机器学习、中文 BERT 与大语言模型（Qwen3，零样本 / 少样本 / QLoRA 微调）的表现，并从统计学角度回答：大模型的优势是否显著、在多大数据规模下成立、其预测置信度是否可靠。

## 研究问题

| 编号 | 研究问题 |
| --- | --- |
| RQ1 | 大模型相比传统方法是否更优？差异是否统计显著？ |
| RQ2 | 标注数据量多少时大模型才具有优势？（核心） |
| RQ3 | 模型规模（1.7B / 4B / 8B）对性能与成本的影响 |
| RQ4 | 大模型预测置信度是否校准良好？主要错误类型是什么？ |

## 数据

- FinFE（BBT-CFLEB 基准）：中文金融社交媒体文本情感三分类，训练 8000 / 验证 1000 / 测试 1000
- 来源：[BBT-FinCUGE-Applications](https://github.com/supersymmetry-technologies/BBT-FinCUGE-Applications)

## 方法

- 模型：TF-IDF + 逻辑回归 / SVM、RoBERTa-wwm-ext、Qwen3 零样本与少样本、Qwen3 + QLoRA
- 统计评估：多随机种子、McNemar 检验、Bootstrap 置信区间、Holm 校正、双因素方差分析、学习曲线幂律拟合
- 可靠性：ECE、Brier 分数、可靠性图、温度缩放、误差分析与卡方检验

## 实验环境

- GPU：NVIDIA RTX 3090（24GB）
- 工具：Python、PyTorch、transformers、LLaMA-Factory、scikit-learn、statsmodels

## 目录结构

```text
.
├── docs/
│   └── mcp-thesis-topic-plan.md   # 选题完整方案
└── README.md
```

## 文档

- [选题完整方案](docs/mcp-thesis-topic-plan.md)

## 进度

- [x] 确定选题与研究方案
- [ ] 开题报告
- [ ] 环境配置与数据探索
- [ ] 实验一至实验四
- [ ] 论文撰写
