"""E2 预训练小模型微调：中文 BERT / RoBERTa。

在验证集上按 Macro-F1 早停，保存测试集逐条三类概率。
每个模型用多个随机种子重复，供方差分析使用。

用法：
  python -m src.baselines.bert --model hfl/chinese-roberta-wwm-ext --seeds 42 43 44
模型默认从 hf-mirror.com 下载（国内网络）。
"""
import argparse
import os
import time

os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
# 部分电脑的 SSL_CERT_FILE 环境变量指向不存在的文件，会导致下载失败
if os.environ.get("SSL_CERT_FILE") and not os.path.exists(os.environ["SSL_CERT_FILE"]):
    os.environ.pop("SSL_CERT_FILE")

import numpy as np  # noqa: E402
import torch  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,  # noqa: E402
                          get_linear_schedule_with_warmup, set_seed)

from src.utils.metrics import load_split, save_run  # noqa: E402

MAX_LEN = 96


def batches(tok, df, bs, shuffle, seed=0):
    idx = np.arange(len(df))
    if shuffle:
        np.random.default_rng(seed).shuffle(idx)
    for i in range(0, len(idx), bs):
        sub = df.iloc[idx[i:i + bs]]
        enc = tok(list(sub["text"]), padding=True, truncation=True, max_length=MAX_LEN, return_tensors="pt")
        enc["labels"] = torch.tensor(sub["label"].values)
        yield enc


@torch.no_grad()
def predict(model, tok, df, bs=128):
    model.eval()
    out = []
    for b in batches(tok, df, bs, False):
        b = {k: v.cuda() for k, v in b.items() if k != "labels"}
        with torch.autocast("cuda", dtype=torch.bfloat16):
            out.append(torch.softmax(model(**b).logits.float(), -1).cpu().numpy())
    return np.concatenate(out)


def run(model_name, seed, epochs, lr, bs, patience):
    set_seed(seed)
    tr, va, te = load_split("train"), load_split("val"), load_split("test")
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3).cuda()
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    steps = epochs * ((len(tr) + bs - 1) // bs)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    best, best_state, bad, t0 = -1, None, 0, time.time()
    for ep in range(epochs):
        model.train()
        for b in batches(tok, tr, bs, True, seed * 100 + ep):
            b = {k: v.cuda() for k, v in b.items()}
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss = model(**b).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sch.step(); opt.zero_grad()
        f1 = f1_score(va["label"], predict(model, tok, va).argmax(1), average="macro")
        print(f"  epoch {ep + 1}: val macro-F1 = {f1:.4f}", flush=True)
        if f1 > best:
            best, bad = f1, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best_state)
    probs = predict(model, tok, te)
    short = model_name.split("/")[-1]
    res = save_run(f"{short}_s{seed}", te, probs, {
        "base_model": model_name, "seed": seed, "lr": lr, "batch_size": bs,
        "best_val_macro_f1": round(best, 4), "epochs_run": ep + 1,
        "train_seconds": round(time.time() - t0, 1)})
    print(f"[{short} seed={seed}] test acc={res['accuracy']} macro-F1={res['macro_f1']}", flush=True)
    del model; torch.cuda.empty_cache()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="hfl/chinese-roberta-wwm-ext")
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44])
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--patience", type=int, default=2)
    a = ap.parse_args()
    for s in a.seeds:
        run(a.model, s, a.epochs, a.lr, a.bs, a.patience)


if __name__ == "__main__":
    main()
