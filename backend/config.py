import platform
from pathlib import Path


DATA_DIR = Path("data")
MODEL_CACHE_DIR = Path(".model_cache")


def is_apple_silicon() -> bool:
    return platform.system() == "Darwin" and platform.processor() == "arm"


def detect_device() -> tuple[str, str]:
    """Return (device, compute_type) based on available hardware.

    Priority:
    1. Apple Silicon + mlx-whisper installed → ("mlx", "mlx")
    2. NVIDIA GPU with CUDA 12.3+            → ("cuda", "float16")
    3. Everything else (CPU)                  → ("cpu", "int8")

    Note: mlx-whisper is an optional dependency, only installable on
    Apple Silicon Macs. Windows/Linux users are unaffected.
    """
    if is_apple_silicon():
        try:
            import mlx_whisper  # type: ignore[import]  # noqa: F401
            return "mlx", "mlx"
        except ImportError:
            pass

    try:
        import ctranslate2  # type: ignore[import]

        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass

    return "cpu", "int8"
