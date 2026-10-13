# Skills 使用指南

本目录是从本地 Modex 重建目录复制的 **技能说明与资源集合**，用于辅助文献调研、实验分析、论文写作、图表制作和质量检查。

> **复制完成不等于安装或启用完成。** `SKILL.md` 主要是给 AI 助手阅读的流程说明，不是一个可以直接执行的程序。这里介绍的是技能的设计用途，不代表对应工具、外部服务或端到端流程均已验证通过。

清单核对日期：**2026-10-12**。当前包含 **70 个主技能**，另有 **33 份 Codex 适配版本**和 **8 份 Claude-review 覆盖版本**，共 111 份 `SKILL.md`。适配版本存在同名技能，不能视为 111 种独立能力。

## 0. 给 Agent 的项目操作约定

**本项目是论文研究，不是桌面应用。采用「现有 skill 提供思路 + Agent 按任务判断 + 现有脚本完成确定性计算」的轻量方式。** 不迁入 Modex 的 tools/backend，不新建工具框架、服务、数据库或强制流水线。下面是工作指南，不要求每次任务都执行全部步骤。

### 先定位材料，不先造工具

以下路径均相对**论文项目根目录**，不是相对当前 `skills/` 目录。

| 要找什么 | 位置与使用方式 |
| --- | --- |
| 当前进度、执行范围 | [根 README](../README.md)；历史计划不等于已完成实验 |
| 已有方法修订与限制 | [第一轮修订记录](../docs/mcp-methodology-revision-round1.md)，避免改回已经纠正的论断 |
| 论文源稿 | `docs/mcp-thesis-abstract.md`、`mcp-thesis-ch1.md`、`mcp-thesis-ch2.md`、`mcp-thesis-ch3-ch4.md`、`mcp-thesis-ch5.md`；后四项同在 `docs/` 下 |
| 合并稿与 Word | `docs/mcp-thesis-draft.md`、`docs/thesis-draft.docx`；修改正文时通常先改对应源稿，再同步生成，避免下次合并覆盖手改内容 |
| 实验依据 | `outputs/analysis/`；必要时追溯 `outputs/predictions/`、`outputs/metrics/` 和 `src/analysis/`，核对样本、种子与统计口径 |
| 既有生成/筛查脚本 | [build_draft.py](../scripts/build_draft.py)、[md2docx.py](../scripts/md2docx.py)、[check_numbers.py](../scripts/check_numbers.py)；先读代码，再确定参数、环境及写入位置 |
| Skill 与参考规则 | 从本页索引按需选择；写作、图表规则已在 `shared-scripts/` 内，不再复制一套 |
| Python/Pandoc 等程序 | 项目根 `runtime/`；使用前确认实际可执行路径、依赖与版本，不覆盖全局 PATH 或原实验环境 |

### 按任务组合，不机械照搬流程

- **只读审查**：参考 `quality-check` / `result-to-claim`，读目标稿与相关结果，报告问题、证据位置和建议；不为了审查重跑实验或重新生成全文。
- **用户已要求改稿**：在其授权范围内小改源章节，同步受影响的摘要、结论和表图说明；不扩成从头重写论文。
- **字数、标题、图片路径等一次性检查**：Agent 可使用已有工具、短命令或内存处理。先说明统计口径，不为一次需求新增永久工具模块。
- **Word 生成**：沿用现有合并和导出脚本，从仓库根运行以正确解析图片；知道它们会写文件，试验先用新输出名，正式稿覆盖须在本次授权范围内。不要仅为套用原应用的 profile 而重写生成器。
- **学校模板或格式要求**：先读取用户模板并参考 `format-profile` / `docx-template-map`；可以直接分析文档结构和样式。原工具缺失时说明限制，不默认补齐一整套模板引擎。
- **重算结果**：优先调用已有分析代码，并明确哪些输出会更新。分析模块可能在 import 时写文件，不能把导入当作只读检查。新统计方法确需可复现实现时，再按实际需求做最小修改。
- **文献/外部评审**：优先使用本次会话实际可用的检索能力；没有接通的 MCP 或外部模型就不假称已调用，也不执行原应用中带凭据或不安全联网设置的脚本。

