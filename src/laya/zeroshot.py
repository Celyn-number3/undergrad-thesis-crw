"""Laya（开源 System One 决策模型）零样本评估。
直接用 choice 问题给出三类选项及判定标准，读取三类概率，按 save_run 统一格式保存。
用法：python -m src.laya.zeroshot [--prompt zh|en]"""
import argparse, sys, time
import numpy as np
sys.path.insert(0, ".")
import laya
from src.utils.metrics import load_split, save_run, LABELS

PROMPTS = {
    "zh": {"instructions": "这条股民评论表达的情感倾向是什么？",
           "criteria": {"消极": "看空、下跌、亏损、抱怨、失望、嘲讽",
                        "中性": "客观陈述事实或数据、提问、闲聊，没有明显的看多或看空情绪",
                        "积极": "看多、上涨、盈利、乐观、满意、称赞"}},
    "en": {"instructions": "What sentiment does this Chinese stock-forum comment express?",
           "criteria": {"消极": "negative: bearish, falling prices, losses, complaints, disappointment, sarcasm",
                        "中性": "neutral: objective facts or numbers, questions, chit-chat, no clear bullish or bearish view",
                        "积极": "positive: bullish, rising prices, profits, optimism, satisfaction, praise"}},
}

def ece(y, p, bins=15):
    conf, pred = p.max(1), p.argmax(1); e = 0.0
    for lo, hi in zip(np.linspace(0, 1, bins + 1)[:-1], np.linspace(0, 1, bins + 1)[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any(): e += m.mean() * abs((pred[m] == y[m]).mean() - conf[m].mean())
    return e

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--prompt", default="zh", choices=PROMPTS)
    a = ap.parse_args()
    agent = laya.load("models/laya/multilingual")
    q = {"sentiment": {"type": "choice", **PROMPTS[a.prompt]}}
    test = load_split("test"); probs = np.zeros((len(test), 3)); t0 = time.time()
    for i, t in enumerate(test.text):
        pr = agent.predict({"body": t}, q)["answers"]["sentiment"]["probabilities"]
        probs[i] = [pr[l] for l in LABELS]
    probs /= probs.sum(1, keepdims=True)
    sec = time.time() - t0
    m = save_run(f"laya-multilingual_zeroshot_{a.prompt}", test, probs,
                 {"ECE": round(ece(test.label.values, probs), 4), "seconds": round(sec, 1),
                  "mean_conf": round(float(probs.max(1).mean()), 4)})
    print(m)

if __name__ == "__main__":
    main()
