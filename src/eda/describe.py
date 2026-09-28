"""FinFE 描述性统计分析（论文第 3.2 节）。

输出（outputs/eda/）：
- stats.json                ：各项统计量
- summary.md                ：可直接放进论文的统计表
- fig_label_dist.png        ：各数据集类别分布
- fig_length_by_label.png   ：各类别文本长度分布（箱线图）
- fig_length_hist.png       ：文本长度直方图
- fig_top_words.png         ：各类别高频词

统计检验：
- 卡方检验：训练集、验证集、测试集的类别分布是否一致
- Kruskal-Wallis 检验：三类文本的长度分布是否存在差异

用法：python src/eda/describe.py
"""
from collections import Counter
import json
from pathlib import Path
import re

import jieba
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

matplotlib.use("Agg")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
jieba.setLogLevel(60)

DATA = Path("data/processed/finfe")
OUT = Path("outputs/eda")
LABELS = {0: "消极", 1: "中性", 2: "积极"}
COLORS = {"消极": "#d62728", "中性": "#7f7f7f", "积极": "#2ca02c"}
STOP = set("的 了 是 我 你 他 她 它 们 在 有 就 都 也 和 与 还 又 被 把 这 那 啊 吧 吗 呢 呀 哈 么 个 不 没 要 会 能 让 给 到 说 看 去 来 上 下 一 很 太 再 才 啥 什么 怎么 这个 那个 就是 还是 可以 自己 今天 明天 现在 已经 没有 一个 大家 知道 不是 真的".split())
NEG_WORDS = ["不", "没", "别", "无", "非", "未", "莫"]


