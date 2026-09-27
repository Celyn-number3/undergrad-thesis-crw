# 本科毕业论文开题报告

| 项目 | 内容 |
| --- | --- |
| 论文题目 | 基于LoRA微调的大语言模型中文金融情感分类研究 |
| 学生姓名 | （待填写） |
| 学号 | （待填写） |
| 专业 | 应用统计学 |
| 指导教师 | （待填写） |
| 日期 | 2026年10月 |

## 一、选题背景与研究意义

### （一）选题背景

金融市场参与者的情绪是影响资产价格的重要因素。随着互联网的普及，股吧、雪球、微博等金融社交媒体每天产生海量文本，这些文本中蕴含的投资者情绪已被大量研究证明与市场收益、成交量和波动率存在关联。如何从非结构化文本中准确、高效地识别情感倾向，是金融文本分析的基础性问题。

金融情感分析经历了三个阶段：早期基于情感词典的方法，依赖人工构建的金融词表，对上下文和新词的适应性较差；随后以 TF-IDF 特征结合逻辑回归、支持向量机等为代表的传统机器学习方法，需要较多人工特征工程；近年来以 BERT 为代表的预训练语言模型通过“预训练 + 微调”范式显著提升了分类效果，FinBERT 等金融领域模型也相继出现。

2023 年以来，以 GPT、Qwen 等为代表的大语言模型（Large Language Model, LLM）展现出强大的语言理解和零样本、少样本学习能力，金融领域出现了 BloombergGPT、FinGPT 等专门模型。然而，大模型参数量巨大，全参数微调需要昂贵的计算资源。以 LoRA（Low-Rank Adaptation）及其量化版本 QLoRA 为代表的参数高效微调方法，只训练少量低秩矩阵参数，使得在单张消费级显卡上微调数十亿参数的大模型成为可能。

### （二）问题的提出

尽管大模型在情感分析上表现突出，现有研究仍存在以下不足：

1. **中文金融三分类场景研究不足**。已有研究多基于英文数据集（如 Financial PhraseBank）；少数涉及中文的研究使用的是仅区分积极与消极的二分类数据，任务难度偏低。中文金融社交媒体文本口语化强、包含大量股市黑话与反讽，且“中性”类最难判别，大模型在其中的表现有待系统评估。
2. **缺少统计显著性检验**。多数研究仅比较准确率或 F1 值的高低，很少检验模型之间的差异是否具有统计显著性，也较少报告多次实验的波动，结论的可靠性不足。
3. **对“数据规模”的讨论缺少统计推断**。实际应用中标注数据往往昂贵且稀缺。已有研究虽然观察到大模型在少量数据下即可取得较好效果，但多为单次实验的描述性比较，未对优势是否显著、优势随数据量如何变化进行统计检验。
4. **较少关注预测置信度的可靠性**。在金融决策中，模型不仅要“判断对”，还要“知道自己有多大把握”。微调后的大模型普遍存在过度自信问题，但在金融情感分析中，置信度校准以及“低置信度样本交由人工处理”的选择性预测机制尚缺乏研究。

### （三）研究意义

**理论意义**：将统计假设检验、方差分析、置信度校准等统计方法系统引入大模型评估，为机器学习模型比较提供更严谨的统计框架；通过样本量实验刻画大模型的样本效率，丰富对参数高效微调方法适用边界的认识。

**实践意义**：为金融机构和研究者在不同数据条件和计算资源下选择情感分析模型提供可操作的参考依据，例如“标注数据不足多少条时宜采用大模型”；同时验证了在单张消费级显卡上开展大模型微调研究的可行性。

## 二、国内外研究现状

### （一）金融文本情感分析

Tetlock（2007）利用《华尔街日报》专栏文本构建悲观情绪指标，发现媒体悲观情绪能够预测市场收益的下行压力，奠定了文本情绪研究的基础。Loughran 和 McDonald（2011）指出通用情感词典在金融语境中存在大量误判，构建了金融专用词典，成为词典法的代表。Malo 等（2014）发布了 Financial PhraseBank 数据集，成为英文金融情感分析最常用的基准之一。

