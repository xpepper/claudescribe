from pathlib import Path


DATA_DIR = Path("data")
MODEL_CACHE_DIR = Path(".model_cache")


def detect_device() -> tuple[str, str]:
    """Return (device, compute_type) based on available hardware.

    - NVIDIA GPU with CUDA: ("cuda", "float16")
    - Everything else (CPU, Apple Silicon): ("cpu", "int8")

    Apple Silicon automatically uses the Apple Accelerate backend
    via CTranslate2's ARM64 optimisations — no extra config needed.
    """
    try:
        import ctranslate2  # type: ignore[import]

        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"
