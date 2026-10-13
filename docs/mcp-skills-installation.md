# Academic Research Skills 项目级安装记录

## 安装结果

- 项目目录：`D:/项目管理/undergrad-thesis-crw`。
- 方式：上游文档的 project-skills-copy，三个 skill 目录原样复制；项目规则使用精简适配，不复制上游冗长的全套流水线规则。
- 版本：v3.23.0；固定提交 `d1e51716e53fc371727ea6164dd709fc8ea28c97`。
- 下载归档 SHA-256：`d34f6ecdf27d65a64167e51b83fef2a0ce6016193c1da303be55bd9016f4f07c`。

| 项目入口 | 文件数 | 建议模式 |
| --- | --- | --- |
| `.claude/skills/academic-paper-reviewer/SKILL.md` | 28 | methodology-focus |
| `.claude/skills/academic-paper/SKILL.md` | 63 | citation-check / revision |
| `.claude/skills/deep-research/SKILL.md` | 53 | fact-check / three-way-scan |

`.claude/vendor/academic-research-skills/` 保留固定版本的上游源码，共 2839 个普通文件，含 shared、scripts、其他 skill 的被引用资料和许可。归档内五个仅供插件发现用的 skills 符号链接已跳过；本安装不注册插件。academic-pipeline 和 sr-screener 仅在源码中保留，不作为项目 skill 入口安装。

## 配置与使用

- 项目规则：`.claude/CLAUDE.md`，已记录简体中文、精简汇报、本科论文尺度、先读后改和不擅自训练/上传/推送。
- 安装清单：`.claude/ars-install.json`。
- 在项目根目录开启新的 Claude Code 会话，使用自然语言指定，例如：
  - “用 academic-paper-reviewer 的 methodology-focus 审查第三、四章，只列关键问题，先不要改文件。”
  - “用 academic-paper 的 citation-check 核对参考文献，区分书目信息与论断支持关系。”
  - “用 deep-research 的 fact-check 核查 FinFE 数据重复问题的已有研究。”
- 本次没有注册 `/ars-*` 插件快捷命令、hooks、API 凭据或全局配置。尚未发起真实模型会话验证自动发现；ShunCode 是否自动发现此目录也未验证。当前 MCP 助手可以直接读取这些文件使用。
- 上游脚本路径须以 `.claude/vendor/academic-research-skills/` 为根解析，不要混用论文项目的 scripts 目录。

## 验证范围

- 下载归档 SHA-256 与安装前取得的归档校验值一致。
- 三个 skill 共 144 个文件与保留的固定版本源码逐文件 SHA-256 一致，SKILL.md 名称和关键依赖路径检查通过。
- check_acronyms.py、verify_passport.py、run_ledger.py 的 Python 语法解析通过；check_acronyms.py --help 返回成功。
- 当前 PATH Python 中 yaml、defusedxml 可用，jsonschema、pypdf 未安装。核心 prompt skill 不依赖这些库；需要相应可选脚本时再建项目隔离环境并补依赖，不能将本次安装视为全部 Python 功能已测试。
- 未运行审稿、检索或论文修改工作流；未调用外部模型，未上传论文材料。
- 安装后 git status 没有已跟踪文件修改；新增 .claude 目录，另有此前已有的 docs/mcp-skills-recommendation.md。本记录随后新增。没有 commit 或 push。

## 维护

本次固定版本，不自动更新。更新时先检查本地修改，再同步源码和三个入口并重新校验，不能只更新其中一份。完整移除时可移除本次新增的 .claude 内容；若后续加入其他工具配置，应只删除本安装清单对应的文件，不要直接删除整个目录。

Based on Academic Research Skills by Cheng-I Wu.
来源：https://github.com/Imbad0202/academic-research-skills
许可：CC BY-NC 4.0，许可原文保留于 `.claude/vendor/academic-research-skills/LICENSE`。
