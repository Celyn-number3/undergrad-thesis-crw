# 文献综述：大语言模型在金融文本情感分类中的应用与评估

| 项目 | 内容 |
| --- | --- |
| 论文题目 | 基于LoRA微调的大语言模型中文金融情感分类研究 |
| 学生姓名 | （待填写） |
| 学号 | （待填写） |
| 专业 | 应用统计学 |
| 指导教师 | （待填写） |

## 摘要

金融文本情感分析是行为金融学与自然语言处理的交叉领域，对理解投资者情绪、预测市场波动具有重要价值。本文围绕“基于LoRA微调的大语言模型中文金融情感分类”这一选题，从五个方面梳理国内外相关研究：一是金融文本情感与资产价格关系的实证研究；二是金融情感分析方法从情感词典、传统机器学习到预训练语言模型的演进；三是大语言模型及其参数高效微调方法在金融情感分析中的应用；四是中文金融情感分析的数据资源与研究进展；五是模型比较的统计检验方法以及置信度校准与选择性预测研究。在此基础上，本文总结了现有研究在中文三分类场景、统计推断和可靠性评价三个方面的不足，并提出本课题的研究方向。

**关键词**：金融情感分析；大语言模型；LoRA；统计检验；置信度校准

## 一、引言

投资者情绪是行为金融学的核心概念之一。传统金融理论假设投资者完全理性，而大量实证研究表明，投资者情绪会引起资产价格偏离基本面价值。随着互联网的发展，财经新闻、股吧、雪球、微博等平台每天产生海量文本，为度量投资者情绪提供了新的数据来源。沈艳等（2019）系统梳理了文本大数据在经济学和金融学中的应用，指出文本数据具有来源多样、增长快和高频等特征，并将文本信息提取方法归纳为词典法、机器学习方法和深度学习方法三类。

情感分类是文本情绪度量的基础环节，其准确性直接决定了后续实证研究的可靠性。近年来，以 GPT、LLaMA、Qwen 为代表的大语言模型（Large Language Model, LLM）快速发展，为金融情感分析带来了新的技术路径；以 LoRA 为代表的参数高效微调方法，使研究者能够在消费级显卡上微调数十亿参数的大模型。然而，大模型在中文金融场景中的表现如何、其优势是否具有统计显著性、其预测是否可靠，仍有待系统研究。本文围绕上述问题对相关文献进行梳理和评述。

## 二、金融文本情感与资产价格

### （一）国外研究

Tetlock（2007）以《华尔街日报》“与市场同行”专栏为样本，利用通用心理学词典构建媒体悲观情绪指标，发现高悲观情绪预示着次日市场价格下行，且异常高或低的悲观情绪预示着较高的成交量，这一研究开创了用文本度量投资者情绪的先河。Loughran 和 McDonald（2011）进一步指出，通用情感词典中近四分之三的“负面词”在金融语境下并不具有负面含义（如 liability、tax、cost 等），因此构建了金融领域专用词典（LM 词典），显著提升了金融文本情绪度量的准确性。这两项研究表明，金融文本情绪包含了对资产价格有价值的信息，同时也揭示了金融文本的领域特殊性。

### （二）国内研究

国内学者围绕中国市场开展了大量研究。游家兴和吴静（2012）从报道基调、曝光程度和关注水平三个维度构建媒体情绪指标，发现媒体情绪越极端，股价偏离基本面的程度越大，揭示了媒体情绪导致资产误定价的“沉默的螺旋”效应。段江娇等（2017）以上证 A 股公司的股吧帖子为研究对象，发现论坛情绪显著正向影响股票当日收益率，论坛发帖数则会影响收益波动。部慧等（2018）基于东方财富股吧评论构建投资者情绪指标，研究了其对股票收益、成交量和波动率的影响。石善冲等（2018）利用微信文本挖掘构建投资者情绪，同样发现其与股票市场表现存在显著关联。

上述研究证明了中文社交媒体文本对股票市场具有信息含量。但这些研究大多采用词典法或传统机器学习方法度量情绪，情感分类本身的准确性往往没有得到充分检验。情感分类质量的提升，是提高此类实证研究可靠性的基础。

## 三、金融情感分析方法的演进

### （一）情感词典方法

