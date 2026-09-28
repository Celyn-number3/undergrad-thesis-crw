"""下载 FinFE 原始数据（BBT-CFLEB 基准，中文金融社交媒体情感三分类）。

公开版本与论文描述不同：
- train_list.json：16157 条带标签样本
- eval_list.json ：2020 条带标签样本
- problem_list.json：2020 条无标签样本（排行榜测试集，标签未公开，本研究不使用）

用法：python src/data/download_finfe.py
"""
import json
from pathlib import Path
import urllib.request

PATH = "supersymmetry-technologies/BBT-FinCUGE-Applications/main/FinCUGE_Publish/finfe/"
# 依次尝试多个下载源（国内网络常无法访问 raw.githubusercontent.com）
MIRRORS = [
    "https://raw.githubusercontent.com/" + PATH,
    "https://cdn.jsdelivr.net/gh/" + PATH.replace("/main/", "@main/", 1),
    "https://ghfast.top/https://raw.githubusercontent.com/" + PATH,
]
FILES = ["train_list.json", "eval_list.json", "problem_list.json"]
OUT = Path("data/raw/finfe")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for f in FILES:
        dst = OUT / f
        if dst.exists() and dst.stat().st_size > 0:
            print(f"已存在，跳过：{dst}")
            continue
        for base in MIRRORS:
            try:
                print(f"下载 {base + f} ...")
                urllib.request.urlretrieve(base + f, dst)
                json.loads(dst.read_text("utf-8"))  # 校验是合法 JSON
                print(f"  -> {dst}（{dst.stat().st_size / 1024:.0f} KB）")
                break
            except Exception as e:  # noqa: BLE001
                print(f"  失败：{type(e).__name__}: {e}")
                dst.unlink(missing_ok=True)
        else:
            raise SystemExit(f"所有下载源均失败：{f}")


if __name__ == "__main__":
    main()
