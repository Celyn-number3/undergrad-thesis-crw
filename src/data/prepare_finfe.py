"""清洗并划分 FinFE 数据。

清洗规则（均记录在 outputs/eda/cleaning_report.json 中）：
1. 文本做 Unicode NFKC 规范化并去除首尾空白；
2. 同一文本在同一文件中重复出现：标签一致则保留一条，标签冲突则全部剔除；
3. 测试集取自 eval_list（带标签），并剔除与训练集文本相同但标签不同的样本（标注有歧义）；
4. 训练池中剔除所有与测试集文本相同的样本，避免数据泄露；
5. 训练池按标签分层，划分出 10% 作为验证集，其余为训练集。

标签含义：0 = 消极，1 = 中性，2 = 积极。
输出：data/processed/finfe/{train,val,test}.jsonl

用法：python src/data/prepare_finfe.py
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import unicodedata

from sklearn.model_selection import train_test_split

RAW = Path("data/raw/finfe")
OUT = Path("data/processed/finfe")
REPORT = Path("outputs/eda/cleaning_report.json")
LABELS = {0: "消极", 1: "中性", 2: "积极"}
SEED = 42
VAL_RATIO = 0.1


def norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s).strip()


def dedup(pairs):
    """返回 (去重后的 {text: label}, 重复条数, 冲突文本数)。"""
    group = defaultdict(list)
    for t, y in pairs:
        group[t].append(y)
    keep = {t: ys[0] for t, ys in group.items() if len(set(ys)) == 1}
    n_dup = sum(len(ys) - 1 for ys in group.values() if len(set(ys)) == 1)
    n_conflict = sum(1 for ys in group.values() if len(set(ys)) > 1)
    return keep, n_dup, n_conflict


def dist(labels):
    c = Counter(labels)
    return {LABELS[k]: c.get(k, 0) for k in LABELS}


def write_jsonl(path: Path, items):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for t, y in items:
            f.write(json.dumps({"text": t, "label": int(y)}, ensure_ascii=False) + "\n")


def main() -> None:
    raw_train = [(norm(t), int(y)) for t, y in json.loads((RAW / "train_list.json").read_text("utf-8"))]
    raw_eval = [(norm(t), int(y)) for t, y in json.loads((RAW / "eval_list.json").read_text("utf-8"))]

    tr, tr_dup, tr_conf = dedup(raw_train)
    ev, ev_dup, ev_conf = dedup(raw_eval)

    cross_same = [t for t in ev if t in tr and tr[t] == ev[t]]
    cross_diff = [t for t in ev if t in tr and tr[t] != ev[t]]
    test = {t: y for t, y in ev.items() if t not in cross_diff}
    pool = {t: y for t, y in tr.items() if t not in ev}

    texts, labels = list(pool), [pool[t] for t in pool]
    x_tr, x_va, y_tr, y_va = train_test_split(
        texts, labels, test_size=VAL_RATIO, stratify=labels, random_state=SEED)

    OUT.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT / "train.jsonl", zip(x_tr, y_tr))
    write_jsonl(OUT / "val.jsonl", zip(x_va, y_va))
    write_jsonl(OUT / "test.jsonl", sorted(test.items()))

    report = {
        "raw": {"train_list": len(raw_train), "eval_list": len(raw_eval),
                "train_list_dist": dist(y for _, y in raw_train),
                "eval_list_dist": dist(y for _, y in raw_eval)},
        "cleaning": {
            "train_duplicates_removed": tr_dup, "train_conflicting_texts_removed": tr_conf,
            "eval_duplicates_removed": ev_dup, "eval_conflicting_texts_removed": ev_conf,
            "eval_texts_also_in_train_same_label": len(cross_same),
            "eval_texts_also_in_train_diff_label_removed_from_test": len(cross_diff),
            "train_texts_removed_for_leakage": len([t for t in tr if t in ev]),
        },
        "final": {"train": len(x_tr), "val": len(x_va), "test": len(test),
                  "train_dist": dist(y_tr), "val_dist": dist(y_va),
                  "test_dist": dist(test.values())},
        "seed": SEED, "val_ratio": VAL_RATIO, "labels": LABELS,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
