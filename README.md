# 基于LoRA微调的大语言模型中文金融情感分类研究

> 应用统计学本科毕业论文项目

远程仓库：[Celyn-number3/undergrad-thesis-crw](https://github.com/Celyn-number3/undergrad-thesis-crw)（私有）。

## Agent 工作入口

开始任务前，请读 [Skills 使用指南中的项目操作约定](skills/README.md)。本项目采用 **skill/README 指导 + Agent 按需执行 + 复用现有脚本**，不为使用技能引入 Modex 后端、Electron、数据库或新工具框架。

`skills/` 是参考流程和资源；`runtime/` 是已复制的本地运行环境，不等于自动启用。已有统计代码和 Word 生成链路保留，缺失能力按实际任务处理，不照搬旧迁移计划。`runtime/` 约 8 GB，现已由 `.gitignore` 排除；本机运行环境、Agent 配置和凭据不随仓库推送。

## 研究简介

本项目以中文金融社交媒体文本情感分类（消极 / 中性 / 积极）为任务，系统比较传统机器学习、中文 BERT 与大语言模型（Qwen3、Qwen2.5、GLM，零样本 / 少样本 / LoRA 微调及 QLoRA 消融）的表现，并从统计学角度回答：大模型的优势是否显著、在多大数据规模下成立、其预测置信度是否可靠。

## 研究问题

| 编号 | 研究问题 |
| --- | --- |
| RQ1 | 大模型相比传统方法是否更优？差异是否统计显著？ |
| RQ2 | 在固定数据划分下，模型差异能否经受训练重复和多重比较检验？ |
| RQ3 | 训练样本量、LoRA 秩和量化配置的单次探索结果如何？ |
| RQ4 | 大模型预测置信度是否可靠？拒绝低置信度样本能否提高准确率？ |

## 数据

- FinFE（BBT-CFLEB 基准）：中文金融社交媒体文本情感三分类，公开文件去重重划分后：训练 8802 / 验证 979 / 测试 1713
- 来源：[BBT-FinCUGE-Applications](https://github.com/supersymmetry-technologies/BBT-FinCUGE-Applications)

## 方法

- 模型：TF-IDF + 逻辑回归 / SVM、BERT、RoBERTa-wwm-ext；Qwen3-8B、Qwen2.5-7B、GLM-4-9B 的零/少样本及 LoRA 微调；Qwen3 QLoRA 消融
- 统计评估：3 个训练种子、单因素 ANOVA / Welch / Tukey、McNemar + Holm、50000 次配对 Bootstrap + 十对比较的 Bonferroni 区间；未实施原计划的模型规模比较和学习曲线幂律拟合
- 可靠性：ECE、Brier、测试分布内温度交叉拟合、选择性预测、保形预测与单元素子集准确率；历史零样本概率精度另做敏感性分析

## 实验环境

- GPU：NVIDIA RTX 3090（24GB）
- 工具：Python、PyTorch、transformers、peft、scikit-learn、statsmodels

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
- [x] 补充分析：训练/验证曝光、共同未曝光文本比较、重复记录一致性和噪声情景推算、保形预测
- [x] 论文初稿：摘要、第 1–5 章、参考文献（`docs/thesis-draft.docx`，由 `scripts/build_draft.py` 合并生成）
- [x] 第一轮方法审查与修订：代码、正文、摘要、结论及 Word 同步；见 `docs/mcp-methodology-revision-round1.md`
- [x] 数字检索初筛（`scripts/check_numbers.py`）；仅检查数值能否找到，不替代逐表和论断核验
- [ ] 取得高精度零样本概率或 logits 后复核 NLL 和温度（本轮未重跑推理）
- [ ] 导师意见与修改
- [ ] 套学校模板、公式编辑器重排公式、致谢
- [ ] 中期检查、终稿、答辩

> 论文 Word 生成：各章修改后运行 `python scripts/build_draft.py`，再用 `scripts/md2docx.py` 转 docx。

## 仅重算现有预测的分析入口

以下命令在项目根目录运行，会更新 `outputs/analysis/`，不训练模型或改写预测 CSV：

```bash
python -m src.analysis.stats
python -m src.analysis.conformal
python -m src.analysis.leakage
python -m src.analysis.label_noise
python -m src.analysis.probability_precision
```

历史开题和选题方案保留为过程记录；当前执行范围以正文与本 README 为准。