### （二）预训练语言模型在金融情感分析中的应用

Vaswani 等（2017）提出 Transformer 架构，Devlin 等（2019）在此基础上提出 BERT，开创了“预训练 + 微调”范式。Araci（2019）在金融语料上继续预训练 BERT 得到 FinBERT，在 Financial PhraseBank 上取得明显提升。中文方面，Cui 等（2021）提出基于全词掩码的中文预训练模型 RoBERTa-wwm-ext；Lu 等（2023）构建了中文金融语料库 BBT-FinCorpus 和中文金融评测基准 BBT-CFLEB，其中 FinFE 为中文金融社交媒体情感分类数据集，GPT2、T5、FinBERT 等模型在其上的准确率约为 79%～80%。

### （三）大语言模型与参数高效微调

Brown 等（2020）提出的 GPT-3 展示了大模型的少样本学习能力；Kaplan 等（2020）揭示了模型性能与参数量、数据量之间的幂律关系。金融领域中，Wu 等（2023）训练了 500 亿参数的 BloombergGPT；Yang 等（2023）提出开源的 FinGPT 框架；Zhang 等（2023）通过指令微调将通用大模型用于金融情感分析，取得了优于 BERT 类模型的效果。在参数高效微调方面，Hu 等（2022）提出 LoRA，通过低秩分解近似权重更新，大幅减少可训练参数；Dettmers 等（2023）提出 QLoRA，结合 4-bit 量化进一步降低显存需求；Zheng 等（2024）开发的 LlamaFactory 框架降低了微调的工程门槛。Yang 等（2025）发布的 Qwen3 系列模型在中文理解方面表现突出，并提供了从 0.6B 到数百亿参数的多种规模。

与本文最为接近的是以下两项研究。Paredes Amorin 等（2025）比较了 FinBERT 与 DeepSeek-LLM 7B、Llama3 8B、Qwen3 8B 三个轻量级大模型在五个金融情感数据集上的表现，并以 5%～100% 的训练数据比例进行微调，发现大模型仅用 5% 的数据即可取得较好效果；但其中文数据集仅包含积极、消极两类，且研究以单次实验的指标比较为主，未进行显著性检验，也未涉及置信度可靠性。Cheng（2025）使用 LoRA 与 QLoRA 微调 Llama-3.1-8B 和 Qwen3-8B，在英文数据集上均优于 FinBERT，且 QLoRA 在显著降低显存的同时保持了相近的准确率。

### （四）模型比较的统计方法与置信度校准

Dietterich（1998）系统讨论了比较分类算法的统计检验方法，推荐在同一测试集上使用 McNemar 检验（McNemar, 1947）。Efron 和 Tibshirani（1993）提出的 Bootstrap 方法可用于构造评价指标的置信区间；Holm（1979）提出的逐步校正方法可控制多重比较中的第一类错误。Guo 等（2017）发现现代神经网络普遍存在“过度自信”问题，提出用期望校准误差（ECE）度量校准程度，并用温度缩放加以改进；Balabanov 和 Linander（2024）进一步发现经 LoRA 微调的大模型同样存在过度自信现象。在“拒绝判断”方面，Chow（1970）最早提出了分类中错误率与拒识率的权衡理论，Geifman 和 El-Yaniv（2017）将其发展为深度神经网络的选择性分类方法，即模型仅对高置信度样本给出预测，其余交由人工处理。

### （五）研究述评

