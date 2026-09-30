# 摘要

金融社交媒体上的投资者评论蕴含丰富的情绪信息，准确识别其情感倾向是金融舆情监测和投资者情绪研究的基础。大语言模型在文本理解上表现突出，LoRA 等参数高效微调方法使其能够在单张消费级显卡上完成微调，但其在中文金融情感分类上相对传统方法的优势是否可靠、给出的置信度能否被信任，仍缺少系统的统计评估。

本文以中文金融社交媒体情感三分类数据集 FinFE 为对象，在单张 RTX 3090 显卡上比较了 TF-IDF 配合逻辑回归和支持向量机、BERT 与 RoBERTa-wwm-ext 微调，以及 Qwen3-8B、Qwen2.5-7B-Instruct、GLM-4-9B 三个开源大模型的零样本、少样本提示与 LoRA 微调，并从统计推断、置信度可靠性和数据质量三个角度进行分析。

研究发现：（1）公开数据的评估集中有 54% 的文本原样出现在训练集中，这种数据泄漏使 TF-IDF 基线的宏平均 F1 虚高 8.1 个百分点，并把其与 RoBERTa 的真实差距缩小约三分之二；本文据此重新构建了无泄漏的数据划分。（2）LoRA 微调的大模型宏平均 F1 为 0.798～0.807，高于 RoBERTa 的 0.778 和 TF-IDF 的 0.70，零样本和少样本提示则明显不及有监督微调。（3）以多随机种子方差分析衡量训练随机性时，大模型的优势显著；以 McNemar 检验和配对 Bootstrap 衡量测试样本抽样误差时，约 2 个百分点的优势仅边缘显著或不显著，说明该优势稳定但幅度较小。（4）零样本大模型平均置信度达 96.4%，而准确率仅 67.1%；LoRA 微调与温度缩放可将期望校准误差降至 0.013～0.030，只处理置信度最高的 50% 样本时准确率约为 96%。（5）重复标注样本的一致率为 82.9%（κ = 0.735），据此估计准确率上限约为 91%，且 82% 的标注冲突涉及中性类，解释了中性类识别困难的原因。此外，4 比特 QLoRA 在峰值显存 11.2 GB 下取得了与 16 位 LoRA 相当的效果。

本文的结果表明，在评估大模型时应同时关注数据质量、统计显著性和置信度的可靠性，可为金融机构开展舆情监测时的模型选型与人机协作提供参考。

**关键词：** 大语言模型；LoRA 微调；金融情感分析；统计检验；置信度校准

# Abstract

Investor comments on financial social media contain rich sentiment information, and identifying their sentiment accurately is fundamental to financial public-opinion monitoring and investor-sentiment research. Large language models (LLMs) excel at text understanding, and parameter-efficient fine-tuning methods such as LoRA make it possible to fine-tune them on a single consumer GPU. However, whether their advantage over traditional methods in Chinese financial sentiment classification is reliable, and whether their confidence scores can be trusted, has not been systematically evaluated from a statistical perspective.

Using FinFE, a three-class Chinese financial social-media sentiment dataset, this thesis compares TF-IDF with logistic regression and support vector machines, fine-tuned BERT and RoBERTa-wwm-ext, and zero-shot prompting, few-shot prompting and LoRA fine-tuning of three open-source LLMs (Qwen3-8B, Qwen2.5-7B-Instruct and GLM-4-9B) on a single RTX 3090 GPU. The results are analysed from three perspectives: statistical inference, confidence reliability and data quality.

The main findings are as follows. (1) In the public data, 54% of the evaluation texts also appear verbatim in the training set. This leakage inflates the macro-F1 of the TF-IDF baseline by 8.1 percentage points and hides about two-thirds of its true gap to RoBERTa; a leakage-free split is therefore constructed. (2) LoRA-tuned LLMs reach a macro-F1 of 0.798–0.807, higher than RoBERTa (0.778) and TF-IDF (0.70), while zero-shot and few-shot prompting fall clearly behind supervised fine-tuning. (3) When training randomness is measured by multi-seed ANOVA, the LLMs' advantage is significant; when test-sample variability is measured by McNemar tests and paired bootstrap, the advantage of about 2 points is only marginally significant or not significant, indicating a stable but small improvement. (4) Zero-shot LLMs are severely overconfident, with a mean confidence of 96.4% against an accuracy of 67.1%. LoRA fine-tuning plus temperature scaling reduces the expected calibration error to 0.013–0.030, and accuracy reaches about 96% when only the 50% most confident samples are answered. (5) Repeatedly annotated texts show an agreement rate of 82.9% (κ = 0.735), implying an accuracy ceiling of about 91%; 82% of annotation conflicts involve the neutral class, which explains why this class is hardest to recognise. In addition, 4-bit QLoRA matches 16-bit LoRA with a peak memory of only 11.2 GB.

These results suggest that evaluations of LLMs should jointly consider data quality, statistical significance and confidence reliability, and they provide a reference for model selection and human–machine collaboration in financial public-opinion monitoring.

**Keywords:** large language models; LoRA fine-tuning; financial sentiment analysis; statistical testing; confidence calibration