### 碰到缺失能力时

先确认任务是否真的需要该能力：能用现有脚本、人工判断或一次性小命令完成，就不迁移新模块；做不到则说明差距和最小方案。只有反复出现、影响复现或明显值得复用的需求，才提出保留独立代码。**少写框架不等于取消真实计算和验证，实验数值仍须可追溯、可复算。**

### 执行与验收边界

- 服从用户本次任务的范围；普通已授权读写不反复请示。新增训练/推理、安装依赖、敏感材料外发、破坏性操作和 Git 推送等超出范围的动作，先说明并取得明确授权。
- 不搬入旧数据库、访问凭据、清理清单或自动恢复任务；不启用无人审批的修改循环。原 skills 中的“自动批准”不代表用户批准。
- 检查结论和执行事实分开：脚本退出成功不等于方法正确；数字初筛不等于逐表核验；文件存在不等于 Word 排版合格。
- 按任务检查实际产物：数值与来源对应、引用可追溯、图片路径有效、生成文档能打开；未做的视觉检查或独立评审如实标注。
- 汇报保持简短：改了什么、验证了什么、还有什么限制。临时脚本/日志按需放 `logs/`，不把一次性任务扩成新框架。

该方式替代了此前 tools/后端迁移方案的实施建议；原方案仅作为风险与历史备选记录，不是待自动执行的任务清单。已复制的 runtime 保留备用，不自动启动或加入 Git 提交。

## 1. 目录结构

```text
skills/
├── README.md                              # 本说明
└── skills-decrypt-docs/
    ├── decrypt_all_skills.py               # 来源附带脚本，使用现有明文技能不需要执行
    ├── decryption-guide.md                # 来源附带记录
    └── skills_decrypted_all/               # 主技能与资源根目录
        ├── <技能目录>/SKILL.md             # 70 个一级技能目录
        ├── shared-scripts/                # 绘图、统计表格、检查脚本及规则
        ├── shared-references/             # 共享参考资料
        ├── decryption-docs/               # 来源附带目录，不是技能入口
        ├── skills-codex/                  # 33 份 Codex 适配版本
        └── skills-codex-claude-review/     # 8 份外部评审覆盖版本
```

主技能目录：[`skills-decrypt-docs/skills_decrypted_all/`](skills-decrypt-docs/skills_decrypted_all/)。

## 2. 当前论文优先使用哪些

| 当前需求 | 建议选用 | 本项目中的使用方式 |
| --- | --- | --- |
| 检查结构、引用与图表 | `quality-check` | 先只读检查，明确目标为 `docs/mcp-thesis-draft.md` |
| 避免实验结论夸大 | `result-to-claim`、`research-review` | 对照已有结果和方法限制；未调用外部模型时如实标注为本助手审查 |
| 检查转 Word 前的格式 | `docx-format-check` | 借鉴检查规则，保留现有 Word 生成脚本 |
| 整理已有实验结果 | `analyze-results`、`paper-figure` | 读取 `outputs/analysis/` 等真实结果，不凭空补数据 |
| 调整中文论文组织 | `paper-plan-zh`、`paper-write-zh-docx` | 仅借鉴大纲和写作规范，不自动覆盖现有章节 |
| 后续对齐学校 Word 模板 | `format-profile`、`docx-template-map` | 先读模板，按需分析并用测试副本核验；不默认补齐工具链 |

当前论文已有稳定的分析和导出链路，**不要为了使用这些技能而迁移全部文件、重跑训练或替换现有生成器**。

## 3. 主技能分类索引（70 个）

点击技能名可阅读对应 `SKILL.md`。下表概述其用途；实际输入、输出、权限和依赖应在使用前逐项确认。

### 3.1 文献、选题与研究规划

