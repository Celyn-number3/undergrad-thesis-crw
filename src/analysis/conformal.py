"""保形预测（split conformal prediction）。
只用已保存的测试集概率，不需要 GPU。测试集随机对半分成校准集和评估集，重复 R 次取平均：
  - 在校准集上计算非一致性分数 s = 1 - p(真实类)，取修正分位数 q；
  - 在评估集上输出预测集合 {k : 1 - p_k <= q}；
  - 统计覆盖率（真实类落在集合内的比例）、平均集合大小、单元素集合比例、各类别覆盖率。
两种做法：标准（边际）保形预测；按类别分别校准的 Mondrian 保形预测（保证每一类的覆盖率）。
输出 outputs/analysis/conformal.{csv,json,md}"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, ".")

PRED = Path("outputs/predictions"); OUT = Path("outputs/analysis"); OUT.mkdir(parents=True, exist_ok=True)
MODELS = {
    "TF-IDF+LR": "tfidf_lr",
    "RoBERTa-wwm-ext": "chinese-roberta-wwm-ext_s42",
    "Qwen3-8B 零样本": "Qwen3-8B_zeroshot",
    "Laya 零样本": "laya-multilingual_zeroshot_en",
    "Qwen3-8B LoRA": "Qwen3-8B_lora_r16_s42",
    "Qwen2.5-7B LoRA": "Qwen2.5-7B-Instruct_lora_r16_s42",
    "GLM-4-9B LoRA": "glm-4-9b-chat-hf_lora_r16_s42",
}
ALPHAS = [0.10, 0.05]; R = 1000; rng = np.random.default_rng(0)
CLS = ["消极", "中性", "积极"]

def qhat(scores, alpha):
    n = len(scores); k = int(np.ceil((n + 1) * (1 - alpha)))
    return np.inf if k > n else np.sort(scores)[k - 1]

def run(p, y, alpha, mondrian):
    n = len(y); res = []
    for _ in range(R):
        idx = rng.permutation(n); cal, ev = idx[: n // 2], idx[n // 2:]
        s = 1 - p[cal, y[cal]]
        if mondrian:
            q = np.array([qhat(s[y[cal] == k], alpha) for k in range(3)])
            S = (1 - p[ev]) <= q[None, :]
        else:
            S = (1 - p[ev]) <= qhat(s, alpha)
        cover = S[np.arange(len(ev)), y[ev]]; size = S.sum(1)
        res.append([cover.mean(), size.mean(), (size == 1).mean(), (size == 0).mean()]
                   + [cover[y[ev] == k].mean() for k in range(3)])
    return np.array(res).mean(0)

rows = []
for name, f in MODELS.items():
    fp = PRED / f"{f}.csv"
    if not fp.exists(): print("缺少", fp); continue
    d = pd.read_csv(fp); p = d[["p0", "p1", "p2"]].to_numpy(float); y = d.label.to_numpy()
    p = np.clip(p, 1e-12, None); p /= p.sum(1, keepdims=True)
    for a in ALPHAS:
        for mon in (False, True):
            r = run(p, y, a, mon)
            rows.append({"模型": name, "目标覆盖率": 1 - a, "方法": "按类别" if mon else "标准",
                         "覆盖率": r[0], "平均集合大小": r[1], "单元素比例": r[2], "空集比例": r[3],
                         **{f"{c}覆盖率": r[4 + i] for i, c in enumerate(CLS)}})
df = pd.DataFrame(rows).round(4)
df.to_csv(OUT / "conformal.csv", index=False, encoding="utf-8-sig")
df.to_json(OUT / "conformal.json", orient="records", force_ascii=False, indent=1)
md = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n" + "\n".join("| " + " | ".join(map(str, r)) + " |" for r in df.values)
(OUT / "conformal.md").write_text(md + "\n", "utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
print(df.to_string(index=False))
