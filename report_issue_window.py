from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit, QComboBox, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QFont
from sharepoint_utils import add_issue_to_sharepoint, get_user_id, get_sharepoint_item

class ReportIssueWindow(QWidget):
    issue_reported = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = ""
        self.password = ""
        self.item_id = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Report Issue")
        self.setFixedSize(600, 450)\
        
        # Set default font for the entire widget
        self.setFont(QFont("Arial", 14))

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setFont(QFont("Arial", 14))
        self.title_input.setPlaceholderText("Enter the issue title")
        form_layout.addRow("Title:", self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setFont(QFont("Arial", 14))
        self.description_input.setPlaceholderText("Enter the issue description")
        form_layout.addRow("Description:", self.description_input)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        form_layout.addRow("Priority:", self.priority_combo)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton("Submit Issue")
        self.submit_button.clicked.connect(self.submit_issue)
        layout.addWidget(self.submit_button)

        self.back_button = QPushButton("Back")

        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def set_credentials(self, username, password):
        self.username = username
        self.password = password

    def set_item_id(self, item_id):
        self.item_id = item_id
        if self.item_id:
            self.prefill_title()

    def prefill_title(self):
        try:
            item = get_sharepoint_item(self.username, self.password, "Inventory", self.item_id)
            item_name = item.get('Item', '')
            self.title_input.setText(f"Issue with {item_name}")
        except Exception as e:
            print(f"Error prefilling title: {str(e)}")

    def reset_fields(self):
        self.title_input.clear()
        self.description_input.clear()
        self.priority_combo.setCurrentIndex(0)
        self.item_id = ""

    def submit_issue(self):
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        priority = self.priority_combo.currentText()

        if not title or not description:
            QMessageBox.warning(self, "Error", "Title and description are required.")
            return

        try:
            user_id = get_user_id(self.username, self.password, self.username)

            add_issue_to_sharepoint(
                self.username, 
                self.password, 
                "Tickets", 
                title, 
                description, 
                priority, 
                user_id,
                self.item_id
            )

            QMessageBox.information(self, "Success", "Issue reported successfully!")
            self.issue_reported.emit()
            self.reset_fields()
            self.go_back()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def go_back(self):
        main_window = self.window()
        if hasattr(main_window, 'show_home'):
            main_window.show_home()
        else:
            print("Error: MainWindow does not have a show_home method")

