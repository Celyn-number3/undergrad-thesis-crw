#!/usr/bin/env bash
# 创建实验环境（Windows Git Bash / Linux 通用）
# 用法：bash scripts/setup_env.sh
set -e
if [ -f /e/anaconda3/etc/profile.d/conda.sh ]; then source /e/anaconda3/etc/profile.d/conda.sh; else source "$(conda info --base)/etc/profile.d/conda.sh"; fi
conda create -y -n thesis python=3.11
conda activate thesis
python -m pip install --upgrade pip
# RTX 3090 + 驱动支持 CUDA 12.8 及以上，使用 cu128 版本的 PyTorch
pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
python src/utils/check_env.py