词典法通过统计文本中正面词与负面词的数量来计算情感得分，具有简单、透明、可解释的优点，Tetlock（2007）与 Loughran 和 McDonald（2011）均属此类。但词典法无法理解上下文、否定和反讽，对网络新词和股市黑话（如“割韭菜”“抄底”“跌停板见”）适应性差，在中文社交媒体文本中的表现尤其受限。

### （二）传统机器学习方法

传统机器学习方法将文本表示为词袋或 TF-IDF 特征向量，再使用朴素贝叶斯、逻辑回归、支持向量机等分类器进行训练。Malo 等（2014）发布了 Financial PhraseBank 数据集，由具有金融背景的标注者对约 4800 条金融新闻句子进行三分类标注，成为英文金融情感分析最常用的基准之一。传统机器学习方法训练速度快、所需数据少，至今仍是重要的基准模型，但其依赖人工特征工程，难以捕捉词序和深层语义。

### （三）预训练语言模型方法

Vaswani 等（2017）提出的 Transformer 架构以自注意力机制取代循环结构，能够高效建模长距离依赖。Devlin 等（2019）在此基础上提出 BERT，通过掩码语言模型在大规模语料上进行预训练，再在下游任务上微调，在多项自然语言理解任务上取得突破。Araci（2019）在金融语料上继续预训练 BERT，得到 FinBERT，在 Financial PhraseBank 上显著优于此前方法。中文方面，Cui 等（2021）提出基于全词掩码的中文预训练模型（如 RoBERTa-wwm-ext），更好地适应了中文以词为语义单位的特点。

预训练语言模型的“预训练 + 微调”范式大幅降低了对人工特征的依赖，成为 2019—2022 年金融情感分析的主流方法。但这类模型参数量通常在 1 亿至 3 亿之间，知识容量有限，且仍需要一定规模的标注数据才能取得良好效果。

## 四、大语言模型与参数高效微调

### （一）大语言模型的发展

Brown 等（2020）提出的 GPT-3 拥有 1750 亿参数，展示了“上下文学习”能力：无需更新参数，仅在提示中给出少量示例即可完成新任务。Kaplan 等（2020）发现语言模型的损失随参数量、数据量和计算量呈幂律下降，为模型规模扩展提供了理论依据。此后开源大模型迅速发展，Yang 等（2025）发布的 Qwen3 系列提供了从 0.6B 到 235B 参数的多种规模，在中文理解方面表现突出，为中文金融文本研究提供了良好的基础模型。

### （二）金融领域大模型

Wu 等（2023）利用金融与通用混合语料训练了 500 亿参数的 BloombergGPT，在金融任务上显著优于同规模通用模型，但训练成本高昂且未开源。Yang 等（2023）提出开源的 FinGPT 框架，主张以低成本微调开源模型的方式构建金融大模型。Lu 等（2023）构建了约 300GB 的中文金融语料库 BBT-FinCorpus 和中文金融评测基准 BBT-CFLEB，并训练了 BBT-FinT5 模型。

### （三）参数高效微调方法

全参数微调大模型需要巨大的显存和计算资源。Hu 等（2022）提出 LoRA（Low-Rank Adaptation），其核心假设是模型适配下游任务时权重的变化量具有低秩结构，因此将权重更新 ΔW 分解为两个低秩矩阵的乘积 BA，冻结原始权重，仅训练 A 和 B。LoRA 将可训练参数减少到原来的万分之一量级，且推理时不增加额外延迟。Dettmers 等（2023）提出 QLoRA，将冻结的原始权重量化为 4-bit NormalFloat 格式，并结合双重量化和分页优化器，使 650 亿参数的模型可以在单张 48GB 显卡上微调，且性能与 16-bit 全参数微调相当。Zheng 等（2024）开发的 LlamaFactory 框架集成了多种高效微调方法，进一步降低了大模型微调的工程门槛。

### （四）大模型在金融情感分析中的应用

Zhang 等（2023a）提出 Instruct-FinGPT，将金融情感分类数据改写为指令格式微调 LLaMA-7B，在 Twitter 金融新闻数据集上的准确率达到 0.88，明显优于 FinBERT 和 ChatGPT，并在需要数值理解和上下文理解的样本上优势更为突出。Zhang 等（2023b）进一步引入检索增强生成（RAG）模块，为模型补充外部背景信息。Wang 等（2023）构建了金融数据集上的指令微调基准，比较了 LLaMA2、Falcon、BLOOM、MPT、ChatGLM2、Qwen 等多个 7B 规模开源模型的表现。Fatemi 和 Hu（2023）比较了微调小规模模型与大模型少样本学习的效果，发现经过微调的较小模型可以达到甚至超过大模型少样本学习的水平。

