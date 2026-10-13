# 复现与资产说明

更新：2026-10-13。本文说明哪些内容在 Git 仓库中，哪些在 Release 或独立加密备份中，以及换电脑后如何恢复和核验。

## 1. 存放位置

| 内容 | 存放位置 | 说明 |
| --- | --- | --- |
| 代码、论文源稿、Word/PDF、预测与分析结果 | Git 仓库 | 私有仓库 |
| 实验环境锁定 | `requirements-lock.txt`、`environment.yml` | conda 环境 `thesis` |
| 工具环境锁定 | `requirements-runtime-lock.txt` 及第 3 节 | `runtime/python` 等 |
| 数据与模型校验值 | `configs/assets-sha256.txt` | 只有 SHA-256，没有文件内容 |
| 论文与实验快照 | Release `snapshot-20261013` | 见第 7 节 |
| FinFE 数据、完整日志、`.claude/`、Git 历史包 | 独立加密备份 | 见第 8 节 |
| 基座模型 | 从上游重新下载 | 见第 4 节，按校验值核对 |
| `runtime/` | 按第 3 节重建 | 不进入仓库、Release 或核心备份 |
| LoRA 微调权重 | 不存在 | 见第 6 节 |

## 2. 实验环境

记录对象为 conda 环境 `thesis`。2026-10-13 导出的关键版本与 `logs/setup_env*.log` 中的安装记录一致：

- Python 3.11.16；torch 2.7.1+cu128（CUDA 12.8，cuDNN 9.7.1）
- transformers 5.17.0、peft 0.21.0、accelerate 1.15.0、bitsandbytes 0.50.2
- scikit-learn 1.9.1、statsmodels 0.15.0、scipy 1.17.1、numpy 2.4.6、pandas 3.0.6、datasets 5.0.1、modelscope 1.40.1
- 硬件与系统：NVIDIA GeForce RTX 3090 24 GB，记录时驱动 596.49；Windows 10（10.0.19045）

重建方式（二选一）：

```bash
conda env create -f environment.yml

conda create -n thesis python=3.11.16
conda activate thesis
pip install -r requirements-lock.txt
```

`requirements.txt` 保留为宽松依赖说明；需要与论文实验一致时使用锁定文件。锁定版本能减少依赖差异，但不保证 GPU 计算逐位相同。

## 3. 本地工具环境

`runtime/` 约 7.5 GiB、99,365 个文件，按复制的离线工具使用，不自动启用。版本如下：

| 工具 | 版本 |
| --- | --- |
| Python（文档、图表和检查脚本） | 3.11.9，依赖见 `requirements-runtime-lock.txt` |
| Git | 2.52.0.windows.1 |
| Pandoc | 3.7.0.2 |
| MiKTeX / XeTeX | MiKTeX 25.12，XeTeX 4.16 |
| Node.js | 24.13.0 |
| draw.io | 28.2.5 |

重建时安装相同或兼容版本，再执行 `python -m pip install -r requirements-runtime-lock.txt`。训练和推理使用第 2 节的 `thesis` 环境，不使用 `runtime/python`。

## 4. 基座模型

三个大模型由 `modelscope download` 下载，并排除 `*.pth` 与 `original/*`（命令记录见 `logs/download_llms.sh`）。2026-10-13 核对时，本地全部文件与 ModelScope `master` 逐文件 SHA-256 和大小一致。

| 本地目录 | 上游 | 权重文件所在提交 | 核对时 master | 许可 | 大小 |
| --- | --- | --- | --- | --- | --- |
| `models/Qwen3-8B` | ModelScope `Qwen/Qwen3-8B` | `7c9709d23bd2136dac1d6ea1fe30f4107d681cd6` | `26028140`（2025-07-26） | Apache-2.0 | 15.3 GiB |
| `models/Qwen2.5-7B-Instruct` | ModelScope `Qwen/Qwen2.5-7B-Instruct` | `077a6aff06a7d75066ecc3abe12ce0d673873603` | `16c17498`（2025-02-26） | Apache-2.0 | 14.2 GiB |
| `models/glm-4-9b-chat-hf` | ModelScope `ZhipuAI/glm-4-9b-chat-hf` | `264d65dcf81b1454f6890d7fb5aa08ebff9117c5` | `cf7f3035`（2026-01-20） | GLM-4 模型许可（README 标注 `other`，以目录内 LICENSE 为准） | 17.5 GiB |
| `models/laya` | `laya==0.3.22` 下载的 Hugging Face 文件，提交 `55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851` | — | — | Apache-2.0 | 654 MiB |

Laya 只用于 `src/laya/zeroshot.py` 的探索，不属于论文主实验。

重新下载并核对：

```bash
modelscope download --model Qwen/Qwen3-8B --local_dir models/Qwen3-8B --exclude "*.pth" "original/*"
modelscope download --model Qwen/Qwen2.5-7B-Instruct --local_dir models/Qwen2.5-7B-Instruct --exclude "*.pth" "original/*"
modelscope download --model ZhipuAI/glm-4-9b-chat-hf --local_dir models/glm-4-9b-chat-hf --exclude "*.pth" "original/*"
sha256sum -c --ignore-missing configs/assets-sha256.txt
```

