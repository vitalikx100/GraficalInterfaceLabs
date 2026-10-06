import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog

WINDOW_TITLE = "ЛР №1. Выполнил 6132 Старыгин Виталий"
WINDOW_SIZE = (1280, 720)
BG_OPACITY = 0.5
MARGINS = (20, 20, 20, 20)
BUTTON_SPACING = 15
BTN_MIN_HEIGHT = 35
FILE_FILTER = "Изображения (*.png *.jpg *.jpeg)"

LABEL_TEXT_DEFAULT = "Надпись"
LABEL_TEXT_CHANGED = "Изменилась"

LABEL_STYLE = """
    font-size: 32px;
    font-weight: bold;
    color: black;
    padding: 10px;
"""

BUTTON_STYLE = """
    font-size: 18px;
    color: black;
    padding: 10px 30px;
    border: 2px solid black;
    background-color: white;
    border-radius: 5px;
"""


class BgWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_img = None
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_img(self, pixmap):
        self.bg_img = pixmap
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.bg_img and not self.bg_img.isNull():
            scaled = self.bg_img.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

            x_offset = (self.width() - scaled.width()) // 2
            y_offset = (self.height() - scaled.height()) // 2

            painter.setOpacity(BG_OPACITY)
            painter.drawPixmap(x_offset, y_offset, scaled)
        else:
            painter.fillRect(self.rect(), Qt.GlobalColor.white)


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(*WINDOW_SIZE)

        self.bg_widget = BgWidget(self)
        self.setCentralWidget(self.bg_widget)

        main_layout = QVBoxLayout(self.bg_widget)
        main_layout.setContentsMargins(*MARGINS)

        self.label = QLabel(LABEL_TEXT_DEFAULT)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(LABEL_STYLE)
        main_layout.addWidget(self.label, stretch=1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(BUTTON_SPACING)
        main_layout.addLayout(buttons_layout)

        self.btn1 = QPushButton("Кнопка1")
        self.btn1.setMinimumHeight(BTN_MIN_HEIGHT)
        self.btn1.setStyleSheet(BUTTON_STYLE)
        self.btn1.clicked.connect(self.change_text)
        buttons_layout.addWidget(self.btn1)

        self.btn2 = QPushButton("Кнопка2")
        self.btn2.setMinimumHeight(BTN_MIN_HEIGHT)
        self.btn2.setStyleSheet(BUTTON_STYLE)
        self.btn2.clicked.connect(self.open_img)
        buttons_layout.addWidget(self.btn2)

    def change_text(self):
        if self.label.text() == LABEL_TEXT_DEFAULT:
            self.label.setText(LABEL_TEXT_CHANGED)
        else:
            self.label.setText(LABEL_TEXT_DEFAULT)

    def open_img(self):
        file_path, _ = QFileDialog.getOpenFileName(self, filter=FILE_FILTER)

        pixmap = QPixmap(file_path)
        self.bg_widget.set_img(pixmap)

        screen = QApplication.primaryScreen().availableGeometry()

        img_width = pixmap.width()
        img_height = pixmap.height()

        if img_width > screen.width() or img_height > screen.height():
            self.showMaximized()
        else:
            self.resize(img_width, img_height)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())
