from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

class HomeWindow(QWidget):
    show_inventory_requested = pyqtSignal()
    show_submit_ticket_requested = pyqtSignal()
    show_item_dashboard_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Set window title and size
        self.setWindowTitle("Home Window")
        self.setFixedSize(450, 300)

        # Set default font for the entire widget
        self.setFont(QFont("Arial", 16))

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        submit_ticket_button = QPushButton("Submit Ticket")
        submit_ticket_button.clicked.connect(self.show_submit_ticket_requested.emit)
        layout.addWidget(submit_ticket_button)

        item_dashboard_button = QPushButton("Item Dashboard")
        item_dashboard_button.clicked.connect(self.show_item_dashboard_requested.emit)
        layout.addWidget(item_dashboard_button)

        inventory_button = QPushButton("Inventory List")
        inventory_button.clicked.connect(self.show_inventory_requested.emit)
        layout.addWidget(inventory_button)


        self.setLayout(layout)

