# 远程仓库迁移记录

日期：2026-10-13

## 目标仓库

- 新仓库：`https://github.com/Celyn-number3/undergrad-thesis-crw`
- 可见性：私有。
- 主分支：`main`。
- 迁移方式：保留原 Git 历史，提交并推送当前论文、代码、分析结果和项目参考资源的更新。
- 原历史基点：`aeb141254f1c81c13374955e89613dd1f8ca353e`，迁移前共有 32 次提交；不改写历史提交及其作者。

## 上传范围与排除规则

上传源码、脚本、依赖说明、分章与合并论文、Word/PDF、现有预测和轻量分析产物，以及按需使用的 Skills 说明和资源。

不上传本机运行环境 `runtime/`、Agent 本机配置 `.claude/`、模型权重 `models/`、原始和处理数据 `data/raw/`、`data/processed/`、检查点 `outputs/checkpoints/`、日志 `logs/`、凭据文件及 LaTeX 临时编译缓存。忽略规则见 `.gitignore`。

上传前对候选文件、ZIP/DOCX 文本成员及历史文本变更进行了常见凭据模式筛查，并检查文件大小。未发现匹配或超过 50 MiB 的文件；这不是穷尽式安全审计，也不代替材料使用授权核查。机器记录保留在不上传的 `logs/` 下。

本次是版本控制同步，不运行训练、推理、统计重算或文档重新生成，不以推送成功替代实验或排版验证。

## About 与 topics

About：

> 基于 LoRA/QLoRA 的中文金融情感分类本科论文研究：在 FinFE 上比较传统机器学习、BERT/RoBERTa 与 Qwen/GLM，涵盖统计检验、概率校准和保形预测。

Topics：

`chinese-nlp`、`financial-sentiment-analysis`、`sentiment-analysis`、`finfe`、`lora`、`qlora`、`large-language-models`、`qwen`、`glm`、`bert`、`statistical-analysis`、`model-calibration`、`conformal-prediction`、`pytorch`、`undergraduate-thesis`。

## 后续 Git 使用

- `origin` 指向新仓库；旧地址保留为 `legacy-origin`，不自动推送旧仓库。
- 新仓库认证使用本机 Git Credential Manager 中的 `Celyn-number3`；不把 token 写入代码、远程 URL 或文档，不改动其他项目的全局凭据配置。
- 新提交使用新账号的 GitHub noreply 身份；历史作者保持原样。
- 后续先查看 `git status`，仅添加本次确需提交且已检查的文件，再使用 `git push origin main`。
- 不使用强制推送、历史重写或工作区清理来完成迁移。
