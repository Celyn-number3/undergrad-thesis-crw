# 摘要

金融社交媒体上的投资者评论蕴含丰富的情绪信息，准确识别其情感倾向是金融舆情监测和投资者情绪研究的基础。大语言模型在文本理解上表现突出，LoRA 等参数高效微调方法使其能够在单张消费级显卡上完成微调，但其在中文金融情感分类上相对传统方法的优势是否可靠、给出的置信度能否被信任，需要在明确数据质量与评估口径后加以判断。

本文以中文金融社交媒体情感三分类数据集 FinFE 为对象，在单张 RTX 3090 显卡上比较了 TF-IDF 配合逻辑回归和支持向量机、BERT 与 RoBERTa-wwm-ext 微调，以及 Qwen3-8B、Qwen2.5-7B-Instruct、GLM-4-9B 三个开源大模型的零样本、少样本提示与 LoRA 微调，并从统计推断、置信度可靠性和数据质量三个角度进行分析。

研究发现：（1）原始评估文件中约 54% 的记录与原始训练文件存在规范化文本重叠；本文区分训练与验证曝光，清洗后得到集合间没有完全重复文本的数据划分，并在共同未曝光样本上比较清洗策略。（2）LoRA 微调的大模型宏平均 F1 为 0.798～0.807，高于 RoBERTa 的 0.778 和 TF-IDF 的 0.70；零样本和少样本提示不及有监督微调。（3）在固定数据划分的三个训练种子中，大模型 F1 点估计均更高，多种子方差分析的事后比较显著；但种子 42 的 McNemar 检验和配对 Bootstrap 经多重比较调整后，未检出大模型相对 RoBERTa 的显著优势。（4）Qwen3 零样本平均置信度为 96.4%，准确率为 67.1%；LoRA 模型经测试分布内五折温度交叉拟合后，期望校准误差为 0.013～0.030，只回答高置信度的一半样本时准确率约为 96%。标准保形预测的整体覆盖率约为 90%，约 77%～78% 的集合为单元素，但该子集准确率为 88.7%～89.3%，不具有单独的 90% 正确率保证。（5）重复记录的配对一致率为 82.9%，82% 的冲突涉及中性类；由于缺少独立复标证据，不将噪声模型推算值解释为实测准确率上限。种子 42 的错误分析中，Qwen3 LoRA 的 307 条错误有 250 条涉及中性类；固定抽样案例用于说明边界，不作因果归因。此外，单次 4 比特 QLoRA 实验在框架记录的峰值分配显存 11.2 GB 下取得了与 16 位 LoRA 接近的效果。

本文的结果表明，在评估大模型时应同时关注数据质量、统计显著性和置信度的可靠性，可为金融机构开展舆情监测时的模型选型与人机协作提供参考。

**关键词：** 大语言模型；LoRA 微调；金融情感分析；统计检验；置信度校准

# Abstract

Investor comments on financial social media contain rich sentiment information, and identifying their sentiment accurately is fundamental to financial public-opinion monitoring and investor-sentiment research. Large language models (LLMs) excel at text understanding, and parameter-efficient fine-tuning methods such as LoRA make it possible to fine-tune them on a single consumer GPU. However, whether their advantage over traditional methods in Chinese financial sentiment classification is reliable, and whether their confidence scores can be trusted, requires evaluation under explicit data-quality and statistical assumptions.

Using FinFE, a three-class Chinese financial social-media sentiment dataset, this thesis compares TF-IDF with logistic regression and support vector machines, fine-tuned BERT and RoBERTa-wwm-ext, and zero-shot prompting, few-shot prompting and LoRA fine-tuning of three open-source LLMs (Qwen3-8B, Qwen2.5-7B-Instruct and GLM-4-9B) on a single RTX 3090 GPU. The results are analysed from three perspectives: statistical inference, confidence reliability and data quality.

The main findings are as follows. (1) About 54% of the original evaluation records share normalized text with the original training file. Training exposure is distinguished from validation exposure; cleaning removes exact cross-split duplicates, and cleaning strategies are compared on shared unexposed examples. (2) LoRA-tuned LLMs achieve a macro-F1 of 0.798–0.807, compared with 0.778 for RoBERTa and about 0.70 for TF-IDF. Zero-shot and few-shot prompting perform worse than supervised fine-tuning. (3) The LLMs have higher F1 point estimates across the three training seeds on the fixed data split, with significant post-hoc comparisons in the multi-seed analysis. However, for seed 42, McNemar tests and paired bootstrap intervals do not establish a significant advantage over RoBERTa after multiplicity adjustment. (4) Zero-shot Qwen3 has a mean confidence of 96.4% but an accuracy of 67.1%. Five-fold temperature cross-fitting within the test distribution gives LoRA models an expected calibration error of 0.013–0.030; accuracy is about 96% when answering only the most confident half of the examples. Standard conformal prediction achieves about 90% overall set coverage, with 77%–78% singleton sets. Accuracy within the singleton subset is 88.7%–89.3%, not a separately guaranteed 90%. (5) Duplicate-record pairs agree on 82.9% of labels, and 82% of conflicts involve the neutral class. Without evidence of independent reannotation, a noise-model calculation is not interpreted as an empirical accuracy ceiling. For seed 42, 250 of Qwen3 LoRA’s 307 errors involve the neutral class; deterministically sampled cases illustrate boundaries without causal attribution. In one run, 4-bit QLoRA performs comparably to 16-bit LoRA, with 11.2 GB of peak framework-allocated GPU memory.

These results suggest that evaluations of LLMs should jointly consider data quality, statistical significance and confidence reliability, and they provide a reference for model selection and human–machine collaboration in financial public-opinion monitoring.

**Keywords:** large language models; LoRA fine-tuning; financial sentiment analysis; statistical testing; confidence calibration
