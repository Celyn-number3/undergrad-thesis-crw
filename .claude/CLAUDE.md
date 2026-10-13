# 本科论文项目：Academic Research Skills

## 项目偏好

- 项目：基于 LoRA 微调的大语言模型中文金融情感分类研究；当前已有实验和论文初稿。
- 默认用简体中文，汇报遵循奥卡姆剃刀原则：结论、关键问题、下一步；不重复解释基础知识。
- 以本科论文要求和学校模板为准，不默认套用顶刊标准、APA 格式或从头重写全文。
- 只做用户当前要求的工作；先读后改、小范围修改、改后验证。不得编造文献、数据或实验结果。
- 未经用户明确授权，不启动训练、删除或覆盖实验结果、安装全局依赖、上传全文到第三方服务或推送远端。
- 跨模型验证需要本次任务明确同意；不得把环境开关或安装本身当成授权。

## 本项目轻量工作方式

- 任务开始时参考 [skills/README.md](../skills/README.md) 中“给 Agent 的项目操作约定”；按任务选技能、复用现有脚本，不引入 Modex 后端或新工具框架。
- 项目根 `skills/` 是另一组已复制的参考资料，不是新增插件安装入口，不覆盖下列已安装 skill。一次性检查按需处理；需要可复现实验实现时仍保留必要代码。

## 已安装的三个 skill

| 入口（相对项目根目录） | 优先模式 |
| --- | --- |
| `.claude/skills/academic-paper-reviewer/SKILL.md` | `methodology-focus`，需要时 `quick` / `re-review` |
| `.claude/skills/academic-paper/SKILL.md` | `citation-check` / `revision`，收到导师意见时 `revision-coach` |
| `.claude/skills/deep-research/SKILL.md` | `fact-check` / `three-way-scan` / `lit-review` |

用户明确指定 skill 或模式时直接进入相应模式；确有任务歧义才询问。执行前读取对应 SKILL.md 和该模式实际引用的 agent / reference 文件。没有用户要求，不启动全套 academic-pipeline，不开展 sr-screener 文献筛选。

## 上游文件与依赖路径

- 版本及校验记录：`.claude/ars-install.json`。
- 固定版本上游源码根：`.claude/vendor/academic-research-skills/`，其中保留 `shared/`、`scripts/`、跨 skill 引用及许可。仅 `.claude/skills/` 下三个目录作为项目 skill 安装入口。
- skill 自身的 `agents/`、`references/`、`templates/` 路径先相对该 skill 目录解析。
- 上游根相对路径（如 `shared/...`、`scripts/...`、`academic-pipeline/...`）必须相对上述源码根解析，不能误用论文项目的 `scripts/` 或 `docs/`。
- 执行上游辅助脚本前先检查代码、依赖及写入位置。需要以上游源码根为 cwd 时，论文输入和输出使用明确的绝对路径，输出留在本论文项目内。不要默认安装整份 requirements-dev.txt。
- 保留当前 `scripts/build_draft.py`、`scripts/md2docx.py` 文档生成链路，不因 skill 格式建议自动替换。

## 能力边界

本次采用 Claude Code 项目 skills-copy 方式，不是 marketplace 插件安装。未注册 `/ars-*` 插件命令、hooks 或全局配置；vendor 中的插件文件只作源码保留。其他宿主是否自动发现 `.claude/skills` 需单独确认；通过 MCP 的助手可直接读取这些文件使用，但不能宣称拥有宿主未提供的多代理能力。

查到文献条目不等于核实了论断；只能访问摘要时明确说明。角色模拟不等于独立专家审查，代码、实验真实性和复现另行核验。

Based on Academic Research Skills by Cheng-I Wu.
https://github.com/Imbad0202/academic-research-skills
上游许可：CC BY-NC 4.0；此文件为本项目精简适配，不是上游原始 CLAUDE.md。