与本课题最为接近的是以下两项 2025 年的研究。Paredes Amorin 等（2025）比较了 FinBERT 与 DeepSeek-LLM 7B、Llama3 8B、Qwen3 8B 三个轻量级大模型在五个金融情感数据集上的表现，并以 5%～100% 的训练数据比例进行微调，发现大模型仅用 5% 的训练数据即可超过 FinBERT，Qwen3 8B 在低数据比例下表现尤为稳健。但该研究使用的中文数据集只包含积极和消极两类，各模型 F1 值均高达 0.97，区分度有限；且研究以单次实验的指标比较为主，没有进行显著性检验。Cheng（2025）使用 LoRA 和 QLoRA 微调 Llama-3.1-8B 和 Qwen3-8B，在 Financial PhraseBank 和 FiQA 数据集上均优于 FinBERT，并发现 QLoRA 在大幅降低显存的同时保持了相近的准确率，但该研究仅使用英文数据。

综合来看，“经参数高效微调的大模型优于 BERT 类模型”“大模型在少量标注数据下即可取得较好效果”两个结论已经在英文数据上得到了初步验证。

## 五、中文金融情感分析

与英文相比，中文金融情感分析面临更多挑战。Paredes Amorin 等（2025）指出，中文属于分析语，没有词干和词形变化，语法关系依靠语序和虚词表达，依赖显式规则的传统方法难以处理；大模型则可以通过在海量语料上预训练学习上下文表示，无需人工规则。此外，中文金融社交媒体文本口语化程度高，充斥着谐音、缩写、反讽和股市黑话，情感表达更加隐晦。

在数据资源方面，Lu 等（2023）构建的 BBT-CFLEB 基准中的 FinFE 数据集是目前较有代表性的中文金融社交媒体情感分类数据集，包含训练集 8000 条、验证集 1000 条、测试集 1000 条，标签分为消极、中性、积极三类。原论文报告 GPT2、T5、FinBERT 等模型在其上的准确率约为 79%～80%，说明该任务具有相当难度，尤其是“中性”类样本与弱正面、弱负面样本的边界较为模糊。Lan 等（2023）构建了中文细粒度金融情感分析数据集，并评测了多个大模型的表现。

总体而言，针对中文金融社交媒体三分类任务、系统比较传统方法、BERT 类模型与最新大模型微调效果的研究仍然较少。

## 六、模型比较的统计方法与可靠性评价

### （一）分类模型比较的统计检验

机器学习研究中，模型比较常仅报告准确率或 F1 值的高低，而忽视了测试集抽样和训练随机性带来的不确定性。Dietterich（1998）系统比较了多种分类算法比较检验方法的第一类错误率，推荐在只能进行单次训练时使用 McNemar 检验（McNemar, 1947）。该检验针对两个模型在同一测试集上的配对预测结果，仅利用“一个模型对、另一个模型错”的不一致样本构造统计量，适用于比较大模型这类训练成本较高的模型。Efron 和 Tibshirani（1993）提出的 Bootstrap 方法通过对测试集有放回重抽样，可以为 F1 值等复杂指标构造置信区间。当同时比较多个模型时，需要控制多重比较带来的第一类错误膨胀，Holm（1979）提出的逐步校正方法比 Bonferroni 校正更有检验功效。此外，方差分析可以用于检验“模型类型”和“训练样本量”两个因素及其交互效应，是分析样本效率的合适工具。

### （二）置信度校准

在金融风控等实际应用中，模型不仅要“判断对”，还要能够给出可靠的置信度。Guo 等（2017）发现，与早期神经网络相比，现代深度神经网络的准确率更高，但普遍存在过度自信问题，即预测概率系统性高于实际正确率。他们提出用期望校准误差（ECE）度量校准程度，并发现“温度缩放”这一简单的后处理方法即可有效改善校准。Balabanov 和 Linander（2024）发现，经 LoRA 微调的大模型在训练后期同样会对错误预测变得越来越自信，校准误差随训练轮次增加而上升。

