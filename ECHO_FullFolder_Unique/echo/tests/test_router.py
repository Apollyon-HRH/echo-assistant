from pathlib import Path

from core.config import AppConfig
from core.model import ModelRouter

def test_routing():
    cfg = AppConfig.load(Path("config.yaml"))
    router = ModelRouter(cfg)
    assert router.choose("crie um código python").reason == "code"