综上，金融情感分析已从词典法发展到大模型阶段，LoRA/QLoRA 使大模型微调在普通硬件上成为可能，“大模型微调优于 BERT”“大模型在少量数据下即有较好表现”已得到初步验证。但现有研究仍存在三点不足：一是以英文或中文二分类数据为主，缺少对含“中性”类的中文金融社交媒体三分类任务的系统评估；二是多为单次实验的指标比较，缺少重复实验、显著性检验和对样本量效应的统计推断；三是几乎未涉及大模型在金融情感分析中的置信度校准与选择性预测。本文拟从统计学视角弥补上述不足。

## 三、研究内容与研究问题

### （一）研究目标

以中文金融社交媒体文本情感三分类（消极、中性、积极）为任务，系统比较传统机器学习、预训练语言模型与大语言模型的表现，并借助统计方法评估大模型优势的显著性、样本效率与可靠性。

### （二）研究问题

| 编号 | 研究问题 |
| --- | --- |
| RQ1 | 经 LoRA 微调的大模型相比传统方法和 BERT 是否更优？差异是否统计显著？ |
| RQ2 | 标注数据量对各模型的影响如何？大模型在多大数据规模下具有显著优势？（核心问题） |
| RQ3 | 模型参数规模（1.7B、4B、8B）如何影响分类性能与计算成本？ |
| RQ4 | 大模型的预测置信度是否可靠？能否通过拒绝低置信度样本提高预测准确率？主要错误类型有哪些？ |

### （三）主要研究内容

1. **数据分析与预处理**：对 FinFE 数据集进行描述性统计（类别分布、文本长度分布、高频词等），完成去重、冲突标签检查和划分一致性检查。
2. **多模型对比实验**：构建 TF-IDF + 逻辑回归、TF-IDF + SVM、RoBERTa-wwm-ext、Qwen3-8B 零样本/少样本提示、Qwen3-8B + QLoRA 微调共五类模型，比较其分类性能，并进行显著性检验。
3. **样本量实验**：在不同规模的训练子集上训练各模型，分析学习曲线和“模型 × 样本量”交互效应，估计大模型优势不再显著的临界样本量。
4. **模型规模实验**：对 Qwen3-1.7B、4B、8B 分别进行 QLoRA 微调，比较性能、显存占用与训练时间。
5. **可靠性与误差分析**：分析各模型的置信度校准情况，尝试温度缩放改进校准；开展选择性预测分析，考察拒绝低置信度样本后准确率的提升；对错误样本进行分类归纳和统计检验。

## 四、研究方法与技术路线

### （一）数据来源

采用 BBT-CFLEB 基准中的 FinFE 数据集，其为中文金融社交媒体文本情感三分类数据集，训练集 8000 条、验证集 1000 条、测试集 1000 条，已完成标注和划分，可直接公开获取，无需爬虫采集。

### （二）模型方法

1. **传统机器学习**：以 TF-IDF 表示文本，分别采用逻辑回归和线性支持向量机分类，作为基准模型。
2. **预训练语言模型**：采用中文 RoBERTa-wwm-ext，在其输出上接分类层进行全参数微调。
3. **大语言模型提示学习**：以 Qwen3-8B 为基础模型，设计零样本与少样本提示，直接生成情感标签。
4. **LoRA/QLoRA 微调**：LoRA 将预训练权重的更新量 ΔW 分解为两个低秩矩阵的乘积，即 W = W₀ + BA，其中 B ∈ R^{d×r}，A ∈ R^{r×k}，r ≪ min(d, k)，训练时冻结 W₀，仅更新 A 和 B；QLoRA 进一步将 W₀ 量化为 4-bit，使 8B 模型可在 24GB 显存上完成微调。微调采用指令格式，基于 LlamaFactory 框架实现。

### （三）评价指标与统计方法