### （三）选择性预测

选择性预测是指模型仅对把握较大的样本给出预测，对其余样本“拒绝判断”并交由人工处理。Chow（1970）最早从理论上分析了分类中错误率与拒识率之间的最优权衡。Geifman 和 El-Yaniv（2017）将其发展为深度神经网络的选择性分类方法：给定期望的错误率，通过置信度阈值控制预测的覆盖率，并以风险-覆盖率曲线评估模型。选择性预测天然适合“机器初筛 + 人工复核”的金融文本处理流程，但目前在金融情感分析中的研究还很少。

## 七、研究述评与展望

综上所述，现有研究取得了以下进展：第一，大量实证研究证明了中外金融文本情绪对资产价格具有信息含量；第二，金融情感分析方法经历了从词典法、传统机器学习到预训练语言模型再到大语言模型的演进，LoRA/QLoRA 使大模型微调在普通硬件上成为可能；第三，已有研究在英文数据上初步验证了大模型相对于 BERT 类模型的优势及其在少量数据下的良好表现。

但现有研究仍存在以下不足：

1. **研究场景方面**，已有大模型研究以英文数据为主，少数涉及中文的研究使用的是二分类数据，缺少对包含“中性”类、口语化程度高的中文金融社交媒体三分类任务的系统评估。
2. **研究方法方面**，多数研究只进行单次实验并比较指标高低，缺少重复实验、显著性检验和多重比较校正；对“训练样本量如何影响大模型优势”这一问题，也停留在描述性观察，缺少统计推断。
3. **评价维度方面**，已有研究几乎只关注准确率和 F1 值，很少考察大模型预测置信度的可靠性，选择性预测在金融情感分析中的应用尚属空白。

针对上述不足，本课题拟以 FinFE 中文金融社交媒体情感三分类数据集为对象，比较传统机器学习、中文 BERT、Qwen3 零样本和少样本提示以及 Qwen3 QLoRA 微调的表现，并从统计学视角开展以下研究：一是通过多次重复实验、McNemar 检验、Bootstrap 置信区间和 Holm 校正，检验大模型优势的显著性；二是通过样本量实验和双因素方差分析，刻画大模型在不同数据规模下的优势边界；三是通过置信度校准和选择性预测分析，评估大模型预测的可靠性。研究结论有望为金融机构在不同数据条件下选择情感分析模型提供依据。

## 参考文献

[1] 沈艳, 陈赟, 黄卓. 文本大数据分析在经济学和金融学中的应用：一个文献综述[J]. 经济学(季刊), 2019, 18(4): 1153-1186.

[2] 游家兴, 吴静. 沉默的螺旋：媒体情绪与资产误定价[J]. 经济研究, 2012, 47(7): 141-152.

[3] 段江娇, 刘红忠, 曾剑平. 中国股票网络论坛的信息含量分析[J]. 金融研究, 2017(10): 178-192.

[4] 部慧, 解峥, 李佳鸿, 吴俊杰. 基于股评的投资者情绪对股票市场的影响[J]. 管理科学学报, 2018, 21(4): 86-101.

[5] 石善冲, 朱颖楠, 赵志刚, 康凯立, 熊熊. 基于微信文本挖掘的投资者情绪与股票市场表现[J]. 系统工程理论与实践, 2018, 38(6): 1404-1412.

[6] Tetlock P C. Giving content to investor sentiment: The role of media in the stock market[J]. The Journal of Finance, 2007, 62(3): 1139-1168.

[7] Loughran T, McDonald B. When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks[J]. The Journal of Finance, 2011, 66(1): 35-65.

[8] Malo P, Sinha A, Korhonen P, et al. Good debt or bad debt: Detecting semantic orientations in economic texts[J]. Journal of the Association for Information Science and Technology, 2014, 65(4): 782-796.

[9] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in Neural Information Processing Systems. 2017: 5998-6008.

[10] Devlin J, Chang M W, Lee K, et al. BERT: Pre-training of deep bidirectional transformers for language understanding[C]//Proceedings of NAACL-HLT. 2019: 4171-4186.

[11] Araci D. FinBERT: Financial sentiment analysis with pre-trained language models[J]. arXiv preprint arXiv:1908.10063, 2019.