| 技能 | 用途与适用场景 |
| --- | --- |
| [assets-inventory](skills-decrypt-docs/skills_decrypted_all/assets-inventory/SKILL.md) | 盘点已有题目、源码、数据、图表和结果，识别材料之间的冲突。 |
| [arxiv](skills-decrypt-docs/skills_decrypted_all/arxiv/SKILL.md) | 按主题或论文编号检索、下载和整理 arXiv 论文；依赖网络及检索工具。 |
| [research-lit](skills-decrypt-docs/skills_decrypted_all/research-lit/SKILL.md) | 检索和阅读研究文献，整理相关工作与关键方法。 |
| [comm-lit-review](skills-decrypt-docs/skills_decrypted_all/comm-lit-review/SKILL.md) | 通信领域专用综述流程，覆盖无线、卫星、网络与传输协议等方向。 |
| [literature-review](skills-decrypt-docs/skills_decrypted_all/literature-review/SKILL.md) | 按主题组织文献、核实来源并撰写综合性文献综述。 |
| [idea-creator](skills-decrypt-docs/skills_decrypted_all/idea-creator/SKILL.md) | 从宽泛方向生成研究想法，并比较价值与可行性。 |
| [novelty-check](skills-decrypt-docs/skills_decrypted_all/novelty-check/SKILL.md) | 对照已有和近期文献查新，识别与现有工作的实质差异。 |
| [research-refine](skills-decrypt-docs/skills_decrypted_all/research-refine/SKILL.md) | 把模糊想法收敛为问题、方法和最小验证方案。 |
| [thesis-proposal](skills-decrypt-docs/skills_decrypted_all/thesis-proposal/SKILL.md) | 撰写学位论文开题报告，涵盖背景、研究内容、技术路线和进度。 |
| [grant-proposal](skills-decrypt-docs/skills_decrypted_all/grant-proposal/SKILL.md) | 根据研究想法、文献和项目要求组织基金申请书。 |

### 3.2 实验、统计与证据解释

| 技能 | 用途与适用场景 |
| --- | --- |
| [experiment-plan](skills-decrypt-docs/skills_decrypted_all/experiment-plan/SKILL.md) | 制定由研究结论驱动的实验路线、评价协议、消融矩阵和预算。 |
| [experiment-bridge](skills-decrypt-docs/skills_decrypted_all/experiment-bridge/SKILL.md) | 把实验计划落成代码、真实运行结果和图表；涉及实际执行。 |
| [run-experiment](skills-decrypt-docs/skills_decrypted_all/run-experiment/SKILL.md) | 部署并运行本地或远程实验，可能使用 GPU、SSH 和训练环境。 |
| [monitor-experiment](skills-decrypt-docs/skills_decrypted_all/monitor-experiment/SKILL.md) | 查看已经运行的实验进度、日志和结果。 |
| [training-check](skills-decrypt-docs/skills_decrypted_all/training-check/SKILL.md) | 检查训练健康状况，如 NaN、损失发散、GPU 空闲；原流程涉及 W&B 等依赖。 |
| [analyze-results](skills-decrypt-docs/skills_decrypted_all/analyze-results/SKILL.md) | 整理实验结果，进行统计分析、模型比较并输出解释。 |
| [result-to-claim](skills-decrypt-docs/skills_decrypted_all/result-to-claim/SKILL.md) | 核对结果支持哪些结论、不能支持哪些结论，以及还缺什么证据。 |
| [ablation-planner](skills-decrypt-docs/skills_decrypted_all/ablation-planner/SKILL.md) | 围绕方法组件和审稿疑问设计消融实验。 |
| [paper-analysis](skills-decrypt-docs/skills_decrypted_all/paper-analysis/SKILL.md) | 依据论文大纲规划数据处理、分析与建模；原模板允许模拟数据，本项目不可用模拟结果替代真实实验。 |
| [dse-loop](skills-decrypt-docs/skills_decrypted_all/dse-loop/SKILL.md) | 面向计算机体系结构和 EDA 的设计空间搜索与迭代调参。 |
| [proof-writer](skills-decrypt-docs/skills_decrypted_all/proof-writer/SKILL.md) | 整理定理、引理和数学证明，检查假设及推导缺口。 |

### 3.3 论文大纲与正文写作

