"""E3/E4 大模型实验：零样本、少样本提示与 LoRA 微调。

核心做法：把分类问题写成对话，让模型回答“消极 / 中性 / 积极”。
不让模型自由生成文字，而是读取回答第一个位置上三个标签词的 logits，
经 softmax 得到三类概率。这样做有两点好处：
1. 不会出现答非所问、无法解析的输出；
2. 得到连续的概率，后续可以做校准（ECE）和选择性预测（AURC）分析。

LoRA 训练的损失就是这个位置上正确标签词的交叉熵，
等价于只在答案词上计算损失的监督微调（SFT）。

用法示例：
  python -m src.llm.run_llm --model models/Qwen3-8B --mode zeroshot
  python -m src.llm.run_llm --model models/Qwen3-8B --mode fewshot --shots 3
  python -m src.llm.run_llm --model models/Qwen3-8B --mode lora --seed 42 --rank 16
  python -m src.llm.run_llm --model models/Qwen3-8B --mode lora --load-4bit      # QLoRA
  python -m src.llm.run_llm --model models/Qwen3-8B --mode lora --train-size 1000  # 样本量消融
"""
import argparse
import json
import math
import os
import time
from pathlib import Path

if os.environ.get("SSL_CERT_FILE") and not os.path.exists(os.environ["SSL_CERT_FILE"]):
    os.environ.pop("SSL_CERT_FILE")

import numpy as np  # noqa: E402
import torch  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed  # noqa: E402

from src.utils.metrics import load_split, save_run  # noqa: E402

LABEL_WORDS = ["消极", "中性", "积极"]
SYSTEM = "你是一名金融文本情感分析助手。"
INSTRUCTION = ("请判断下面这条股民评论的情感倾向，只能回答“消极”“中性”“积极”三者之一，不要输出其他内容。\n"
               "评论：{text}")


# ---------------------------------------------------------------- 提示构造
def build_messages(text: str, shots: list[tuple[str, int]] | None = None) -> list[dict]:
    msgs = [{"role": "system", "content": SYSTEM}]
    for t, y in shots or []:
        msgs += [{"role": "user", "content": INSTRUCTION.format(text=t)},
                 {"role": "assistant", "content": LABEL_WORDS[y]}]
    msgs.append({"role": "user", "content": INSTRUCTION.format(text=text)})
    return msgs


def render(tok, msgs) -> str:
    kw = dict(tokenize=False, add_generation_prompt=True)
    try:  # Qwen3：关闭“思考模式”，直接作答
        return tok.apply_chat_template(msgs, enable_thinking=False, **kw)
    except TypeError:
        return tok.apply_chat_template(msgs, **kw)


def label_token_ids(tok) -> list[int]:
    ids = [tok.encode(w, add_special_tokens=False)[0] for w in LABEL_WORDS]
    assert len(set(ids)) == 3, f"三个标签词的首个 token 相同，无法区分：{ids}"
    return ids


def pick_shots(train, k_per_class: int, seed: int) -> list[tuple[str, int]]:
    """每类随机抽 k 条作为示例，并打乱顺序。"""
    rng = np.random.default_rng(seed)
    shots = []
    for y in range(3):
        sub = train[train["label"] == y]
        for i in rng.choice(len(sub), k_per_class, replace=False):
            shots.append((sub.iloc[i]["text"], y))
    rng.shuffle(shots)
    return shots


# ---------------------------------------------------------------- 前向计算
def last_logits(model, tok, prompts: list[str], ids: list[int]) -> torch.Tensor:
    enc = tok(prompts, return_tensors="pt", padding=True).to(model.device)
    out = model(**enc, logits_to_keep=1)
    return out.logits[:, -1, :].float()  # (B, V)


@torch.no_grad()
def predict_probs(model, tok, texts, ids, shots=None, bs=32) -> np.ndarray:
    model.eval()
    res = []
    for i in range(0, len(texts), bs):
        prompts = [render(tok, build_messages(t, shots)) for t in texts[i:i + bs]]
        logits = last_logits(model, tok, prompts, ids)[:, ids]
        res.append(torch.softmax(logits, -1).cpu().numpy())
    return np.concatenate(res)


# ---------------------------------------------------------------- 模型加载
def load_model(path: str, load_4bit: bool):
    tok = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    tok.padding_side = "left"  # 左填充，保证最后一个位置就是答案位置
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    kw = dict(dtype=torch.bfloat16, device_map={"": 0}, trust_remote_code=True)
    if load_4bit:
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(path, **kw)
    return tok, model


