"""量化数据泄露对评估结果的影响。

对比两种做法：
- 未清洗：在原始训练文件上训练，在原始 eval_list（2020 条）上测试；
- 清洗后：本文的做法（去重、去冲突、去泄露），测试集 1713 条。

把未清洗测试集按“是否在训练文件中出现过”分成三组：
  seen_same：训练文件中出现过，且训练中有相同标签（模型可以“背答案”）
  seen_diff：训练文件中出现过，但标签与训练中都不同（背答案反而会错）
  unseen   ：训练文件中没有出现过
分别计算准确率与 Macro-F1，看泄露让分数虚高了多少。

用法：python -m src.analysis.leakage
"""
from collections import defaultdict
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

PRED = Path("outputs/predictions")
OUT = Path("outputs/analysis")
RAW_DIR = Path("data/processed/finfe_raw")
MODELS = {  # 显示名 -> (未清洗预测文件前缀, 清洗后预测文件前缀)
    "TF-IDF+LR": ("tfidf_lr_raw", "tfidf_lr"),
    "RoBERTa": ("chinese-roberta-wwm-ext_raw", "chinese-roberta-wwm-ext"),
}
SEEDS = [42, 43, 44]


def files(prefix):
    f = PRED / f"{prefix}.csv"
    return [f] if f.exists() else [PRED / f"{prefix}_s{s}.csv" for s in SEEDS if (PRED / f"{prefix}_s{s}.csv").exists()]


def score(df):
    if len(df) == 0:
        return np.nan, np.nan
    return (df.pred == df.label).mean(), f1_score(df.label, df.pred, average="macro")


def main():
    train_labels = defaultdict(set)
    for split in ("train", "val"):  # 未清洗做法中，验证集也来自训练文件
        for r in pd.read_json(RAW_DIR / f"{split}.jsonl", lines=True).itertuples():
            train_labels[r.text].add(r.label)
    test = pd.read_json(RAW_DIR / "test.jsonl", lines=True)

    def group(r):
        if r.text not in train_labels:
            return "unseen"
        return "seen_same" if r.label in train_labels[r.text] else "seen_diff"
    test["group"] = [group(r) for r in test.itertuples()]
    counts = test["group"].value_counts().to_dict()
    clean_test = pd.read_json("data/processed/finfe/test.jsonl", lines=True)
    unseen_texts = set(test.loc[test.group == "unseen", "text"])

    rows = []
    for name, (raw_p, clean_p) in MODELS.items():
        for kind, prefix in (("未清洗", raw_p), ("清洗后", clean_p)):
            res = defaultdict(list)
            for f in files(prefix):
                d = pd.read_csv(f)
                if kind == "未清洗":
                    d["group"] = test["group"].values
                    res["全部测试集"].append(score(d))
                    for g in ("seen_same", "seen_diff", "unseen"):
                        res[g].append(score(d[d.group == g]))
                else:
                    res["全部测试集"].append(score(d))
                    res["unseen"].append(score(d[d.text.isin(unseen_texts)]))
            for g, v in res.items():
                v = np.array(v)
                rows.append({"模型": name, "训练与测试方式": kind, "子集": g,
                             "样本数": {"全部测试集": 2020 if kind == "未清洗" else len(clean_test)}.get(
                                 g, counts.get(g) if kind == "未清洗" else int(clean_test.text.isin(unseen_texts).sum())),
                             "准确率": v[:, 0].mean(), "MacroF1": v[:, 1].mean(), "运行次数": len(v)})
    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "leakage.csv", index=False, encoding="utf-8-sig")
    summary = {"未清洗测试集分组": counts}
    for name in MODELS:
        g = df[df.模型 == name].set_index(["训练与测试方式", "子集"])
        summary[name] = {
            "未清洗_全部": round(g.loc[("未清洗", "全部测试集"), "MacroF1"], 4),
            "未清洗_未见过": round(g.loc[("未清洗", "unseen"), "MacroF1"], 4),
            "未清洗_见过同标签": round(g.loc[("未清洗", "seen_same"), "MacroF1"], 4),
            "清洗后_全部": round(g.loc[("清洗后", "全部测试集"), "MacroF1"], 4),
            "虚高(未清洗全部-清洗后全部)": round(g.loc[("未清洗", "全部测试集"), "MacroF1"] - g.loc[("清洗后", "全部测试集"), "MacroF1"], 4),
        }
    (OUT / "leakage.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(df.round(4).to_string()); print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
