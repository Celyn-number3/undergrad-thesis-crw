"""重复记录一致性与独立对称噪声假设下的情景推算。

思路：FinFE 中有不少文本被标注了不止一次（训练文件内部重复、训练与评估文件之间重复）。
同一文本的重复记录不一定来自独立复标；一致性只描述记录间的标签关系。

1. 一致率 p：在所有“同一文本的两次标注”配对中，标签相同的比例（按文本做 Bootstrap 求置信区间）；
2. 机会校正一致率 κ = (p − p_e) / (1 − p_e)，p_e 为按类别比例随机标注时的一致率；
3. 标注正确率 q：假设每次标注以概率 q 给出真实标签、否则等可能给出另外两类之一，
   则两次标注一致的概率为 p = q² + (1 − q)² / 2，解得 q = [1 + √(6p − 2)] / 3。
   该推算还要求给定真实类别后两次标注独立且同质，不能当作清洗后测试集的实测上限；
4. 冲突类型：不一致的配对分别发生在哪两类之间。

局限：被重复标注的文本不一定是随机样本（例如更短、更常见），结论应视为粗略估计。

用法：python -m src.analysis.label_noise
"""
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import unicodedata

import numpy as np

RAW = Path("data/raw/finfe")
OUT = Path("outputs/analysis")
NAMES = {0: "消极", 1: "中性", 2: "积极"}
RNG = np.random.default_rng(2026)


def norm(s):
    return unicodedata.normalize("NFKC", s).strip()


def pairs_stats(label_lists):
    agree = total = 0
    for ls in label_lists:
        for a, b in combinations(ls, 2):
            total += 1; agree += a == b
    return agree, total


def q_from_p(p):
    return (1 + np.sqrt(max(6 * p - 2, 0))) / 3


def main():
    ann = defaultdict(list)
    src = defaultdict(set)
    for f in ("train_list", "eval_list"):
        for t, y in json.loads((RAW / f"{f}.json").read_text("utf-8")):
            ann[norm(t)].append(int(y)); src[norm(t)].add(f)
    multi = {t: ls for t, ls in ann.items() if len(ls) >= 2}
    lists = list(multi.values())
    agree, total = pairs_stats(lists)
    p = agree / total
    # 每条文本固定取前两条记录（并非随机抽对），用于不同权重口径的敏感性描述
    p_one = np.mean([ls[0] == ls[1] for ls in lists])
    boot = []
    for _ in range(2000):
        idx = RNG.integers(0, len(lists), len(lists))
        a, t = pairs_stats([lists[i] for i in idx]); boot.append(a / t)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    # 配对两端的汇总边际，与一致率的配对加权单位一致；无固定标注者身份，
    # 因此只称机会校正一致性指标，不称标准双标注者 Cohen kappa。
    pair_endpoints = Counter()
    for ls in lists:
        for a, b in combinations(ls, 2):
            pair_endpoints.update((a, b))
    pe = sum((c / (2 * total)) ** 2 for c in pair_endpoints.values())
    kappa = (p - pe) / (1 - pe)
    prior = Counter(y for ls in ann.values() for y in ls); n = sum(prior.values())
    pe_legacy = sum((c / n) ** 2 for c in prior.values())
    conflict = Counter()
    for ls in lists:
        for a, b in combinations(ls, 2):
            if a != b:
                conflict["-".join(NAMES[x] for x in sorted((a, b)))] += 1
    lens_multi = np.mean([len(t) for t in multi]); lens_all = np.mean([len(t) for t in ann])
    cross = [ls for t, ls in multi.items() if len(src[t]) == 2]
    ca, ct = pairs_stats(cross)
    res = {
        "不同文本数": len(ann), "被标注2次及以上的文本数": len(multi), "标注配对数": total,
        "一致率p": round(p, 4), "一致率95%CI": [round(lo, 4), round(hi, 4)],
        "每文本取一对的一致率": round(float(p_one), 4),
        "跨文件重复文本内全部配对一致率": round(ca / ct, 4) if ct else None,
        "跨文件重复文本内全部配对数": ct,
        "随机一致率p_e(配对两端汇总边际)": round(pe, 4),
        "机会校正一致性K_pair(非标准Cohen_kappa)": round(kappa, 4),
        "旧全体边际口径指标(仅追溯)": round((p - pe_legacy) / (1 - pe_legacy), 4),
        "独立对称噪声假设下情景q(非实测上限)": round(q_from_p(p), 4),
        "解释限制": "原始数据无标注者ID与独立复标证明；q依赖独立、同质、均匀错标假设，不外推为清洗后测试集上限",
        "q条件于噪声模型的Bootstrap95%区间": [round(q_from_p(lo), 4), round(q_from_p(hi), 4)],
        "冲突配对类型": dict(conflict.most_common()),
        "重复文本平均长度": round(lens_multi, 1), "全部文本平均长度": round(lens_all, 1),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "label_noise.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
