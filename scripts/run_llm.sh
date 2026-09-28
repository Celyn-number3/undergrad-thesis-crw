#!/usr/bin/env bash
# 大模型主实验（E3 零样本/少样本 + E4 LoRA 微调）
# 用法：bash scripts/run_llm.sh models/Qwen3-8B
set -e
M=${1:?请指定模型目录，如 models/Qwen3-8B}
export PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1
PY="python -m src.llm.run_llm --model $M"
$PY --mode zeroshot
$PY --mode fewshot --shots 1 --seed 42
$PY --mode fewshot --shots 3 --seed 42 --eval-bs 16
$PY --mode lora --seed 42
echo "LLM_DONE $M"
