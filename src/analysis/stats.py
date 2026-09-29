"""E6/E7 统计评估：显著性检验、校准分析与选择性预测。

输入：outputs/predictions/*.csv（每个模型在测试集上的逐条预测与三类概率）
输出：outputs/analysis/ 下的 JSON、Markdown 汇总表和图

分析内容
1. 主结果表：准确率、Macro-F1、各类 F1；多种子给出均值 ± 标准差；
   单次运行给出 Bootstrap 95% 置信区间（测试集重抽样 2000 次）。
2. McNemar 检验（两两比较，种子 42），用 Holm 方法校正多重比较。
3. 配对 Bootstrap：关键模型之间 Macro-F1 差值的 95% 置信区间。
4. 单因素方差分析（多种子）+ Levene 方差齐性检验 + Tukey HSD 事后比较。
5. 校准：ECE、MCE、Brier 分数、NLL；温度缩放（在测试集上做 5 折交叉拟合）；可靠性图。
6. 选择性预测：风险-覆盖率曲线、AURC、E-AURC、指定覆盖率下的准确率。

用法：python -m src.analysis.stats
"""
from itertools import combinations
import json
from pathlib import Path
import re

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize, stats
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.multitest import multipletests

matplotlib.use("Agg")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

PRED = Path("outputs/predictions")
OUT = Path("outputs/analysis")
LABELS = ["消极", "中性", "积极"]
N_BOOT = 2000
RNG = np.random.default_rng(2026)

# 主比较中的模型：显示名 -> 文件名前缀（多种子文件形如 前缀_s42.csv）
MAIN = {
    "TF-IDF+LR": "tfidf_lr",
    "TF-IDF+SVM": "tfidf_svm",
    "BERT": "bert-base-chinese",
    "RoBERTa": "chinese-roberta-wwm-ext",
    "Qwen3-8B 零样本": "Qwen3-8B_zeroshot",
    "Qwen3-8B 少样本(3)": "Qwen3-8B_fewshot3",
    "Qwen2.5-7B 零样本": "Qwen2.5-7B-Instruct_zeroshot",
    "Qwen2.5-7B 少样本(3)": "Qwen2.5-7B-Instruct_fewshot3",
    "GLM-4-9B 零样本": "glm-4-9b-chat-hf_zeroshot",
    "GLM-4-9B 少样本(3)": "glm-4-9b-chat-hf_fewshot3",
    "Qwen3-8B LoRA": "Qwen3-8B_lora_r16",
    "Qwen2.5-7B LoRA": "Qwen2.5-7B-Instruct_lora_r16",
    "GLM-4-9B LoRA": "glm-4-9b-chat-hf_lora_r16",
}
# McNemar / Bootstrap 两两比较的模型（均取种子 42 或单次运行）
PAIRWISE = ["TF-IDF+LR", "RoBERTa", "Qwen3-8B LoRA", "Qwen2.5-7B LoRA", "GLM-4-9B LoRA"]
# 方差分析的组（需要多个种子）
ANOVA = ["BERT", "RoBERTa", "Qwen3-8B LoRA", "Qwen2.5-7B LoRA", "GLM-4-9B LoRA"]
# 校准与选择性预测分析的模型
CALIB = ["TF-IDF+LR", "RoBERTa", "Qwen3-8B 零样本", "Qwen3-8B LoRA", "Qwen2.5-7B LoRA", "GLM-4-9B LoRA"]


# ------------------------------------------------------------------ 读取
def files_for(prefix: str) -> list[Path]:
    exact = PRED / f"{prefix}.csv"
    if exact.exists():
        return [exact]
    fs = sorted(p for p in PRED.glob(f"{prefix}_s*.csv") if re.fullmatch(rf"{re.escape(prefix)}_s\d+", p.stem))
    return fs


def load(path: Path):
    d = pd.read_csv(path)
    return d["label"].to_numpy(), d[["p0", "p1", "p2"]].to_numpy()


def seed42(prefix: str) -> Path:
    fs = files_for(prefix)
    for f in fs:
        if f.stem.endswith("_s42"):
            return f
    return fs[0]


def macro_f1(y, pred):
    return f1_score(y, pred, average="macro")


# ------------------------------------------------------------------ 1 主结果
def boot_ci(y, pred, fn=macro_f1):
    n = len(y)
    vals = [fn(y[i], pred[i]) for i in (RNG.integers(0, n, n) for _ in range(N_BOOT))]
    return np.percentile(vals, [2.5, 97.5])


