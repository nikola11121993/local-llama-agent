from __future__ import annotations

from dataclasses import dataclass
import requests


@dataclass(slots=True)
class OllamaReply:
    content: str


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        context_size: int = 4096,
        keep_alive: str = "5m",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.context_size = context_size
        self.keep_alive = keep_alive

    def healthcheck(self, timeout: float = 3.0) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=timeout)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def chat(self, messages: list[dict[str, str]], timeout: float = 300.0) -> OllamaReply:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "keep_alive": self.keep_alive,
                "options": {
                    "num_ctx": self.context_size,
                },
            },
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return OllamaReply(content=payload["message"]["content"])
