from __future__ import annotations

class PermissionError(Exception):
    pass

class PermissionManager:
    def __init__(self, config):
        self.config = config
        self.levels = config.permissions or {}

    def require(self, capability: str, level: str = "safe"):
        allowed = self.levels.get(capability, "safe")
        order = ["off", "safe", "limited", "full"]
        if order.index(allowed) < order.index(level):
            raise PermissionError(f"capability={capability} requires {level}, current={allowed}")
