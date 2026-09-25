from __future__ import annotations

from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QMenu

from lama.ui.chat_window import ChatWindow


class DesktopLlama(QWidget):
    def __init__(self, chat_window: ChatWindow) -> None:
        super().__init__()
        self.chat_window = chat_window
        self.drag_position = QPoint()
        self.state = "idle"

        flags = Qt.FramelessWindowHint | Qt.Tool
        if True:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(180, 180)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, 180, 180)
        self.label.setStyleSheet("font-size: 104px; background: transparent;")
        self.set_state("idle")

        self.chat_window.thinking_changed.connect(
            lambda thinking: self.set_state("thinking" if thinking else "idle")
        )

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 30, screen.bottom() - self.height() - 30)

        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self._idle_animation)
        self.idle_timer.start(6000)

    def set_state(self, state: str) -> None:
        self.state = state
        icons = {
            "idle": "🦙",
            "thinking": "🦙💭",
            "eating": "🦙🥕",
            "sleeping": "🦙💤",
            "attention": "🦙❗",
        }
        self.label.setText(icons.get(state, "🦙"))
        self.setToolTip(f"Лама: {state}")

    def _idle_animation(self) -> None:
        if self.state == "idle":
            self.label.setText("🦙" if self.label.text() != "🦙" else "🦙✨")

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.chat_window.show()
            self.chat_window.raise_()
            self.chat_window.activateWindow()

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)

        open_chat = QAction("Открыть чат", self)
        open_chat.triggered.connect(self.chat_window.show)
        menu.addAction(open_chat)

        eat = QAction("Дать морковку", self)
        eat.triggered.connect(self._eat)
        menu.addAction(eat)

        menu.addSeparator()

        quit_action = QAction("Закрыть Ламу", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        menu.exec(event.globalPos())

    def _eat(self) -> None:
        self.set_state("eating")
        QTimer.singleShot(2500, lambda: self.set_state("idle"))
