from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QFont

from sharepoint_utils import test_sharepoint_connection

class LoginWindow(QWidget):
    login_successful = pyqtSignal(str, str)

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

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            test_sharepoint_connection(username, password)
            self.login_successful.emit(username, password)
        except ValueError as e:
            QMessageBox.warning(self, "Login Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {str(e)}")
