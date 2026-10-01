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
| RQ4 | 大模型预测置信度是否可靠？拒绝低置信度样本能否提高准确率？ |

## 数据

- FinFE（BBT-CFLEB 基准）：中文金融社交媒体文本情感三分类，公开文件去重重划分后：训练 8802 / 验证 979 / 测试 1713
- 来源：[BBT-FinCUGE-Applications](https://github.com/supersymmetry-technologies/BBT-FinCUGE-Applications)

## 方法

- 模型：TF-IDF + 逻辑回归 / SVM、RoBERTa-wwm-ext、Qwen3 零样本与少样本、Qwen3 + QLoRA
- 统计评估：多随机种子、McNemar 检验、Bootstrap 置信区间、Holm 校正、双因素方差分析、学习曲线幂律拟合
- 可靠性：ECE、Brier 分数、可靠性图、温度缩放、选择性预测（覆盖率-准确率曲线、AURC）、误差分析与卡方检验

## 实验环境

- GPU：NVIDIA RTX 3090（24GB）
- 工具：Python、PyTorch、transformers、LLaMA-Factory、scikit-learn、statsmodels

## 目录结构

```text
.
├── docs/
│   ├── mcp-thesis-topic-plan.md   # 选题完整方案
│   ├── mcp-thesis-proposal.md     # 开题报告（Markdown）
│   ├── thesis-proposal.docx       # 开题报告（Word）
│   ├── mcp-literature-review.md   # 文献综述（Markdown）
│   ├── literature-review.docx     # 文献综述（Word）
│   ├── mcp-foreign-translation.md # 外文翻译（Markdown）
│   ├── foreign-translation.docx   # 外文翻译（Word）
│   └── foreign-translation-original.pdf # 外文翻译原文
└── README.md
```

## 文档

- [选题完整方案](docs/mcp-thesis-topic-plan.md)
- [开题报告（Markdown）](docs/mcp-thesis-proposal.md)
- [开题报告（Word）](docs/thesis-proposal.docx)
- [文献综述（Markdown）](docs/mcp-literature-review.md)
- [文献综述（Word）](docs/literature-review.docx)
- [外文翻译（Markdown）](docs/mcp-foreign-translation.md)
- [外文翻译（Word）](docs/foreign-translation.docx)
- [外文翻译原文（PDF）](docs/foreign-translation-original.pdf)

## 进度

- [x] 确定选题与研究方案
- [x] 开题报告（数据划分已更正为 8802 / 979 / 1713）
- [x] 文献综述
- [x] 外文翻译
- [x] 环境配置与数据探索
- [x] 实验 E1–E5（基线、零/少样本、LoRA 多种子、统计检验、校准与选择性预测、消融）
- [x] 补充实验：数据泄漏分析、标注噪声上限估计、保形预测
- [x] 论文初稿：摘要、第 1–5 章、参考文献（`docs/thesis-draft.docx`，由 `scripts/build_draft.py` 合并生成）
- [x] 全文数字核对（`scripts/check_numbers.py`）
- [ ] 导师意见与修改
- [ ] 套学校模板、公式编辑器重排公式、致谢
- [ ] 中期检查、终稿、答辩

> 论文 Word 生成：各章修改后运行 `python scripts/build_draft.py`，再用 `scripts/md2docx.py` 转 docx。