| 技能 | 用途与适用场景 |
| --- | --- |
| [paper-plan](skills-decrypt-docs/skills_decrypted_all/paper-plan/SKILL.md) | 根据实验结果和审查结论规划论文结构。 |
| [paper-plan-zh](skills-decrypt-docs/skills_decrypted_all/paper-plan-zh/SKILL.md) | 规划中文论文的大纲、章节与论证结构。 |
| [paper-write](skills-decrypt-docs/skills_decrypted_all/paper-write/SKILL.md) | 按大纲撰写英文 LaTeX 论文。 |
| [paper-write-zh](skills-decrypt-docs/skills_decrypted_all/paper-write-zh/SKILL.md) | 撰写使用 ctex/XeLaTeX 的中文 LaTeX 论文。 |
| [paper-write-nature](skills-decrypt-docs/skills_decrypted_all/paper-write-nature/SKILL.md) | 按 Nature 风格组织英文 LaTeX 稿件；不保证满足具体期刊全部要求。 |
| [paper-write-docx](skills-decrypt-docs/skills_decrypted_all/paper-write-docx/SKILL.md) | 撰写面向 Word 导出的英文 Markdown 正文。 |
| [paper-write-zh-docx](skills-decrypt-docs/skills_decrypted_all/paper-write-zh-docx/SKILL.md) | 撰写面向 Word 导出的中文 Markdown 正文。 |
| [paper-write-nature-docx](skills-decrypt-docs/skills_decrypted_all/paper-write-nature-docx/SKILL.md) | 撰写面向 Word 导出的 Nature 风格 Markdown 正文。 |

### 3.4 审查、改稿与 Word 格式

| 技能 | 用途与适用场景 |
| --- | --- |
| [quality-check](skills-decrypt-docs/skills_decrypted_all/quality-check/SKILL.md) | 检查字数、章节结构、参考文献、图表、格式和语言风格。 |
| [docx-format-check](skills-decrypt-docs/skills_decrypted_all/docx-format-check/SKILL.md) | 检查转 Word 前的 Markdown 表格、图片、公式、代码块等格式问题。 |
| [docx-template-map](skills-decrypt-docs/skills_decrypted_all/docx-template-map/SKILL.md) | 分析 Word 模板占位位置，规划映射、试填和检查；需补齐模板分析与填充工具。 |
| [format-profile](skills-decrypt-docs/skills_decrypted_all/format-profile/SKILL.md) | 将字体、字号、行距、页边距等要求整理成样式配置；需匹配实际导出引擎。 |
| [research-review](skills-decrypt-docs/skills_decrypted_all/research-review/SKILL.md) | 对研究问题、方法、证据和贡献进行批判性审查。 |
| [auto-review-loop](skills-decrypt-docs/skills_decrypted_all/auto-review-loop/SKILL.md) | 多轮研究审查、修改与复核的编排流程。 |
| [auto-review-loop-llm](skills-decrypt-docs/skills_decrypted_all/auto-review-loop-llm/SKILL.md) | 通过 OpenAI 兼容接口配置外部评审的循环流程。 |
| [auto-review-loop-minimax](skills-decrypt-docs/skills_decrypted_all/auto-review-loop-minimax/SKILL.md) | 面向 MiniMax 或配置的评审后端的循环流程。 |
| [auto-paper-improvement-loop](skills-decrypt-docs/skills_decrypted_all/auto-paper-improvement-loop/SKILL.md) | 针对写作和呈现进行评审、修改与重新编译的迭代流程。 |
| [rebuttal](skills-decrypt-docs/skills_decrypted_all/rebuttal/SKILL.md) | 逐条回应外部审稿意见，约束回复覆盖范围、事实依据和字数。 |

### 3.5 图表、插图与展示

