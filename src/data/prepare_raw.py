"""构建“未清洗”版本的 FinFE，用于量化数据泄露的影响（对照实验）。

模拟常见的直接使用做法：不去重、不处理标签冲突、不去除泄露，
训练文件随机划出 10% 作验证集，eval_list 全部 2020 条作测试集。
文本只做与清洗版相同的 NFKC 规范化，便于逐条匹配。

输出：data/processed/finfe_raw/{train,val,test}.jsonl
用法：python src/data/prepare_raw.py
"""
import json
from pathlib import Path
import unicodedata

from sklearn.model_selection import train_test_split

RAW = Path("data/raw/finfe")
OUT = Path("data/processed/finfe_raw")


def norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s).strip()


def write(path, items):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for t, y in items:
            f.write(json.dumps({"text": t, "label": int(y)}, ensure_ascii=False) + "\n")


def main():
    tr = [(norm(t), int(y)) for t, y in json.loads((RAW / "train_list.json").read_text("utf-8"))]
    ev = [(norm(t), int(y)) for t, y in json.loads((RAW / "eval_list.json").read_text("utf-8"))]
    x_tr, x_va = train_test_split(tr, test_size=0.1, stratify=[y for _, y in tr], random_state=42)
    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT / "train.jsonl", x_tr); write(OUT / "val.jsonl", x_va); write(OUT / "test.jsonl", ev)
    print(f"train {len(x_tr)}  val {len(x_va)}  test {len(ev)}")


if __name__ == "__main__":
    main()