[12] Cui Y, Che W, Liu T, et al. Pre-training with whole word masking for Chinese BERT[J]. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 2021, 29: 3504-3514.

[13] Brown T, Mann B, Ryder N, et al. Language models are few-shot learners[C]//Advances in Neural Information Processing Systems. 2020: 1877-1901.

[14] Kaplan J, McCandlish S, Henighan T, et al. Scaling laws for neural language models[J]. arXiv preprint arXiv:2001.08361, 2020.

[15] Yang A, Li A, Yang B, et al. Qwen3 technical report[J]. arXiv preprint arXiv:2505.09388, 2025.

[16] Wu S, Irsoy O, Lu S, et al. BloombergGPT: A large language model for finance[J]. arXiv preprint arXiv:2303.17564, 2023.

[17] Yang H, Liu X Y, Wang C D. FinGPT: Open-source financial large language models[J]. arXiv preprint arXiv:2306.06031, 2023.

[18] Lu D, Wu H, Liang J, et al. BBT-Fin: Comprehensive construction of Chinese financial domain pre-trained language model, corpus and benchmark[J]. arXiv preprint arXiv:2302.09432, 2023.

[19] Hu E J, Shen Y, Wallis P, et al. LoRA: Low-rank adaptation of large language models[C]//International Conference on Learning Representations. 2022.

[20] Dettmers T, Pagnoni A, Holtzman A, et al. QLoRA: Efficient finetuning of quantized LLMs[C]//Advances in Neural Information Processing Systems. 2023.

[21] Zheng Y, Zhang R, Zhang J, et al. LlamaFactory: Unified efficient fine-tuning of 100+ language models[C]//Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations). Bangkok: ACL, 2024: 400-410.

[22] Zhang B, Yang H, Liu X Y. Instruct-FinGPT: Financial sentiment analysis by instruction tuning of general-purpose large language models[J]. arXiv preprint arXiv:2306.12659, 2023.

[23] Zhang B, Yang H, Zhou T, et al. Enhancing financial sentiment analysis via retrieval augmented large language models[J]. arXiv preprint arXiv:2310.04027, 2023.

[24] Wang N, Yang H, Wang C D. FinGPT: Instruction tuning benchmark for open-source large language models in financial datasets[J]. arXiv preprint arXiv:2310.04793, 2023.

[25] Fatemi S, Hu Y. A comparative analysis of fine-tuned LLMs and few-shot learning of LLMs for financial sentiment analysis[J]. arXiv preprint arXiv:2312.08725, 2023.

[26] Paredes Amorin A, Python A, Weisser C. Fine-tuning of lightweight large language models for sentiment classification on heterogeneous financial textual data[J]. arXiv preprint arXiv:2512.00946, 2025.

[27] Cheng X. Financial sentiment analysis with large language models[J]. Finance & Economics, 2025, 3(6). DOI: 10.61173/gvntfv56.

[28] Lan Y, Wu Y, Xu W, et al. Chinese fine-grained financial sentiment analysis with large language models[J]. arXiv preprint arXiv:2306.14096, 2023.

[29] McNemar Q. Note on the sampling error of the difference between correlated proportions or percentages[J]. Psychometrika, 1947, 12(2): 153-157.

[30] Dietterich T G. Approximate statistical tests for comparing supervised classification learning algorithms[J]. Neural Computation, 1998, 10(7): 1895-1923.

[31] Efron B, Tibshirani R J. An introduction to the bootstrap[M]. New York: Chapman & Hall, 1993.

[32] Holm S. A simple sequentially rejective multiple test procedure[J]. Scandinavian Journal of Statistics, 1979, 6(2): 65-70.

[33] Guo C, Pleiss G, Sun Y, et al. On calibration of modern neural networks[C]//International Conference on Machine Learning. 2017: 1321-1330.

[34] Balabanov O, Linander H. Uncertainty quantification in fine-tuned LLMs using LoRA ensembles[J]. arXiv preprint arXiv:2402.12264, 2024.

[35] Chow C K. On optimum recognition error and reject tradeoff[J]. IEEE Transactions on Information Theory, 1970, 16(1): 41-46.

[36] Geifman Y, El-Yaniv R. Selective classification for deep neural networks[C]//Advances in Neural Information Processing Systems. 2017.
