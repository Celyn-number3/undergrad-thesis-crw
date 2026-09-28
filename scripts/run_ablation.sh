#!/usr/bin/env bash
# E5 消融实验（Qwen3-8B，种子 42）：LoRA 秩、训练样本量、4-bit 量化
# r=16、全量数据、16 位精度的结果已在主实验中得到，不再重复
set -e
export PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1
PY="python -m src.llm.run_llm --model models/Qwen3-8B --mode lora --seed 42"
for n in 500 1000 2000 4000; do $PY --train-size $n --epochs 3; done
for r in 4 8 32; do $PY --rank $r; done
$PY --load-4bit
echo ABLATION_DONE