如上游以后更新，以校验值为准；不一致时不能直接视为论文所用模型。

## 5. FinFE 数据

- 上游：`supersymmetry-technologies/BBT-FinCUGE-Applications` 的 `FinCUGE_Publish/finfe/`；该路径最后修改提交为 `03dc5aabd5b41bb7bdfc24b05c3983f1aa530bf7`（2022-09-22）。
- 本地 `data/raw/finfe/` 的三个文件与上游 `main` 当前文件的 Git blob 一致：

| 文件 | 记录数 | 字节 | Git blob |
| --- | --- | --- | --- |
| `train_list.json` | 16157（有标签） | 1,085,511 | `29998e5571cc664f3f8eb28cfd6caa054ba10028` |
| `eval_list.json` | 2020（有标签） | 135,818 | `bd5fbb00c1e0c84fc5a133f61e6e5d0eb16b3727` |
| `problem_list.json` | 2020（无标签，未使用） | 173,232 | `cb29779d74b119efeb0a73f8f5e8c93030aad421` |

- 处理后数据：`data/processed/finfe/` 为训练 8802、验证 979、测试 1713（`src/data/prepare_finfe.py`）；`data/processed/finfe_raw/` 为训练 14541、验证 1616、测试 2020，用于泄露对照（`src/data/prepare_raw.py`）。SHA-256 见 `configs/assets-sha256.txt`。
- 许可：2026-10-13 检查，上游仓库没有 GitHub 可识别的许可证文件，也未见独立数据许可。因此 FinFE 数据不放入 Release，只保存在独立加密备份中；公开或分享前需要另行确认使用条件。
- 注意：`outputs/predictions/*.csv` 含测试文本列 `text`。仓库和 Release 目前均为私有；如果以后公开或分享，应先移除或替换文本内容。

重建时先运行 `python src/data/download_finfe.py`，再运行两个处理脚本（用法见脚本开头说明），最后用 `sha256sum -c --ignore-missing configs/assets-sha256.txt` 核对结果。

## 6. LoRA 微调权重

`src/llm/run_llm.py` 的 `train_lora()` 只在内存中保留验证集最优的 LoRA 参数，用于测试集预测后结束。当前代码和 Git 历史中都没有保存 adapter 的调用，本地也不存在 adapter 或训练状态文件，因此没有可以放入 Release 或备份的微调权重。

现有 `outputs/predictions/`（逐条概率）和 `outputs/metrics/` 足以支持论文中的统计分析，但不能在不重新训练的情况下对新文本推理。论文中的 17 次 LoRA/QLoRA 运行合计约 31,312 秒（约 8.7 小时，RTX 3090）。重新训练可得到新的 adapter，但 GPU 非确定性可能使结果与论文数字略有差异；修改训练代码或重新训练需另行确认。

## 7. Release

标签 `snapshot-20261013` 对应包含本文件的提交。附件包括论文 Word、LaTeX 预览 PDF、`outputs/` 结果包、脱敏后的关键实验与核验记录、环境清单和 `SHA256SUMS.txt`。

不包含：FinFE 数据、LoRA 权重、基座模型、`runtime/`、完整日志、修改前备份和第三方论文 PDF。下载全部附件后，在同一目录运行 `sha256sum -c SHA256SUMS.txt` 核对。

## 8. 独立加密备份

- 文件：`undergrad-thesis-crw-core-20261013.7z` 和同名 `.sha256` 文件；本机生成位置为 `D:\项目管理\undergrad-thesis-crw-backups\`。请复制到网盘或移动硬盘，至少保留一份不在这台电脑上的副本。
- 加密：7-Zip AES-256，同时加密文件名。密码由使用者本人设置，没有写入仓库、Release 或备份文件；遗失密码将无法恢复。
- 内容：`data/`、`logs/`、`.claude/`、`undergrad-thesis-crw.bundle`（全部分支与标签）、`BACKUP-MANIFEST-sha256.txt`、`BACKUP-README.txt`。
- 不含：基座模型、`runtime/`。

恢复步骤：

```bash
sha256sum -c undergrad-thesis-crw-core-20261013.7z.sha256
7z x undergrad-thesis-crw-core-20261013.7z -o恢复目录
cd 恢复目录
sha256sum -c BACKUP-MANIFEST-sha256.txt
git clone undergrad-thesis-crw.bundle undergrad-thesis-crw
```

然后把 `data/`、`logs/`、`.claude/` 复制回项目根目录，并在项目根目录运行 `sha256sum -c --ignore-missing configs/assets-sha256.txt`。

## 9. Agent 配置

`.claude/CLAUDE.md`（项目规则）和 `.claude/ars-install.json`（上游固定版本记录）进入仓库。`.claude/skills/` 与 `.claude/vendor/` 是 Academic Research Skills v3.23.0（提交 `d1e51716e53fc371727ea6164dd709fc8ea28c97`，CC BY-NC 4.0）的本地副本，不进入仓库；可从独立备份恢复，或按 `ars-install.json` 记录的版本重新获取。