| 类别 | 方法 | 用途 |
| --- | --- | --- |
| 分类指标 | 准确率、宏平均 F1、各类别精确率与召回率、混淆矩阵 | 衡量分类性能 |
| 稳定性 | 多随机种子（3～5 次）重复实验，报告均值 ± 标准差 | 排除随机性影响 |
| 显著性检验 | McNemar 检验 | 比较两模型在同一测试集上的差异 |
| 区间估计 | Bootstrap 置信区间 | 给出 F1 的 95% 置信区间 |
| 多重比较 | Holm 校正 | 控制多模型两两比较的第一类错误 |
| 样本量分析 | 学习曲线、双因素方差分析、幂律函数拟合 | 分析数据规模的影响与交互效应 |
| 可靠性 | ECE、Brier 分数、可靠性图、温度缩放 | 评估与改进置信度校准 |
| 选择性预测 | 覆盖率-准确率曲线、AURC（风险-覆盖率曲线下面积） | 评估拒绝低置信度样本后的准确率提升 |
| 误差分析 | 列联表与卡方检验 | 检验错误是否集中于特定文本特征 |

### （四）实验设计

- **实验一（RQ1）**：全量训练数据下比较五类模型，进行显著性检验与区间估计。
- **实验二（RQ2）**：训练样本量取 100、250、500、1000、2000、4000、8000，每个规模重复抽样 3 次，绘制学习曲线并进行双因素方差分析；在每个样本量上对大模型与 BERT 的差异进行显著性检验，并用 Bootstrap 方法估计“优势不再显著”的临界样本量及其置信区间。
- **实验三（RQ3）**：对 Qwen3-1.7B、4B、8B 进行 QLoRA 微调，比较性能与计算成本，并与实验二结合分析“小模型 + 多数据”与“大模型 + 少数据”的取舍。
- **实验四（RQ4）**：计算各模型的 ECE 与 Brier 分数，绘制可靠性图，比较温度缩放前后的校准效果；按置信度从高到低逐步提高拒识比例，绘制覆盖率-准确率曲线，比较各模型的 AURC，回答“只处理模型最有把握的 80% 样本时准确率能提高多少”等实际问题；对错误样本按反讽、否定、专业术语、中性模糊等类型归纳，并进行卡方检验。

### （五）技术路线

```text
数据获取（FinFE）
  → 描述性统计与预处理
  → 模型构建
      ├─ 传统机器学习：TF-IDF + LR / SVM
      ├─ 预训练模型：RoBERTa-wwm-ext 微调
      ├─ 大模型提示：Qwen3 零样本 / 少样本
      └─ 大模型微调：Qwen3 + QLoRA
  → 实验一：多模型对比与显著性检验
  → 实验二：样本量实验
  → 实验三：模型规模实验
  → 实验四：置信度校准与误差分析
  → 结论与建议
```

## 五、预期创新点

1. **研究场景**：针对含“中性”类、文本口语化的中文金融社交媒体三分类任务，系统评估 Qwen3 系列大模型的参数高效微调效果，补充已有研究多基于英文或中文二分类数据的不足。
2. **统计推断**：通过多次重复实验、McNemar 检验、Holm 校正和“模型 × 样本量”交互效应的方差分析，对大模型的优势及其随数据规模的变化进行严格的统计检验，并给出临界样本量的区间估计，改进已有研究仅做单次描述性比较的做法。
3. **可靠性评价**：将置信度校准与选择性预测引入金融情感分析，考察大模型“是否知道自己何时会出错”，以及拒绝低置信度样本对准确率的提升，为人机协同的金融文本处理提供依据。

## 六、可行性分析

1. **数据可行性**：FinFE 为公开的已标注数据集，规模适中，无需爬虫采集与大规模清洗。
2. **技术可行性**：LlamaFactory、transformers、scikit-learn、statsmodels 等开源工具成熟，文献与教程丰富。
3. **硬件可行性**：本人拥有 NVIDIA RTX 3090（24GB 显存）。在 QLoRA 下，8B 模型微调约需 12～18GB 显存，1 万条短文本单次训练预计在 1 小时左右，可满足全部实验需求。
4. **专业可行性**：研究所需的假设检验、方差分析、回归拟合等方法均为应用统计学专业课程内容。