def main_table():
    rows = []
    for name, prefix in MAIN.items():
        fs = files_for(prefix)
        if not fs:
            continue
        accs, f1s, pcs = [], [], []
        for f in fs:
            y, p = load(f)
            pr = p.argmax(1)
            accs.append((pr == y).mean())
            f1s.append(macro_f1(y, pr))
            pcs.append(f1_score(y, pr, average=None))
        y, p = load(seed42(prefix))
        lo, hi = boot_ci(y, p.argmax(1))
        pc = np.mean(pcs, 0)
        rows.append({"模型": name, "运行次数": len(fs),
                     "准确率均值": np.mean(accs), "准确率标准差": np.std(accs, ddof=1) if len(fs) > 1 else np.nan,
                     "MacroF1均值": np.mean(f1s), "MacroF1标准差": np.std(f1s, ddof=1) if len(fs) > 1 else np.nan,
                     "MacroF1_CI下限": lo, "MacroF1_CI上限": hi,
                     "消极F1": pc[0], "中性F1": pc[1], "积极F1": pc[2], "各次MacroF1": [round(v, 4) for v in f1s]})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 2 McNemar
def mcnemar_all():
    preds = {}
    for name in PAIRWISE:
        fs = files_for(MAIN[name])
        if fs:
            y, p = load(seed42(MAIN[name]))
            preds[name] = p.argmax(1) == y
    rows = []
    for a, b in combinations(preds, 2):
        ca, cb = preds[a], preds[b]
        n01, n10 = int((ca & ~cb).sum()), int((~ca & cb).sum())
        tab = [[int((ca & cb).sum()), n01], [n10, int((~ca & ~cb).sum())]]
        exact = n01 + n10 < 25
        r = mcnemar(tab, exact=exact, correction=not exact)
        rows.append({"模型A": a, "模型B": b, "A对B错": n01, "A错B对": n10,
                     "统计量": float(r.statistic), "p值": float(r.pvalue)})
    df = pd.DataFrame(rows)
    df["Holm校正p值"] = multipletests(df["p值"], method="holm")[1]
    df["显著(0.05)"] = df["Holm校正p值"] < 0.05
    return df


# ------------------------------------------------------------------ 3 配对 Bootstrap
def paired_bootstrap():
    data = {}
    for name in PAIRWISE:
        if files_for(MAIN[name]):
            y, p = load(seed42(MAIN[name]))
            data[name] = p.argmax(1)
    n = len(y)
    idx = [RNG.integers(0, n, n) for _ in range(N_BOOT)]
    rows = []
    for a, b in combinations(data, 2):
        d = np.array([macro_f1(y[i], data[a][i]) - macro_f1(y[i], data[b][i]) for i in idx])
        rows.append({"模型A": a, "模型B": b, "F1差值(A-B)": macro_f1(y, data[a]) - macro_f1(y, data[b]),
                     "CI下限": np.percentile(d, 2.5), "CI上限": np.percentile(d, 97.5),
                     "单侧p(A<=B)": float((d <= 0).mean())})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 4 方差分析
def anova():
    groups = {}
    for name in ANOVA:
        fs = files_for(MAIN[name])
        if len(fs) >= 2:
            groups[name] = [macro_f1(*(lambda y, p: (y, p.argmax(1)))(*load(f))) for f in fs]
    vals = list(groups.values())
    res = {"组": {k: [round(x, 4) for x in v] for k, v in groups.items()}}
    f, p = stats.f_oneway(*vals)
    res["ANOVA"] = {"F": round(float(f), 3), "p": float(f"{p:.4g}")}
    lev = stats.levene(*vals, center="median")
    res["Levene"] = {"W": round(float(lev.statistic), 3), "p": float(f"{lev.pvalue:.4g}")}
    wel = welch_anova(vals)
    res["Welch_ANOVA"] = wel
    endog = np.concatenate(vals)
    grp = np.concatenate([[k] * len(v) for k, v in groups.items()])
    tk = pairwise_tukeyhsd(endog, grp, alpha=0.05)
    t = pd.DataFrame(tk.summary().data[1:], columns=tk.summary().data[0])
    res["Tukey_HSD"] = t.to_dict(orient="records")
    # 只比较三个 LoRA 大模型
    llm = [v for k, v in groups.items() if "LoRA" in k]
    if len(llm) >= 2:
        f2, p2 = stats.f_oneway(*llm)
        res["ANOVA_仅LoRA大模型"] = {"F": round(float(f2), 3), "p": float(f"{p2:.4g}")}
    return res