| 技能 | 用途与适用场景 |
| --- | --- |
| [paper-figure](skills-decrypt-docs/skills_decrypted_all/paper-figure/SKILL.md) | 从真实实验结果制作论文图表和统计表。 |
| [nature-figure](skills-decrypt-docs/skills_decrypted_all/nature-figure/SKILL.md) | 参考 Nature 风格设置 matplotlib 图表的字体、配色和输出格式。 |
| [paper-figure-drawio](skills-decrypt-docs/skills_decrypted_all/paper-figure-drawio/SKILL.md) | 制作 draw.io 架构图、技术路线图及 TikZ 图；需对应绘图/编译工具。 |
| [mermaid-diagram](skills-decrypt-docs/skills_decrypted_all/mermaid-diagram/SKILL.md) | 将结构或流程转成 Mermaid 图，输出 .mmd/.md 文件。 |
| [paper-illustration](skills-decrypt-docs/skills_decrypted_all/paper-illustration/SKILL.md) | 使用图像生成服务制作方法示意图；需另行配置并授权外部服务。 |
| [paper-slides](skills-decrypt-docs/skills_decrypted_all/paper-slides/SKILL.md) | 规划论文汇报幻灯片、讲稿及 PDF/PPTX 输出链路。 |
| [paper-poster](skills-decrypt-docs/skills_decrypted_all/paper-poster/SKILL.md) | 规划学术海报及 PDF/PPTX/SVG 输出链路。 |
| [pixel-art](skills-decrypt-docs/skills_decrypted_all/pixel-art/SKILL.md) | 制作适合 README、文档或幻灯片的像素风 SVG 插图。 |

### 3.6 LaTeX 编译

| 技能 | 用途与适用场景 |
| --- | --- |
| [paper-compile](skills-decrypt-docs/skills_decrypted_all/paper-compile/SKILL.md) | 编译英文 LaTeX 论文为 PDF，原流程使用 pdflatex。 |
| [paper-compile-zh](skills-decrypt-docs/skills_decrypted_all/paper-compile-zh/SKILL.md) | 使用 XeLaTeX 编译中文论文为 PDF。 |

### 3.7 数学建模与统计建模竞赛

| 技能 | 用途与适用场景 |
| --- | --- |
| [comp-stats-topic](skills-decrypt-docs/skills_decrypted_all/comp-stats-topic/SKILL.md) | 依据统计建模赛事主题选择题目、规划方案和数据来源。 |
| [comp-prob-analysis](skills-decrypt-docs/skills_decrypted_all/comp-prob-analysis/SKILL.md) | 拆解赛题子问题、变量及建模思路。 |
| [comp-modeling](skills-decrypt-docs/skills_decrypted_all/comp-modeling/SKILL.md) | 建立数学模型、推导公式并设计求解算法。 |
| [comp-code](skills-decrypt-docs/skills_decrypted_all/comp-code/SKILL.md) | 把建模方案实现成代码，执行计算并保存真实结果。 |
| [comp-paper-zh](skills-decrypt-docs/skills_decrypted_all/comp-paper-zh/SKILL.md) | 组织中文竞赛论文，原流程输出 LaTeX。 |
| [comp-paper-en](skills-decrypt-docs/skills_decrypted_all/comp-paper-en/SKILL.md) | 组织 MCM/ICM 等英文竞赛论文，原流程输出 LaTeX。 |
| [comp-paper-zh-docx](skills-decrypt-docs/skills_decrypted_all/comp-paper-zh-docx/SKILL.md) | 组织面向 Word 导出的中文竞赛论文 Markdown 正文。 |
| [comp-paper-en-docx](skills-decrypt-docs/skills_decrypted_all/comp-paper-en-docx/SKILL.md) | 组织面向 Word 导出的英文竞赛论文 Markdown 正文。 |
| [comp-compile-zh](skills-decrypt-docs/skills_decrypted_all/comp-compile-zh/SKILL.md) | 编译中文竞赛论文，并检查页数、匿名和格式等要求。 |
| [comp-compile-en](skills-decrypt-docs/skills_decrypted_all/comp-compile-en/SKILL.md) | 编译英文竞赛论文，并进行赛事格式检查。 |

### 3.8 课程论文与课程报告