## 七、预期困难与解决方案

| 可能困难 | 解决方案 |
| --- | --- |
| 实验组合多、计算时间长，初稿截止时间早（2027年1月15日） | 样本量实验优先使用 BERT 和 Qwen3-1.7B/4B，8B 仅在关键样本量上运行；合理安排夜间批量实验 |
| 大模型生成的标签格式不规范 | 在提示中限定输出格式，并编写规则解析；对无法解析的输出单独统计 |
| 大模型优势不显著 | 如实报告结果，不显著本身也是有价值的结论，可据此给出小数据与大数据场景下的选择建议 |
| 中性类识别困难、类别不平衡 | 采用宏平均 F1 作为主要指标，并进行分类别分析 |
| 编程与调试经验不足 | 采用成熟框架减少手写代码，提前完成环境配置与小规模试跑 |

## 八、研究进度安排

根据《数理学院2027届本科毕业设计（论文）时间安排和具体工作要求》，结合本课题实验量较大的特点，将全部实验安排在论文初稿截止前完成，具体安排如下：

| 时间 | 工作内容 | 学院节点 |
| --- | --- | --- |
| 2026年10月9日前 | 确定选题 | 完成选题（10月9日） |
| 2026年10月10日—10月16日 | 接收任务书，查阅文献 | 任务书下达（10月16日） |
| 2026年10月17日—11月7日 | 撰写开题报告；配置实验环境，获取 FinFE 数据，完成描述性统计与预处理 | 提交开题报告（11月7日） |
| 2026年11月8日—11月30日 | 完成传统机器学习、BERT 基准实验和大模型提示实验；完成 Qwen3 QLoRA 微调与实验一 | 开题报告审核（11月19日） |
| 2026年12月1日—12月19日 | 完成实验二（样本量实验）；撰写文献综述，完成外文翻译 | 提交文献综述、外文翻译（12月19日） |
| 2026年12月20日—12月31日 | 完成实验三（模型规模实验）与实验四（校准与误差分析）；整理实验结果 | 文献综述、外文翻译审核 |
| 2027年1月1日—1月15日 | 撰写并提交论文初稿 | 提交论文初稿（1月15日） |
| 2027年1月16日—3月6日 | 根据指导教师意见修改论文，补充实验，准备中期检查 | 中期检查（开学前；3月6日） |
| 2027年3月7日—4月9日 | 完善论文，查重，提交终稿 | 提交论文终稿（4月9日） |
| 2027年4月10日—5月6日 | 根据评阅意见修改，准备答辩 | 评阅（4月23日）、交叉评阅（4月30日）、答辩（5月6日） |

注：具体时间节点以学院最新通知为准。

## 九、论文结构安排

1. 第1章 绪论：研究背景与意义、国内外研究现状、研究内容与创新点、论文结构。
2. 第2章 相关理论与方法：TF-IDF、逻辑回归与支持向量机、Transformer 与 BERT、大语言模型与提示学习、LoRA/QLoRA 原理、统计检验方法、校准理论与选择性预测。
3. 第3章 数据与实验设计：数据集介绍、描述性统计、数据预处理、实验环境与参数设置、评价指标。
4. 第4章 实验结果与分析：多模型对比、样本效率、模型规模、置信度校准与选择性预测四个实验的结果与分析。
5. 第5章 结论与展望：主要结论、实践建议、不足与展望。

## 十、参考文献

[1] Tetlock P C. Giving content to investor sentiment: The role of media in the stock market[J]. The Journal of Finance, 2007, 62(3): 1139-1168.

[2] Loughran T, McDonald B. When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks[J]. The Journal of Finance, 2011, 66(1): 35-65.

[3] Malo P, Sinha A, Korhonen P, et al. Good debt or bad debt: Detecting semantic orientations in economic texts[J]. Journal of the Association for Information Science and Technology, 2014, 65(4): 782-796.

