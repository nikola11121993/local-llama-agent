from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from lama.brain.ollama_client import OllamaClient
from lama.core.config import AppConfig
from lama.core.logging_setup import setup_logging
from lama.memory.store import MemoryStore
from lama.ui.chat_window import ChatWindow
from lama.ui.desktop_llama import DesktopLlama


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    root = project_root()
    setup_logging(root / "logs")

    config = AppConfig.load(root / "config.json")
    MemoryStore(root / "data" / "lama.sqlite3")

    client = OllamaClient(
        base_url=config.ollama_url,
        model=config.model,
        context_size=config.context_size,
        keep_alive=config.keep_alive,
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    if not client.healthcheck():
        QMessageBox.warning(
            None,
            "Лама",
            "Ollama не отвечает на 127.0.0.1:11434. "
            "Запусти Ollama и перезапусти Ламу.",
        )

    chat = ChatWindow(client)
    llama = DesktopLlama(chat)
    llama.show()

    return app.exec()