| 技能 | 用途与适用场景 |
| --- | --- |
| [course-plan](skills-decrypt-docs/skills_decrypted_all/course-plan/SKILL.md) | 规划课程论文的大纲、数据分析和图表。 |
| [course-paper](skills-decrypt-docs/skills_decrypted_all/course-paper/SKILL.md) | 根据大纲、数据结果和图表撰写课程论文正文。 |
| [course-report-plan](skills-decrypt-docs/skills_decrypted_all/course-report-plan/SKILL.md) | 阅读项目材料，提取项目事实并规划课程报告。 |
| [course-report](skills-decrypt-docs/skills_decrypted_all/course-report/SKILL.md) | 根据项目事实、大纲和结果撰写课程报告。 |

### 3.9 组合工作流与辅助能力

| 技能 | 用途与适用场景 |
| --- | --- |
| [idea-discovery](skills-decrypt-docs/skills_decrypted_all/idea-discovery/SKILL.md) | 串联文献调研、想法生成、查新和研究审查。 |
| [idea-discovery-robot](skills-decrypt-docs/skills_decrypted_all/idea-discovery-robot/SKILL.md) | 面向机器人/具身智能的选题流程，强调基准、仿真与实现条件。 |
| [research-refine-pipeline](skills-decrypt-docs/skills_decrypted_all/research-refine-pipeline/SKILL.md) | 串联研究方案细化与实验规划。 |
| [research-pipeline](skills-decrypt-docs/skills_decrypted_all/research-pipeline/SKILL.md) | 串联选题、实现和审查的综合科研流程；依赖各子步骤实际可用。 |
| [paper-writing](skills-decrypt-docs/skills_decrypted_all/paper-writing/SKILL.md) | 串联大纲、图表、正文、编译和改稿的完整写作流程。 |
| [editor-agent](skills-decrypt-docs/skills_decrypted_all/editor-agent/SKILL.md) | 通用论文编辑助手流程，可能读写文件和执行命令，必须限定授权范围。 |
| [feishu-notify](skills-decrypt-docs/skills_decrypted_all/feishu-notify/SKILL.md) | 向飞书/Lark 发送状态通知；需配置 webhook 或相关服务并确认发送内容。 |

## 4. 两套适配版本怎么选

| 目录 | 定位 | 注意事项 |
| --- | --- | --- |
| 主技能目录中的一级技能 | 基础流程文本，多数沿用 Claude Code/原应用工具约定 | 当前可按需阅读和人工适配，不代表 ShunCode 会自动注册它们 |
| [`skills-codex/`](skills-decrypt-docs/skills_decrypted_all/skills-codex/) | 面向 Codex 的 33 份适配版本 | 部分流程使用子代理或外部服务，仍取决于宿主是否提供相关能力 |
| [`skills-codex-claude-review/`](skills-decrypt-docs/skills_decrypted_all/skills-codex-claude-review/) | 在 Codex 基础版本之上切换评审后端的 8 份覆盖文件 | 不是完整独立技能包，需要另行准备 Claude-review MCP 服务和合法鉴权 |

原包说明：
- [Codex 适配说明](skills-decrypt-docs/skills_decrypted_all/skills-codex/README_CN.md)
- [Claude-review 覆盖层说明](skills-decrypt-docs/skills_decrypted_all/skills-codex-claude-review/README_CN.md)

**不要把三套目录无差别混装。** 同名文件会互相覆盖；已有 `.claude/skills/` 中的其他技能也不应被直接覆盖。原包 README 的数量、安装路径和外部桥接文件说明可能与本次拷贝不同，以实际文件和宿主能力为准。

## 5. 如何使用

### 推荐：让助手先阅读，再执行经确认的范围

可以直接提出以下请求，不需要先安装整个原应用：

```text
请先读取：
skills/skills-decrypt-docs/skills_decrypted_all/quality-check/SKILL.md

参考其中的检查清单，只读审查 docs/mcp-thesis-draft.md。
实验数值以 outputs/analysis/ 中现有结果为依据。
不要修改正文、安装依赖、重新训练或调用外部模型。
缺失的脚本请明确指出，不要把退出码为 0 当作完成检查。
输出问题、证据位置及修改建议。
```