def load(split: str) -> pd.DataFrame:
    df = pd.read_json(DATA / f"{split}.jsonl", lines=True)
    df["split"] = split
    df["类别"] = df["label"].map(LABELS)
    df["长度"] = df["text"].str.len()
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.concat([load(s) for s in ["train", "val", "test"]], ignore_index=True)
    order = list(LABELS.values())
    res: dict = {}

    # 1. 类别分布
    ct = pd.crosstab(df["split"], df["类别"])[order].loc[["train", "val", "test"]]
    chi2, p, dof, _ = stats.chi2_contingency(ct.values)
    res["label_counts"] = ct.to_dict(orient="index")
    res["label_ratio"] = (ct.div(ct.sum(1), axis=0).round(4)).to_dict(orient="index")
    res["chi2_split_vs_label"] = {"chi2": round(chi2, 4), "dof": int(dof), "p": float(f"{p:.4g}")}

    # 2. 文本长度
    desc = df.groupby("类别")["长度"].describe()[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]].loc[order]
    res["length_by_label"] = desc.round(2).to_dict(orient="index")
    res["length_overall"] = df["长度"].describe().round(2).to_dict()
    groups = [df.loc[df["类别"] == c, "长度"] for c in order]
    h, p_kw = stats.kruskal(*groups)
    res["kruskal_length_vs_label"] = {"H": round(h, 4), "p": float(f"{p_kw:.4g}")}

    # 3. 文本特征：否定词、数字、问号、感叹号
    feats = {
        "含否定词": df["text"].apply(lambda s: any(w in s for w in NEG_WORDS)),
        "含数字": df["text"].str.contains(r"\d"),
        "含问号": df["text"].str.contains(r"[?？]"),
        "含感叹号": df["text"].str.contains(r"[!！]"),
    }
    res["text_features_ratio_by_label"] = {}
    for name, s in feats.items():
        tab = pd.crosstab(df["类别"], s.astype(bool)).reindex(columns=[False, True], fill_value=0).loc[order]
        c2, pp, _, _ = stats.chi2_contingency(tab.values)
        res["text_features_ratio_by_label"][name] = {
            **{c: round(float(tab.loc[c, True] / tab.loc[c].sum()), 4) for c in order},
            "chi2": round(c2, 3), "p": float(f"{pp:.4g}")}

    # 4. 高频词（训练集）
    tr = df[df["split"] == "train"]
    top = {}
    for c in order:
        cnt = Counter(w for s in tr.loc[tr["类别"] == c, "text"] for w in jieba.lcut(s)
                      if len(w) > 1 and w not in STOP and not re.fullmatch(r"[\W\d_a-zA-Z]+", w))
        top[c] = cnt.most_common(15)
    res["top_words_train"] = top

    (OUT / "stats.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str) + "\n", "utf-8")

    # ---------- 图 ----------
    fig, ax = plt.subplots(figsize=(7, 4))
    ratio = ct.div(ct.sum(1), axis=0)
    ratio.index = ["训练集", "验证集", "测试集"]
    ratio.plot(kind="bar", ax=ax, color=[COLORS[c] for c in order], rot=0)
    for cont in ax.containers:
        ax.bar_label(cont, fmt="%.1f%%", labels=[f"{v*100:.1f}%" for v in cont.datavalues], fontsize=8)
    ax.set_ylabel("比例"); ax.set_title("各数据集类别分布"); ax.legend(title="类别")
    fig.tight_layout(); fig.savefig(OUT / "fig_label_dist.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.boxplot(groups, tick_labels=order, showfliers=False, patch_artist=True,
               boxprops=dict(facecolor="#dbe9f6"))
    ax.set_ylabel("文本长度（字符）"); ax.set_title("各类别文本长度分布")
    fig.tight_layout(); fig.savefig(OUT / "fig_length_by_label.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.arange(0, df["长度"].max() + 3, 2)
    for c in order:
        ax.hist(df.loc[df["类别"] == c, "长度"], bins=bins, alpha=0.5, label=c, color=COLORS[c])
    ax.set_xlabel("文本长度（字符）"); ax.set_ylabel("频数"); ax.set_title("文本长度直方图"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "fig_length_hist.png", dpi=200); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5))
    for ax, c in zip(axes, order):
        words, cnts = zip(*top[c][::-1])
        ax.barh(words, cnts, color=COLORS[c]); ax.set_title(f"{c}类高频词")
    fig.tight_layout(); fig.savefig(OUT / "fig_top_words.png", dpi=200); plt.close(fig)

    # ---------- 论文用表格 ----------
    rep = json.loads(Path("outputs/eda/cleaning_report.json").read_text("utf-8"))
    L = ["# FinFE 描述性统计结果", "",
         "由 `src/eda/describe.py` 自动生成。", "",
         "## 表 3-1 数据清洗过程", "",
         "| 步骤 | 数量 |", "| --- | --- |",
         f"| 原始训练文件 train_list | {rep['raw']['train_list']} |",
         f"| 原始评估文件 eval_list | {rep['raw']['eval_list']} |"]
    names = {
        "train_duplicates_removed": "训练文件：删除重复样本（标签一致）",
        "train_conflicting_texts_removed": "训练文件：删除标签冲突的文本",
        "eval_duplicates_removed": "评估文件：删除重复样本（标签一致）",
        "eval_conflicting_texts_removed": "评估文件：删除标签冲突的文本",
        "eval_texts_also_in_train_same_label": "评估文件中与训练文件重复且标签一致的文本",
        "eval_texts_also_in_train_diff_label_removed_from_test": "评估文件中与训练文件重复但标签不同的文本（从测试集删除）",
        "train_texts_removed_for_leakage": "训练池中与测试集重复的文本（删除以防数据泄露）",
    }
    for k, v in rep["cleaning"].items():
        L.append(f"| {names.get(k, k)} | {v} |")
    L += ["", "## 表 3-2 清洗后各数据集类别分布", "",
          "| 数据集 | 消极 | 中性 | 积极 | 合计 |", "| --- | --- | --- | --- | --- |"]
    for sp, name in [("train", "训练集"), ("val", "验证集"), ("test", "测试集")]:
        r = res["label_counts"][sp]; n = sum(r.values())
        L.append(f"| {name} | " + " | ".join(f"{r[c]}（{r[c]/n*100:.1f}%）" for c in order) + f" | {n} |")
    x = res["chi2_split_vs_label"]
    L += ["", f"卡方检验（数据集 × 类别）：χ² = {x['chi2']}，自由度 = {x['dof']}，p = {x['p']}。", "",
          "## 表 3-3 各类别文本长度（字符）", "",
          "| 类别 | 样本数 | 均值 | 标准差 | 最小值 | 中位数 | 最大值 |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for c in order:
        d = res["length_by_label"][c]
        L.append(f"| {c} | {int(d['count'])} | {d['mean']} | {d['std']} | {int(d['min'])} | {d['50%']} | {int(d['max'])} |")
    k = res["kruskal_length_vs_label"]
    L += ["", f"Kruskal-Wallis 检验：H = {k['H']}，p = {k['p']}。", "",
          "## 表 3-4 文本特征在各类别中的占比", "",
          "| 特征 | 消极 | 中性 | 积极 | χ² | p |", "| --- | --- | --- | --- | --- | --- |"]
    for name, d in res["text_features_ratio_by_label"].items():
        L.append(f"| {name} | " + " | ".join(f"{d[c]*100:.1f}%" for c in order) + f" | {d['chi2']} | {d['p']} |")
    L += ["", "## 表 3-5 训练集各类别高频词（前 15）", "", "| 类别 | 高频词（词频） |", "| --- | --- |"]
    for c in order:
        L.append(f"| {c} | " + "、".join(f"{w}（{n}）" for w, n in top[c]) + " |")
    (OUT / "summary.md").write_text("\n".join(L) + "\n", "utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
