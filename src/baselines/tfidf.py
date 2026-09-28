"""E1 传统基线：TF-IDF（字符 1-3 元组）+ 逻辑回归 / 线性 SVM。

超参数 C 在验证集上按 Macro-F1 选择，再用训练集重新拟合，在测试集上评估。
SVM 没有原生概率，用 sigmoid 校准（CalibratedClassifierCV）得到三类概率。

用法：python -m src.baselines.tfidf
"""
import json
import time

from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.pipeline import make_pipeline
from sklearn.svm import LinearSVC

from src.utils.metrics import load_split, save_run

SEED = 42
GRID = [0.1, 0.3, 1, 3, 10, 30, 100]


def build(kind: str, c: float):
    vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 3), min_df=2, sublinear_tf=True)
    if kind == "lr":
        clf = LogisticRegression(C=c, max_iter=3000, class_weight="balanced", random_state=SEED)
    else:
        clf = CalibratedClassifierCV(LinearSVC(C=c, class_weight="balanced", random_state=SEED), cv=5)
    return make_pipeline(vec, clf)


def main() -> None:
    tr, va, te = load_split("train"), load_split("val"), load_split("test")
    results = []
    for kind, name in [("lr", "tfidf_lr"), ("svm", "tfidf_svm")]:
        scores = {}
        for c in GRID:
            m = build(kind, c).fit(tr["text"], tr["label"])
            scores[c] = f1_score(va["label"], m.predict(va["text"]), average="macro")
        best = max(scores, key=scores.get)
        t0 = time.time()
        model = build(kind, best).fit(tr["text"], tr["label"])
        probs = model.predict_proba(te["text"])
        res = save_run(name, te, probs, {"best_C": best, "val_macro_f1_by_C": {str(k): round(v, 4) for k, v in scores.items()},
                                          "train_seconds": round(time.time() - t0, 2)})
        results.append(res)
        print(json.dumps({k: res[k] for k in ["model", "accuracy", "macro_f1", "per_class_f1", "best_C"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
