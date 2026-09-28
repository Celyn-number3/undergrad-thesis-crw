"""通用评价工具：计算指标并保存预测结果，供后续统计检验使用。"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

LABELS = ["消极", "中性", "积极"]
PRED_DIR = Path("outputs/predictions")
METRIC_DIR = Path("outputs/metrics")


def load_split(split: str) -> pd.DataFrame:
    return pd.read_json(f"data/processed/finfe/{split}.jsonl", lines=True)


def evaluate(y_true, y_pred) -> dict:
    rep = classification_report(y_true, y_pred, target_names=LABELS, output_dict=True, zero_division=0)
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "macro_f1": round(f1_score(y_true, y_pred, average="macro"), 4),
        "weighted_f1": round(f1_score(y_true, y_pred, average="weighted"), 4),
        "per_class_f1": {c: round(rep[c]["f1-score"], 4) for c in LABELS},
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1, 2]).tolist(),
    }


def save_run(name: str, test_df: pd.DataFrame, probs: np.ndarray, extra: dict | None = None) -> dict:
    """保存测试集逐条预测（含三类概率）与汇总指标。"""
    PRED_DIR.mkdir(parents=True, exist_ok=True)
    METRIC_DIR.mkdir(parents=True, exist_ok=True)
    pred = probs.argmax(1)
    out = test_df[["text", "label"]].copy()
    out["pred"] = pred
    for i in range(3):
        out[f"p{i}"] = probs[:, i].round(6)
    out.to_csv(PRED_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")
    m = {"model": name, **evaluate(test_df["label"].values, pred), **(extra or {})}
    (METRIC_DIR / f"{name}.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", "utf-8")
    return m
