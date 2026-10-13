"""评估曝光与清洗策略的描述性比较；不把不同测试子集的差值当成纯泄漏效应。

区分原始训练文件曝光（含后来划出的验证集）与实际优化训练集曝光；
另在同样的共同未曝光文本上对齐两种训练策略。只读取现有预测，不训练。
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
MODELS = {
    "TF-IDF+LR": ("tfidf_lr_raw", "tfidf_lr"),
    "RoBERTa": ("chinese-roberta-wwm-ext_raw", "chinese-roberta-wwm-ext"),
}
SEEDS = [42, 43, 44]


def files(prefix):
    f = PRED / f"{prefix}.csv"
    return [f] if f.exists() else [PRED / f"{prefix}_s{s}.csv" for s in SEEDS]


def score(d):
    if len(d) == 0:
        return np.nan, np.nan
    return float((d.pred == d.label).mean()), float(f1_score(d.label, d.pred, average="macro"))


def label_map(frame):
    result = defaultdict(set)
    for row in frame.itertuples():
        result[row.text].add(row.label)
    return result


def exposure_groups(test, labels):
    return np.array(["unseen" if r.text not in labels else
                     "seen_same" if r.label in labels[r.text] else "seen_diff"
                     for r in test.itertuples()])


def aligned(path, target):
    d = pd.read_csv(path)
    if list(zip(d.text, d.label)) != list(zip(target.text, target.label)):
        raise ValueError(f"预测与相应测试集未对齐：{path}")
    return d


def main():
    train = pd.read_json(RAW_DIR / "train.jsonl", lines=True)
    val = pd.read_json(RAW_DIR / "val.jsonl", lines=True)
    test = pd.read_json(RAW_DIR / "test.jsonl", lines=True)
    clean_test = pd.read_json("data/processed/finfe/test.jsonl", lines=True)
    groups = {
        "原始训练文件(含验证)": exposure_groups(test, label_map(pd.concat([train, val]))),
        "实际优化训练集": exposure_groups(test, label_map(train)),
    }
    unseen_texts = set(test.loc[groups["原始训练文件(含验证)"] == "unseen", "text"])
    common_texts = unseen_texts & set(clean_test.text)
    rows, matched = [], []
    for name, (raw_prefix, clean_prefix) in MODELS.items():
        raw_files, clean_files = files(raw_prefix), files(clean_prefix)
        if len(raw_files) != len(clean_files):
            raise ValueError(f"运行次数不一致：{name}")
        raw_predictions = [aligned(f, test) for f in raw_files]
        clean_predictions = [aligned(f, clean_test) for f in clean_files]
        for basis, group in groups.items():
            for subset in ["全部测试集", "seen_same", "seen_diff", "unseen"]:
                mask = np.ones(len(test), dtype=bool) if subset == "全部测试集" else group == subset
                values = np.array([score(d[mask]) for d in raw_predictions])
                rows.append({"模型": name, "训练与测试方式": "未清洗", "分组依据": basis,
                             "子集": subset, "样本数": int(mask.sum()), "准确率": values[:, 0].mean(),
                             "MacroF1": values[:, 1].mean(), "运行次数": len(values)})
        values = np.array([score(d) for d in clean_predictions])
        rows.append({"模型": name, "训练与测试方式": "清洗后", "分组依据": "清洗后完整测试集",
                     "子集": "全部测试集", "样本数": len(clean_test), "准确率": values[:, 0].mean(),
                     "MacroF1": values[:, 1].mean(), "运行次数": len(values)})
        paired = []
        for a, b in zip(raw_predictions, clean_predictions):
            a = a[a.text.isin(common_texts)].drop_duplicates("text").sort_values("text")
            b = b[b.text.isin(common_texts)].sort_values("text")
            if list(zip(a.text, a.label)) != list(zip(b.text, b.label)):
                raise ValueError("共同文本标签不一致")
            paired.append([*score(a), *score(b)])
        values = np.array(paired)
        matched.append({"模型": name, "共同文本数": len(common_texts), "运行次数": len(values),
                        "未清洗训练_准确率": values[:, 0].mean(), "未清洗训练_MacroF1": values[:, 1].mean(),
                        "清洗后训练_准确率": values[:, 2].mean(), "清洗后训练_MacroF1": values[:, 3].mean(),
                        "MacroF1差(清洗后-未清洗)": (values[:, 3] - values[:, 1]).mean()})
    df, matched_df = pd.DataFrame(rows), pd.DataFrame(matched)
    summary = {
        "解释限制": "所有跨子集差值为描述性比较，不识别纯泄漏因果效应；验证曝光与实际训练曝光分开报告",
        "分组计数": {basis: pd.Series(group).value_counts().to_dict() for basis, group in groups.items()},
        "仅验证曝光的原始评估记录数": int(test.text.isin(set(val.text) - set(train.text)).sum()),
        "原始训练文件口径子集类别计数": {
            g: {str(k): int(v) for k, v in test.loc[groups["原始训练文件(含验证)"] == g, "label"].value_counts().items()}
            for g in ["seen_same", "seen_diff", "unseen"]},
        "原始训练文件口径子集类别比例": {
            g: {str(k): float(v) for k, v in test.loc[groups["原始训练文件(含验证)"] == g, "label"].value_counts(normalize=True).items()}
            for g in ["seen_same", "seen_diff", "unseen"]},
        "共同未曝光文本比较": matched,
        "原始训练文件口径_全体与unseen的描述差": {},
    }
    for name in MODELS:
        selected = df[(df.模型 == name) & (df.分组依据 == "原始训练文件(含验证)")].set_index("子集")
        summary["原始训练文件口径_全体与unseen的描述差"][name] = float(selected.loc["全部测试集", "MacroF1"] - selected.loc["unseen", "MacroF1"])
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "leakage.csv", index=False, encoding="utf-8-sig")
    matched_df.to_csv(OUT / "leakage_matched.csv", index=False, encoding="utf-8-sig")
    (OUT / "leakage.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(df.round(4).to_string(index=False))
    print(matched_df.round(4).to_string(index=False))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