def welch_anova(groups):
    k = len(groups)
    n = np.array([len(g) for g in groups]); m = np.array([np.mean(g) for g in groups])
    v = np.array([np.var(g, ddof=1) for g in groups])
    w = n / np.maximum(v, 1e-12)
    mw = (w * m).sum() / w.sum()
    a = (w * (m - mw) ** 2).sum() / (k - 1)
    tmp = ((1 - w / w.sum()) ** 2 / (n - 1)).sum()
    b = 1 + 2 * (k - 2) / (k ** 2 - 1) * tmp
    f = a / b
    df2 = (k ** 2 - 1) / (3 * tmp)
    p = stats.f.sf(f, k - 1, df2)
    return {"F": round(float(f), 3), "df1": k - 1, "df2": round(float(df2), 2), "p": float(f"{p:.4g}")}


# ------------------------------------------------------------------ 5 校准
def ece_mce(y, p, bins=15):
    conf, pred = p.max(1), p.argmax(1)
    acc = pred == y
    edges = np.linspace(0, 1, bins + 1)
    ece, mce, curve = 0.0, 0.0, []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.sum() == 0:
            continue
        gap = abs(acc[m].mean() - conf[m].mean())
        ece += m.mean() * gap
        mce = max(mce, gap)
        curve.append((conf[m].mean(), acc[m].mean(), int(m.sum())))
    return ece, mce, curve


def brier(y, p):
    oh = np.eye(3)[y]
    return float(((p - oh) ** 2).sum(1).mean())


def nll(y, p):
    return float(-np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1)).mean())


def temp_scale(logits, y):
    def loss(t):
        z = logits / t
        z = z - z.max(1, keepdims=True)
        lp = z - np.log(np.exp(z).sum(1, keepdims=True))
        return -lp[np.arange(len(y)), y].mean()
    return optimize.minimize_scalar(loss, bounds=(0.05, 20), method="bounded").x


def softmax(z):
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def calibration():
    rows, curves, scaled = [], {}, {}
    for name in CALIB:
        if not files_for(MAIN[name]):
            continue
        y, p = load(seed42(MAIN[name]))
        logits = np.log(np.clip(p, 1e-12, 1))
        # 温度缩放：5 折交叉拟合（在 4 折上拟合 T，应用到剩下 1 折）
        ps, ts = np.zeros_like(p), []
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(p, y):
            t = temp_scale(logits[tr], y[tr]); ts.append(t)
            ps[te] = softmax(logits[te] / t)
        e, m, c = ece_mce(y, p)
        e2, m2, c2 = ece_mce(y, ps)
        rows.append({"模型": name, "平均置信度": float(p.max(1).mean()), "准确率": float((p.argmax(1) == y).mean()),
                     "ECE": e, "MCE": m, "Brier": brier(y, p), "NLL": nll(y, p),
                     "温度T(均值)": float(np.mean(ts)), "缩放后ECE": e2, "缩放后Brier": brier(y, ps), "缩放后NLL": nll(y, ps)})
        curves[name], scaled[name] = c, c2
    return pd.DataFrame(rows), curves, scaled


# ------------------------------------------------------------------ 6 选择性预测
def risk_coverage(y, p):
    conf = p.max(1)
    err = (p.argmax(1) != y).astype(float)
    order = np.argsort(-conf, kind="stable")
    risks = np.cumsum(err[order]) / np.arange(1, len(y) + 1)
    cov = np.arange(1, len(y) + 1) / len(y)
    return cov, risks


def selective():
    rows, curves = [], {}
    for name in CALIB:
        if not files_for(MAIN[name]):
            continue
        y, p = load(seed42(MAIN[name]))
        cov, risk = risk_coverage(y, p)
        aurc = float(risk.mean())
        r = (p.argmax(1) != y).mean()
        optimal = r + (1 - r) * np.log(1 - r) if r > 0 else 0.0  # 理想排序下的 AURC
        at = {c: float(1 - risk[int(c * len(y)) - 1]) for c in (0.5, 0.7, 0.8, 0.9, 1.0)}
        rows.append({"模型": name, "AURC": aurc, "E-AURC": aurc - optimal,
                     **{f"覆盖{int(c * 100)}%准确率": v for c, v in at.items()}})
        curves[name] = (cov, risk)
    return pd.DataFrame(rows), curves


