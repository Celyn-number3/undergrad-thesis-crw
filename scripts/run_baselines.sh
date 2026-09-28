#!/usr/bin/env bash
# 运行全部对照实验（E1 + E2）
set -e
python -m src.baselines.tfidf
for m in google-bert/bert-base-chinese hfl/chinese-roberta-wwm-ext; do
  python -m src.baselines.bert --model "$m" --seeds 42 43 44
done
echo BASELINES_DONE
