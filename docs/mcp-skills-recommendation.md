# MCP 接入与论文 Skill 推荐

## 状态与范围

- 已通过 HTTP MCP 完成 initialize、tools/list，并实测目录列举与批量读取；服务为 shuncode-bridge 0.7.6，共 15 个工具。不是 Arena 原生插件安装。
- 已读 README.md、docs/mcp-thesis-abstract.md、docs/mcp-innovation-points.md、docs/mcp-experiment-setup.md，以及 ARS README 和五个 SKILL.md 的能力与模式说明。
- 项目为《基于LoRA微调的大语言模型中文金融情感分类研究》。按 README.md，实验及初稿已完成，当前应优先审查、修订和学校格式适配。本次未审核全部正文、代码或原始结果，文档中的实验数字尚未独立核验。

## 推荐：三个 Skill 按需用，不启动全套流水线

| 优先级 | Skill / 模式 | 本项目用途 |
| --- | --- | --- |
| 1 | academic-paper-reviewer / methodology-focus | 审查数据清洗与测试集选择偏差、多种子统计推断、校准和保形预测的假设、噪声上限推导；依据本科论文要求，不套顶刊门槛 |
| 2 | academic-paper / citation-check、revision | 核对文献真实性与论断支持关系；按导师意见局部修订，避免重写全文 |
| 3 | deep-research / fact-check、three-way-scan、lit-review | 有具体证据缺口时补查金融情感分类、校准及数据泄漏文献，不重做选题 |

academic-paper 的 revision-coach 可在收到导师意见后借用；format-convert 可辅助输出，但仓库列出的五种引文格式不含 GB/T 7714，不能视为学校模板的一键适配。保留 scripts/build_draft.py 与 scripts/md2docx.py 的现有链路，先核验再调整。

暂不推荐 academic-pipeline（当前任务不需要全流程编排）和 sr-screener（当前不是系统综述筛选项目）。ARS 不是实验执行或复现验证工具，不能替代对 src/、outputs/、logs/ 的核验。

## 初步关注点（待核验，不是已确认错误）

- README.md 中的模型规模研究问题与摘要中的多模型比较重点不同，需要核对是否有过期描述。
- 摘要的“保证 90% 覆盖率”须核对保形预测所需假设及实际评估条件。
- 摘要中的“91% 准确率上限”应保留 docs/mcp-innovation-points.md 已写明的简化模型及非随机重复样本限制。

## 后续操作规则

- 默认只在当前论文工作区操作；不因工具权限宽就遍历整台电脑。
- 先读后改，优先小补丁与版本校验；修改后做相关检查。查文件用 find_files，查文本用 search_files，查代码符号用 lsp。
- 多步骤任务维护 set_todos，结束时显式完成或标记阻塞；独立读取可并行，同文件修改串行。
- 不擅自安装 skill、启动训练、删除或覆盖实验结果、上传材料或推送远端。论文事实以证据为准，缺证据明确标记。
- 汇报只保留结论、关键问题和下一步。本次仅新增本记录，未修改论文、数据或代码。
- ARS 是面向 Claude Code 的工作流文档与脚本集合；当前可借鉴其规则，不宣称已经安装或运行多代理审稿。

## 外部依据

仓库：https://github.com/Imbad0202/academic-research-skills ，查阅版本 README 标注 v3.23.0。
对应文件：academic-paper-reviewer/SKILL.md、academic-paper/SKILL.md、deep-research/SKILL.md、academic-pipeline/SKILL.md、sr-screener/SKILL.md。