# ------------------------------------------------------------------ 图
def plot_models(tab):
    t = tab[~tab["模型"].str.contains("TF-IDF\\+SVM")].sort_values("MacroF1均值")
    fig, ax = plt.subplots(figsize=(8, 5.5))
    colors = ["#4c72b0" if "LoRA" in m else "#dd8452" if ("样本" in m) else "#55a868" for m in t["模型"]]
    err = np.vstack([t["MacroF1均值"] - t["MacroF1_CI下限"], t["MacroF1_CI上限"] - t["MacroF1均值"]])
    ax.barh(t["模型"], t["MacroF1均值"], xerr=err, color=colors, capsize=3)
    for i, v in enumerate(t["MacroF1均值"]):
        ax.text(v + 0.012, i, f"{v:.3f}", va="center", fontsize=8)
    ax.set_xlim(0.55, 0.88); ax.set_xlabel("Macro-F1（误差线：Bootstrap 95% 置信区间）")
    ax.set_title("各模型测试集 Macro-F1")
    fig.tight_layout(); fig.savefig(OUT / "fig_model_comparison.png", dpi=200); plt.close(fig)


def plot_reliability(curves, scaled):
    names = list(curves)
    fig, axes = plt.subplots(2, (len(names) + 1) // 2, figsize=(4 * ((len(names) + 1) // 2), 8))
    for ax, n in zip(axes.flat, names):
        for c, style, lab in [(curves[n], "o-", "原始"), (scaled[n], "s--", "温度缩放后")]:
            if c:
                x, yv, _ = zip(*c)
                ax.plot(x, yv, style, ms=4, label=lab)
        ax.plot([0, 1], [0, 1], "k:", lw=1)
        ax.set_xlim(0.3, 1); ax.set_ylim(0.3, 1); ax.set_title(n, fontsize=10)
        ax.set_xlabel("平均置信度"); ax.set_ylabel("实际准确率"); ax.legend(fontsize=8)
    for ax in list(axes.flat)[len(names):]:
        ax.axis("off")
    fig.suptitle("可靠性图（对角线 = 完美校准；曲线在对角线下方 = 过度自信）")
    fig.tight_layout(); fig.savefig(OUT / "fig_reliability.png", dpi=200); plt.close(fig)


def plot_rc(curves):
    fig, ax = plt.subplots(figsize=(7, 5))
    for n, (cov, risk) in curves.items():
        ax.plot(cov, risk, label=n)
    ax.set_xlabel("覆盖率（模型选择作答的样本比例）"); ax.set_ylabel("错误率")
    ax.set_xlim(0.1, 1); ax.set_title("风险-覆盖率曲线（越低越好）"); ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(OUT / "fig_risk_coverage.png", dpi=200); plt.close(fig)


def ablation():
    rows = []
    def get(stem):
        f = PRED / f"{stem}.csv"
        if f.exists():
            y, p = load(f); return macro_f1(y, p.argmax(1)), float((p.argmax(1) == y).mean())
        return None
    full = get("Qwen3-8B_lora_r16_s42")
    zero = get("Qwen3-8B_zeroshot")
    size = [(0, zero)] + [(n, get(f"Qwen3-8B_lora_r16_n{n}_s42")) for n in (500, 1000, 2000, 4000)] + [(8802, full)]
    rank = [(r, get(f"Qwen3-8B_lora_r{r}_s42")) for r in (4, 8, 16, 32)]
    quant = [("16 位", full), ("4 位", get("Qwen3-8B_lora_r16_4bit_s42"))]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    s = [(n, v) for n, v in size if v]
    axes[0].plot([n for n, _ in s], [v[0] for _, v in s], "o-")
    rob = [macro_f1(*(lambda y, p: (y, p.argmax(1)))(*load(f))) for f in files_for("chinese-roberta-wwm-ext")]
    if rob:
        axes[0].axhline(np.mean(rob), color="gray", ls="--", label="RoBERTa（全部数据）"); axes[0].legend()
    axes[0].set_xlabel("训练样本数（0 = 零样本）"); axes[0].set_ylabel("Macro-F1"); axes[0].set_title("训练样本量")
    r = [(k, v) for k, v in rank if v]
    axes[1].bar([str(k) for k, _ in r], [v[0] for _, v in r], color="#4c72b0")
    axes[1].set_ylim(0.75, 0.83); axes[1].set_xlabel("LoRA 秩 r"); axes[1].set_title("LoRA 秩")
    q = [(k, v) for k, v in quant if v]
    axes[2].bar([k for k, _ in q], [v[0] for _, v in q], color=["#4c72b0", "#c44e52"])
    axes[2].set_ylim(0.75, 0.83); axes[2].set_title("量化精度")
    for ax in axes[1:]:
        for p_ in ax.patches:
            ax.text(p_.get_x() + p_.get_width() / 2, p_.get_height() + 0.002, f"{p_.get_height():.3f}", ha="center", fontsize=8)
    fig.suptitle("Qwen3-8B LoRA 消融实验（种子 42）")
    fig.tight_layout(); fig.savefig(OUT / "fig_ablation.png", dpi=200); plt.close(fig)
    for grp, items in [("训练样本量", size), ("LoRA秩", rank), ("量化", quant)]:
        for k, v in items:
            if v:
                rows.append({"消融": grp, "设置": k, "MacroF1": v[0], "准确率": v[1]})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 输出
def md(df: pd.DataFrame, digits=4) -> str:
    d = df.copy()
    for c in d.columns:
        if d[c].dtype.kind == "f":
            d[c] = d[c].map(lambda v: "" if pd.isna(v) else (f"{v:.2e}" if 0 < abs(v) < 1e-3 else f"{v:.{digits}f}"))
    head = "| " + " | ".join(d.columns) + " |\n| " + " | ".join("---" for _ in d.columns) + " |\n"
    return head + "\n".join("| " + " | ".join(str(x) for x in r) + " |" for r in d.values) + "\n"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tab = main_table()
    mc = mcnemar_all()
    bs = paired_bootstrap()
    an = anova()
    cal, curves, scaled = calibration()
    sel, rc = selective()
    abl = ablation()
    plot_models(tab); plot_reliability(curves, scaled); plot_rc(rc)

    for name, df in [("main_results", tab), ("mcnemar", mc), ("paired_bootstrap", bs),
                     ("calibration", cal), ("selective", sel), ("ablation", abl)]:
        df.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")
    (OUT / "anova.json").write_text(json.dumps(an, ensure_ascii=False, indent=2, default=str) + "\n", "utf-8")

    t = tab.drop(columns=["各次MacroF1"])
    L = ["# 统计评估结果", "", "由 `src/analysis/stats.py` 自动生成。测试集 n = 1713。", "",
         "## 表 4-1 主结果", "", "多种子模型给出均值与标准差；置信区间为种子 42 运行的 Bootstrap 95% CI。", "", md(t),
         "## 表 4-2 McNemar 检验（Holm 校正）", "", md(mc),
         "## 表 4-3 配对 Bootstrap：Macro-F1 差值", "", md(bs),
         "## 表 4-4 方差分析（各模型多个种子的 Macro-F1）", "",
         f"- 各组：{an['组']}",
         f"- 单因素 ANOVA：F = {an['ANOVA']['F']}，p = {an['ANOVA']['p']}",
         f"- Levene 方差齐性检验：W = {an['Levene']['W']}，p = {an['Levene']['p']}",
         f"- Welch ANOVA：F = {an['Welch_ANOVA']['F']}，df = ({an['Welch_ANOVA']['df1']}, {an['Welch_ANOVA']['df2']})，p = {an['Welch_ANOVA']['p']}"]
    if "ANOVA_仅LoRA大模型" in an:
        L.append(f"- 仅三个 LoRA 大模型：F = {an['ANOVA_仅LoRA大模型']['F']}，p = {an['ANOVA_仅LoRA大模型']['p']}")
    L += ["", "Tukey HSD 事后比较：", "", md(pd.DataFrame(an["Tukey_HSD"])),
          "## 表 4-5 校准指标", "", md(cal),
          "## 表 4-6 选择性预测", "", md(sel),
          "## 表 4-7 消融实验（Qwen3-8B，种子 42）", "", md(abl)]
    (OUT / "summary.md").write_text("\n".join(L), "utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