[4] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems. 2017: 5998-6008.

[5] Devlin J, Chang M W, Lee K, et al. BERT: Pre-training of deep bidirectional transformers for language understanding[C]//Proceedings of NAACL-HLT. 2019: 4171-4186.

[6] Araci D. FinBERT: Financial sentiment analysis with pre-trained language models[J]. arXiv preprint arXiv:1908.10063, 2019.

[7] Cui Y, Che W, Liu T, et al. Pre-training with whole word masking for Chinese BERT[J]. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 2021, 29: 3504-3514.

[8] Lu D, Wu H, Liang J, et al. BBT-Fin: Comprehensive construction of Chinese financial domain pre-trained language model, corpus and benchmark[J]. arXiv preprint arXiv:2302.09432, 2023.

[9] Brown T, Mann B, Ryder N, et al. Language models are few-shot learners[C]//Advances in Neural Information Processing Systems. 2020: 1877-1901.

[10] Kaplan J, McCandlish S, Henighan T, et al. Scaling laws for neural language models[J]. arXiv preprint arXiv:2001.08361, 2020.

[11] Wu S, Irsoy O, Lu S, et al. BloombergGPT: A large language model for finance[J]. arXiv preprint arXiv:2303.17564, 2023.

[12] Yang H, Liu X Y, Wang C D. FinGPT: Open-source financial large language models[J]. arXiv preprint arXiv:2306.06031, 2023.

[13] Zhang B, Yang H, Liu X Y. Instruct-FinGPT: Financial sentiment analysis by instruction tuning of general-purpose large language models[J]. arXiv preprint arXiv:2306.12659, 2023.

[14] Hu E J, Shen Y, Wallis P, et al. LoRA: Low-rank adaptation of large language models[C]//International Conference on Learning Representations. 2022.

[15] Dettmers T, Pagnoni A, Holtzman A, et al. QLoRA: Efficient finetuning of quantized LLMs[C]//Advances in Neural Information Processing Systems. 2023.

[16] Zheng Y, Zhang R, Zhang J, et al. LlamaFactory: Unified efficient fine-tuning of 100+ language models[C]//Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations). Bangkok: ACL, 2024: 400-410.

[17] Yang A, Li A, Yang B, et al. Qwen3 technical report[J]. arXiv preprint arXiv:2505.09388, 2025.

[18] McNemar Q. Note on the sampling error of the difference between correlated proportions or percentages[J]. Psychometrika, 1947, 12(2): 153-157.

[19] Dietterich T G. Approximate statistical tests for comparing supervised classification learning algorithms[J]. Neural Computation, 1998, 10(7): 1895-1923.

[20] Efron B, Tibshirani R J. An introduction to the bootstrap[M]. New York: Chapman & Hall, 1993.

[21] Holm S. A simple sequentially rejective multiple test procedure[J]. Scandinavian Journal of Statistics, 1979, 6(2): 65-70.

[22] Guo C, Pleiss G, Sun Y, et al. On calibration of modern neural networks[C]//International Conference on Machine Learning. 2017: 1321-1330.

[23] Paredes Amorin A, Python A, Weisser C. Fine-tuning of lightweight large language models for sentiment classification on heterogeneous financial textual data[J]. arXiv preprint arXiv:2512.00946, 2025.

[24] Cheng X. Financial sentiment analysis with large language models[J]. Finance & Economics, 2025, 3(6). DOI: 10.61173/gvntfv56.

[25] Balabanov O, Linander H. Uncertainty quantification in fine-tuned LLMs using LoRA ensembles[J]. arXiv preprint arXiv:2402.12264, 2024.

[26] Chow C K. On optimum recognition error and reject tradeoff[J]. IEEE Transactions on Information Theory, 1970, 16(1): 41-46.

[27] Geifman Y, El-Yaniv R. Selective classification for deep neural networks[C]//Advances in Neural Information Processing Systems. 2017.
