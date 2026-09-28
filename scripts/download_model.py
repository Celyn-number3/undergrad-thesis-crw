"""断点续传 + 多连接并行下载 ModelScope 模型（网络不稳定时比 modelscope download 可靠）。

- 大文件切成 4 段同时下载，每段断线后自动从断点续传，不会从头重下；
- 下载完成后按 ModelScope 提供的文件大小与 SHA256 校验。

用法：python scripts/download_model.py Qwen/Qwen3-8B [Qwen/Qwen2.5-7B-Instruct ...]
"""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
import sys
import threading
import time
from pathlib import Path

if os.environ.get("SSL_CERT_FILE") and not os.path.exists(os.environ["SSL_CERT_FILE"]):
    os.environ.pop("SSL_CERT_FILE")
import requests  # noqa: E402

API = "https://modelscope.cn/api/v1/models/{m}/repo/files?Recursive=true&Revision=master"
URL = "https://modelscope.cn/models/{m}/resolve/master/{p}"
SKIP = (".pth", ".bin")
N_CONN = 4
lock = threading.Lock()


def log(msg: str) -> None:
    with lock:
        print(msg, flush=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def get_range(url: str, part: Path, start: int, end: int, progress: dict, key: int) -> None:
    """把 [start, end] 字节下载到 part 文件，支持断点续传。"""
    need = end - start + 1
    while True:
        done = part.stat().st_size if part.exists() else 0
        progress[key] = done
        if done >= need:
            return
        try:
            r = requests.get(url, headers={"Range": f"bytes={start + done}-{end}"}, stream=True, timeout=(15, 60))
            if r.status_code != 206:
                raise IOError(f"HTTP {r.status_code}")
            with part.open("ab") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
                    progress[key] += len(chunk)
        except Exception as e:  # noqa: BLE001
            log(f"    段 {key} 中断（{type(e).__name__}），5 秒后续传")
            time.sleep(5)


def fetch(model: str, item: dict, out: Path) -> None:
    dst = out / item["Path"]
    size, digest = int(item.get("Size", 0)), item.get("Sha256", "")
    if dst.exists() and dst.stat().st_size == size:
        log(f"  [已完成] {item['Path']}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.with_name(dst.name + ".incomplete").unlink(missing_ok=True)  # modelscope 残留，无法续传
    url = URL.format(m=model, p=item["Path"])
    n = N_CONN if size > 50_000_000 else 1
    step = (size + n - 1) // n
    parts = [dst.with_name(f"{dst.name}.part{i}") for i in range(n)]
    progress = {}
    stop = threading.Event()

    def reporter():
        last, t = 0, time.time()
        while not stop.wait(30):
            cur = sum(progress.values())
            log(f"  {item['Path']}: {cur / 1e9:.2f}/{size / 1e9:.2f} GB, {(cur - last) / (time.time() - t) / 1e6:.1f} MB/s")
            last, t = cur, time.time()

    threading.Thread(target=reporter, daemon=True).start()
    with ThreadPoolExecutor(n) as ex:
        for i in range(n):
            ex.submit(get_range, url, parts[i], i * step, min(size, (i + 1) * step) - 1, progress, i)
    stop.set()
    with dst.with_name(dst.name + ".tmp").open("wb") as f:
        for p in parts:
            with p.open("rb") as g:
                while chunk := g.read(1 << 24):
                    f.write(chunk)
    tmp = dst.with_name(dst.name + ".tmp")
    if digest and sha256(tmp) != digest:
        log(f"  [校验失败] 重新下载 {item['Path']}")
        tmp.unlink()
        for p in parts:
            p.unlink()
        return fetch(model, item, out)
    for p in parts:
        p.unlink()
    tmp.replace(dst)
    log(f"  [OK] {item['Path']}（SHA256 校验通过）")


def main() -> None:
    for model in sys.argv[1:]:
        out = Path("models") / model.split("/")[-1]
        files = requests.get(API.format(m=model), timeout=30).json()["Data"]["Files"]
        files = [f for f in files if f["Type"] == "blob" and not f["Path"].endswith(SKIP)
                 and not f["Path"].startswith("original/")]
        log(f"== {model}：{len(files)} 个文件，共 {sum(int(f['Size']) for f in files) / 1e9:.1f} GB")
        for f in sorted(files, key=lambda x: int(x["Size"])):
            fetch(model, f, out)
        log(f"== {model} 下载完成")
    log("DOWNLOAD_DONE")


if __name__ == "__main__":
    main()
