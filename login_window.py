from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QFont

from sharepoint_utils import connect_sharepoint

class LoginWindow(QWidget):
    login_successful = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login")
        self.setFixedSize(450, 200)

        # Set default font for the entire widget
        self.setFont(QFont("Arial", 14))

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        prompt = QLabel("Sign in with your work account in the Microsoft browser window.")
        prompt.setWordWrap(True)
        layout.addWidget(prompt)

        self.login_button = QPushButton("Sign in with Microsoft")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        self.login_button.setEnabled(False)
        try:
            sharepoint = connect_sharepoint()
        except ValueError as exc:
            QMessageBox.warning(self, "Sign-in error", str(exc))
        else:
            self.login_successful.emit(sharepoint)
        finally:
            self.login_button.setEnabled(True)
