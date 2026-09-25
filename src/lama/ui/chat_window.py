from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
)

from lama.brain.ollama_client import OllamaClient


SYSTEM_PROMPT = (
    "Ты Лама — локальный помощник пользователя на его Windows-компьютере. "
    "Всегда отвечай по-русски, если пользователь сам не попросил другой язык. "
    "Отвечай понятно и по делу. "
    "Никогда не утверждай, что выполнила действие на компьютере, если инструмент "
    "действительно не вернул подтверждение успешного выполнения."
)


class ChatWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, client: OllamaClient, messages: list[dict[str, str]]) -> None:
        super().__init__()
        self.client = client
        self.messages = list(messages)

    def run(self) -> None:
        try:
            reply = self.client.chat(self.messages)
            self.finished.emit(reply.content)
        except Exception as exc:
            self.failed.emit(str(exc))


class ChatWindow(QWidget):
    thinking_changed = Signal(bool)

    def __init__(self, client: OllamaClient) -> None:
        super().__init__()
        self.client = client
        self.thread: QThread | None = None
        self.worker: ChatWorker | None = None
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        self.setWindowTitle("Лама — локальный помощник")
        self.resize(640, 520)

        layout = QVBoxLayout(self)

        self.status = QLabel("Локальная модель готова")
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Спроси Ламу…")
        self.input.returnPressed.connect(self.send_message)

        self.button = QPushButton("Отправить")
        self.button.clicked.connect(self.send_message)

        layout.addWidget(self.status)
        layout.addWidget(self.chat)
        layout.addWidget(self.input)
        layout.addWidget(self.button)

    def send_message(self) -> None:
        text = self.input.text().strip()
        if not text or self.thread is not None:
            return

        self.input.clear()
        self.chat.append(f"<b>Я:</b> {text}<br>")
        self.messages.append({"role": "user", "content": text})

        self.button.setEnabled(False)
        self.input.setEnabled(False)
        self.status.setText("Лама думает…")
        self.thinking_changed.emit(True)
        QApplication.processEvents()

        self.thread = QThread(self)
        self.worker = ChatWorker(self.client, self.messages)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_reply)
        self.worker.failed.connect(self._on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup_thread)
        self.thread.start()

    def _on_reply(self, answer: str) -> None:
        self.messages.append({"role": "assistant", "content": answer})
        safe = answer.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.chat.append(f"<b>🦙 Лама:</b><br>{safe}<br>")
        self._set_idle()

    def _on_error(self, error: str) -> None:
        safe = error.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.chat.append(f"<b>Ошибка:</b> {safe}<br>")
        self.status.setText("Ошибка связи с Ollama")
        self.thinking_changed.emit(False)
        self.button.setEnabled(True)
        self.input.setEnabled(True)

    def _set_idle(self) -> None:
        self.status.setText("Локальная модель готова")
        self.thinking_changed.emit(False)
        self.button.setEnabled(True)
        self.input.setEnabled(True)
        self.input.setFocus()

    def _cleanup_thread(self) -> None:
        if self.worker is not None:
            self.worker.deleteLater()
        if self.thread is not None:
            self.thread.deleteLater()
        self.worker = None
        self.thread = None