# ---------------------------------------------------------------- LoRA 训练
def train_lora(model, tok, ids, tr, va, a):
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    if a.load_4bit:
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    else:
        model.gradient_checkpointing_enable()
        model.enable_input_require_grads()
    cfg = LoraConfig(r=a.rank, lora_alpha=2 * a.rank, lora_dropout=0.05, task_type="CAUSAL_LM",
                     target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"])
    model = get_peft_model(model, cfg)
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_all = sum(p.numel() for p in model.parameters())
    print(f"  可训练参数 {n_train / 1e6:.1f}M / 总参数 {n_all / 1e9:.2f}B（{100 * n_train / n_all:.2f}%）", flush=True)

    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=a.lr, weight_decay=0.0)
    steps_per_epoch = math.ceil(len(tr) / a.bs)
    total = steps_per_epoch * a.epochs
    warm = int(0.05 * total)
    sch = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda s: (s + 1) / max(1, warm) if s < warm else max(0.0, (total - s) / max(1, total - warm)))
    target_map = torch.tensor(ids, device=model.device)
    best, best_state, history, step = -1.0, None, [], 0
    rng = np.random.default_rng(a.seed)
    for ep in range(a.epochs):
        model.train()
        order = rng.permutation(len(tr))
        run_loss = 0.0
        for b in range(steps_per_epoch):
            idx = order[b * a.bs:(b + 1) * a.bs]
            sub = tr.iloc[idx]
            loss_sum = 0.0
            for j in range(0, len(sub), a.micro_bs):  # 梯度累积
                mb = sub.iloc[j:j + a.micro_bs]
                prompts = [render(tok, build_messages(t)) for t in mb["text"]]
                logits = last_logits(model, tok, prompts, ids)
                y = target_map[torch.tensor(mb["label"].values, device=model.device)]
                loss = torch.nn.functional.cross_entropy(logits, y) * len(mb) / len(sub)
                loss.backward()
                loss_sum += loss.item()
            torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
            opt.step(); sch.step(); opt.zero_grad(set_to_none=True)
            run_loss += loss_sum; step += 1
            if step % 50 == 0:
                print(f"  epoch {ep + 1} step {step}/{total} loss {run_loss / 50:.4f}", flush=True)
                run_loss = 0.0
        vp = predict_probs(model, tok, list(va["text"]), ids, bs=a.eval_bs)
        f1 = f1_score(va["label"], vp.argmax(1), average="macro")
        history.append(round(f1, 4))
        print(f"  epoch {ep + 1}: val macro-F1 = {f1:.4f}", flush=True)
        if f1 > best:
            best = f1
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items() if "lora_" in k}
    model.load_state_dict(best_state, strict=False)
    return model, best, history, n_train


# ---------------------------------------------------------------- 主程序
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="本地模型目录，如 models/Qwen3-8B")
    ap.add_argument("--mode", choices=["zeroshot", "fewshot", "lora"], required=True)
    ap.add_argument("--shots", type=int, default=1, help="少样本：每类示例数")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--bs", type=int, default=16, help="有效批大小")
    ap.add_argument("--micro-bs", type=int, default=16)
    ap.add_argument("--eval-bs", type=int, default=32)
    ap.add_argument("--train-size", type=int, default=0, help="只用前 N 条训练样本（0 = 全部）")
    ap.add_argument("--load-4bit", action="store_true", help="4-bit 量化加载（QLoRA）")
    ap.add_argument("--limit", type=int, default=0, help="调试：只评估前 N 条测试样本")
    ap.add_argument("--tag", default="", help="结果文件名后缀")
    a = ap.parse_args()

    set_seed(a.seed)
    tr, va, te = load_split("train"), load_split("val"), load_split("test")
    if a.train_size:
        tr = tr.sample(n=a.train_size, random_state=a.seed).reset_index(drop=True)
    if a.limit:
        te = te.iloc[:a.limit].reset_index(drop=True)
    name = Path(a.model).name
    t0 = time.time()
    tok, model = load_model(a.model, a.load_4bit)
    ids = label_token_ids(tok)
    print(f"[{name}] 标签词 token id：{dict(zip(LABEL_WORDS, ids))}", flush=True)
    print("提示示例：\n" + render(tok, build_messages(te.iloc[0]["text"])), flush=True)

    extra = {"base_model": name, "mode": a.mode, "seed": a.seed, "load_4bit": a.load_4bit}
    shots = None
    if a.mode == "fewshot":
        shots = pick_shots(tr, a.shots, a.seed)
        extra["shots_per_class"] = a.shots
        run = f"{name}_fewshot{a.shots}_s{a.seed}"
    elif a.mode == "zeroshot":
        run = f"{name}_zeroshot"
    else:
        model, best, hist, n_train = train_lora(model, tok, ids, tr, va, a)
        extra.update({"rank": a.rank, "lr": a.lr, "epochs": a.epochs, "batch_size": a.bs,
                      "train_size": len(tr), "best_val_macro_f1": round(best, 4),
                      "val_macro_f1_history": hist, "trainable_params": n_train,
                      "peak_gpu_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2)})
        run = f"{name}_lora_r{a.rank}" + ("_4bit" if a.load_4bit else "") + \
              (f"_n{a.train_size}" if a.train_size else "") + f"_s{a.seed}"
    run += a.tag
    probs = predict_probs(model, tok, list(te["text"]), ids, shots, bs=a.eval_bs)
    extra["seconds"] = round(time.time() - t0, 1)
    extra["peak_gpu_gb_total"] = round(torch.cuda.max_memory_allocated() / 1e9, 2)
    res = save_run(run, te, probs, extra)
    print(json.dumps({k: res[k] for k in ["model", "accuracy", "macro_f1", "per_class_f1", "seconds"]},
                     ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