使用顺序：
1. 选择与当前目标最相关的一个或少数几个技能，不默认启动“全流程”。
2. 明确输入路径、结果依据、输出位置，以及是否允许修改文件或执行命令。
3. 将原技能的 `$ARGUMENTS`、`user_data/`、`paper/main.md`、`_utils/` 等约定映射到实际项目。
4. 检查引用的脚本是否存在、是否真的实现，确认网络、模型、GPU 等条件。
5. 先在只读模式或测试副本上验证，再决定是否接入常用工作流。

`/quality-check` 等斜杠命令只在宿主实际安装并识别相应技能后才可能成立；**把文件放在本目录不会自动新增命令或 MCP 工具**。`allowed-tools` 也不能凭空提供工具或扩大用户授权。

## 6. 共享资源与 Runtime 的关系

- [`shared-scripts/`](skills-decrypt-docs/skills_decrypted_all/shared-scripts/)：含 `stats_utils.py`、`plot_utils.py`、`figure_check.py`、`drawio_check.py`、写作/绘图规则和编译辅助脚本。
- [`shared-references/`](skills-decrypt-docs/skills_decrypted_all/shared-references/)：共享参考资料。
- [`../runtime/`](../runtime/)：独立的运行环境资源，包括 Python、Pandoc、Node、Git/Bash、Claude CLI，以及绘图/排版相关文件。

2026-10-12 的检查中，内嵌 Python 的基础数据计算、python-docx 内存读写，以及 Pandoc 的中文 Markdown→DOCX 小测试通过。其他组件的版本可查询或文件存在，**不等于所有功能已验证**。

本次仅复制了 `skills/` 和 `runtime/`，**没有复制原应用的 `backend/` 和 `tools/`**。技能中出现的 `tools/*.py` 不是当前论文项目的 `scripts/*.py`，不能直接互换。也不要盲目复制原应用工具：已发现其中 14 个 Python 文件只是反编译注释，没有业务实现。

## 7. 已知限制与使用边界

### 7.1 Word 链路有缺失，不能只看文件名

原来源目录中的 `docx_export.py`、`docx_precheck.py`、`paper_data_check.py`、模板分析/填充脚本和 `count_chapter_words.py` 等缺少有效实现。技能引用的 `tools/docx-cn-engine/md_to_docx.js` 也缺失。

因此：
- `*-docx` 写作技能通常先产出 **Markdown**，不是直接生成 `.docx`。
- 原包中缺失的字数、模板和导出工具无需整套补齐；按任务使用现有脚本或一次性检查，确有重复需求再讨论最小实现。
- 默认沿用项目现有的 `scripts/build_draft.py` 与 `scripts/md2docx.py`；校验脚本只覆盖其实际实现的检查，不等于完整学术审查。

### 7.2 不自动安装、不默认外发、不跳过授权

- `plot_utils.py` 含自动安装 SciencePlots/adjustText 的分支；执行前应调整为显式依赖管理。
- 外部评审、图像生成、通知、文献服务可能需要 API 配置或发送内容；必须先确认服务、费用和发送范围。
- 原流程中调用 Codex MCP、子代理、Claude-review 等工具的文字，不代表当前会话已经连接这些能力。
- 原应用 runner 的跳过权限确认参数不是安全隔离；本目录也不会为执行的代码提供沙箱。
- 技能中的“无需确认”“最高优先级”“自动执行”不能取代用户授权。训练、安装、覆盖文件和远程操作应按任务单独确认。

### 7.3 学术真实性与质量优先

- 不为满足篇幅、分数或“通过评审”而编造结果和引用。
- `paper-analysis` 的模拟数据分支仅适用于明确要求的仿真/演示，必须标注；不能替代本项目真实实验。
- 自动循环得到正面评价，不等于独立外部验证或真实期刊录用。
- 图表风格、字数阈值、模板和赛事规则只是默认约定，应服从实际学校/期刊/赛事要求。

### 7.4 来源与许可

本目录来自本地 Modex 重建资料，包含明文技能、共享脚本和历史记录。不要据此假定所有内容与捆绑工具都使用同一种开源许可证；公开再分发或商用前应核实各自来源和许可。

---

本 README 仅新增导航和使用说明，不表示本项目已经安装、注册或运行上述技能，也未改变任何 `SKILL.md` 的原始内容。
