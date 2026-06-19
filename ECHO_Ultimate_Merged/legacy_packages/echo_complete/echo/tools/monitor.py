from core.exceptions import ToolException

def monitor() -> str:
    """Return CPU, RAM and GPU usage statistics."""
    try:
        import psutil
        data = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_percent": psutil.virtual_memory().percent,
        }
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            data["gpu"] = [{"name": g.name, "load": g.load, "memoryUtil": g.memoryUtil} for g in gpus]
        except Exception:
            data["gpu"] = []
        import json
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ToolException(f"Erro na ferramenta monitor: {e}") from e
