"""核对论文中的数字是否能在实验结果文件中找到。
从 docs/mcp-thesis-draft.md 提取所有小数和百分数，与 outputs/ 下所有 json/csv 中的数值
（按 2～4 位小数及百分数四舍五入）比对，列出找不到来源的数字及其上下文，供人工检查。
用法：python scripts/check_numbers.py > outputs/analysis/number_check.txt"""
import json, re, glob, csv, math
vals = set()
def add(x):
    try: x = float(x)
    except: return
    if math.isnan(x) or math.isinf(x): return
    for v in (x, abs(x), x * 100, abs(x) * 100):
        for d in (1, 2, 3, 4): vals.add(round(v, d))
def walk(o):
    if isinstance(o, dict): [walk(v) for v in o.values()]
    elif isinstance(o, list): [walk(v) for v in o]
    elif isinstance(o, (int, float)): add(o)
    elif isinstance(o, str):
        for m in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", o): add(m)
for f in glob.glob("outputs/**/*.json", recursive=True):
    try: walk(json.load(open(f, encoding="utf-8")))
    except Exception: pass
for f in glob.glob("outputs/**/*.csv", recursive=True):
    if "predictions" in f: continue
    for row in csv.reader(open(f, encoding="utf-8-sig")):
        for c in row:
            for m in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", c): add(m)
for f in glob.glob("outputs/**/*.md", recursive=True):
    for m in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", open(f, encoding="utf-8").read()): add(m)

text = open("docs/mcp-thesis-draft.md", encoding="utf-8").read()
body = text.split("\n# 参考文献")[0]
miss = []; total = 0
for ln, line in enumerate(body.split("\n"), 1):
    if line.startswith("!["): continue
    for m in re.finditer(r"(?<![\w.])(\d*\.\d+)(%?)", line):
        s = m.group(1); total += 1
        x = float(s); d = len(s.split(".")[1])
        if round(x, d) in vals or round(x * 100, max(d - 2, 0)) in vals: continue
        miss.append((ln, s + m.group(2), line[max(0, m.start() - 30): m.end() + 20]))
print(f"共检查 {total} 个小数，未找到来源 {len(miss)} 个：")
for ln, s, ctx in miss: print(f"行{ln:5d}  {s:>8}  …{ctx}…")
