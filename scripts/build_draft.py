"""合并摘要与各章为完整初稿，并把 [作者, 年份] 引用改为按出现顺序的数字编号 [n]。
用法（仓库根目录）：python scripts/build_draft.py  -> docs/mcp-thesis-draft.md
各章 md 保持作者-年份写法，方便单独修改；每次改完重新运行本脚本即可。"""
import re, io
D = "docs/"
PARTS = ["mcp-thesis-abstract.md", "mcp-thesis-ch1.md", "mcp-thesis-ch2.md",
         "mcp-thesis-ch3-ch4.md", "mcp-thesis-ch5.md"]
# 引用键 -> 文献综述参考文献表中的编号（或直接给出完整条目）
KEYS = {
    "沈艳等, 2019": 1, "游家兴和吴静, 2012": 2, "段江娇等, 2017": 3, "部慧等, 2018": 4,
    "Tetlock, 2007": 6, "Loughran 和 McDonald, 2011": 7, "Malo 等, 2014": 8,
    "Vaswani 等, 2017": 9, "Devlin 等, 2019": 10, "Araci, 2019": 11, "Cui 等, 2021": 12,
    "Brown 等, 2020": 13, "Kaplan 等, 2020": 14, "Yang 等, 2025": 15, "Wu 等, 2023": 16,
    "Yang 等, 2023": 17, "Lu 等, 2023": 18, "Hu 等, 2022": 19, "Dettmers 等, 2023": 20,
    "Zhang 等, 2023": 22, "Fatemi 和 Hu, 2023": 25, "Paredes Amorin 等, 2025": 26,
    "McNemar, 1947": 29, "Dietterich, 1998": 30, "Efron 和 Tibshirani, 1993": 31,
    "Holm, 1979": 32, "Guo 等, 2017": 33, "Balabanov 和 Linander, 2024": 34,
    "Chow, 1970": 35, "Geifman 和 El-Yaniv, 2017": 36,
    "Chen 等, 2023": "Chen W, Wang Q, Long Z, et al. DISC-FinLLM: A Chinese financial large language model "
                     "based on multiple experts fine-tuning[J]. arXiv preprint arXiv:2310.15205, 2023.",
}
KEYS.update({
    "Vovk 等, 2005": "Vovk V, Gammerman A, Shafer G. Algorithmic learning in a random world[M]. New York: Springer, 2005.",
    "Angelopoulos 和 Bates, 2023": "Angelopoulos A N, Bates S. Conformal prediction: A gentle introduction[J]. Foundations and Trends in Machine Learning, 2023, 16(4): 494-591.",
    "ConvAI Innovations, 2026": "ConvAI Innovations. Laya: open-weight System One decision models[EB/OL]. (2026)[2026-09-30]. https://huggingface.co/convaiinnovations/laya.",
})
NARR = {"Cui 等（2021）": "Cui 等, 2021"}  # 叙述式引用

lit = io.open(D + "mcp-literature-review.md", encoding="utf-8").read()
LIT = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"^\[(\d+)\]\s*(.+)$", lit, re.M)}

text = "\n\n".join(io.open(D + p, encoding="utf-8").read().strip() for p in PARTS)
text = re.sub(r"\n## 参考文献（本章引用）.*?(?=\n# |\Z)", "\n", text, flags=re.S)  # 去掉章内文献表

order = {}
def num(key):
    key = key.strip()
    if key not in KEYS:
        raise SystemExit(f"未知引用：{key}")
    return order.setdefault(key, len(order) + 1)

def fmt(ns):
    ns = sorted(set(ns)); out = []; i = 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1: j += 1
        out.append(f"{ns[i]}-{ns[j]}" if j - i >= 2 else ",".join(map(str, ns[i:j + 1])))
        i = j + 1
    return "[" + ",".join(out) + "]"

for k, v in NARR.items():
    text = text.replace(k, k.split("（")[0] + "[" + v + "]")
text = re.sub(r"\s?\[([^\[\]\n]*?(?:19|20)\d\d[^\[\]\n]*?)\]",
              lambda m: fmt([num(k) for k in m.group(1).split(";")]), text)

refs = []
for key, n in sorted(order.items(), key=lambda x: x[1]):
    v = KEYS[key]; refs.append(f"[{n}] " + (LIT[v] if isinstance(v, int) else v))
text += "\n\n# 参考文献\n\n" + "\n\n".join(refs) + "\n"
io.open(D + "mcp-thesis-draft.md", "w", encoding="utf-8", newline="\n").write(text)
print(f"引用文献 {len(refs)} 篇")
