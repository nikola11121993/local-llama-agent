from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass(slots=True)
class AppConfig:
    ollama_url: str = "http://127.0.0.1:11434"
    model: str = "qwen3:8b"
    context_size: int = 4096
    keep_alive: str = "5m"
    always_on_top: bool = True

    @classmethod
    def load(cls, path: Path) -> "AppConfig":
        if not path.exists():
            cfg = cls()
            path.write_text(
                json.dumps(asdict(cfg), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return cfg

        raw = json.loads(path.read_text(encoding="utf-8"))
        allowed = set(cls.__dataclass_fields__)
        data = {k: v for k, v in raw.items() if k in allowed}
        return cls(**data)
