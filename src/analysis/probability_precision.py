"""历史概率的截断敏感性，不用更换 epsilon 冒充恢复丢失的概率精度。
运行：python -m src.analysis.probability_precision
仅读取历史 CSV，新增精度诊断产物，不修改预测文件或拟合模型。
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from src.analysis.stats import CALIB, MAIN, seed42, temp_scale, softmax, ece_mce


def main():
    rows = []
    for name in CALIB:
        d = pd.read_csv(seed42(MAIN[name]))
        y, p = d.label.to_numpy(), d[["p0", "p1", "p2"]].to_numpy(float)
        truth = p[np.arange(len(y)), y]
        for floor in [1e-6, 1e-8, 1e-12]:
            z = np.log(np.clip(p, floor, 1)); scaled = np.zeros_like(p); temperatures = []
            for tr, te in StratifiedKFold(5, shuffle=True, random_state=0).split(p, y):
                t = temp_scale(z[tr], y[tr]); temperatures.append(t)
                scaled[te] = softmax(z[te] / t)
            rows.append({"模型": name, "截断下限": floor,
                         "真实类概率为零条数": int((truth == 0).sum()),
                         "NLL": float(-np.log(np.clip(truth, floor, 1)).mean()),
                         "温度T均值": float(np.mean(temperatures)),
                         "交叉拟合后NLL": float(-np.log(scaled[np.arange(len(y)), y]).mean()),
                         "交叉拟合后ECE": ece_mce(y, scaled)[0]})
    out = Path("outputs/analysis"); out.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(out / "probability_precision.csv", index=False, encoding="utf-8-sig")
    (out / "probability_precision.json").write_text(json.dumps({
        "解释": "历史六位小数概率不能还原高精度logits；各截断值只作敏感性分析，不判定任一值为真实值。新save_run不再舍入，但未重写历史CSV。",
        "results": rows}, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(frame.round(6).to_string(index=False))


if __name__ == "__main__":
    main()
