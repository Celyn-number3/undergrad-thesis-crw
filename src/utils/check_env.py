"""检查实验环境：Python、PyTorch、CUDA、GPU 与关键依赖。"""
import importlib
import platform
import sys


def main() -> None:
    print(f"Python      : {sys.version.split()[0]} ({platform.system()})")
    try:
        import torch

        print(f"PyTorch     : {torch.__version__}")
        print(f"CUDA 可用   : {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            p = torch.cuda.get_device_properties(0)
            print(f"GPU         : {p.name}, 显存 {p.total_memory / 1024**3:.1f} GB")
            print(f"CUDA 版本   : {torch.version.cuda}")
            print(f"bf16 支持   : {torch.cuda.is_bf16_supported()}")
    except ImportError:
        print("PyTorch     : 未安装")
    for name in ["transformers", "peft", "accelerate", "bitsandbytes", "sklearn",
                 "statsmodels", "scipy", "pandas", "matplotlib", "jieba"]:
        try:
            m = importlib.import_module(name)
            print(f"{name:<12}: {getattr(m, '__version__', 'ok')}")
        except Exception as e:  # noqa: BLE001
            print(f"{name:<12}: 不可用（{type(e).__name__}: {e}）")


if __name__ == "__main__":
    main()
