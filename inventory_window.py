import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
                             QLabel, QMessageBox, QApplication)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QFont
from sharepoint_utils import get_sharepoint_list_items
import logging

logging.basicConfig(level=logging.DEBUG)

class InventoryWindow(QWidget):
    item_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = ""
        self.password = ""
        self.current_page = 1
        self.total_pages = 1
        self.current_field = None
        self.current_value = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Inventory Management")
        self.setFixedSize(800, 600)
        
        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Search controls
        search_layout = QHBoxLayout()
        self.field_combo = QComboBox()
        self.field_combo.addItems(["Item", "Description", "S/N", "Location", "Condition", "Assigned To", "Date", "Cost", "Funding"])
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter search value")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_items)
        search_layout.addWidget(self.field_combo)
        search_layout.addWidget(self.value_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # Inventory table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(['Edit', 'Item', 'Description', 'S/N', 'Location', 'Condition', 'Assigned To', 'Date', 'Cost', 'Funding'])
        layout.addWidget(self.table)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_page)  # Connect prev_button to prev_page
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)  # Connect next_button to next_page
        self.page_label = QLabel()
        self.page_label.setFont(QFont("Arial", 14))
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_button)
        layout.addLayout(nav_layout)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def set_credentials(self, username, password):
        self.username = username
        self.password = password
        self.load_items()

    def load_items(self, page=1, field=None, value=None):
        items, has_next, page_number, total_pages = get_sharepoint_list_items(
            self.username, self.password, "Inventory", page_size=100, page_number=page, field=field, value=value
        )
        logging.debug(f"Loaded items: {items}")
        self.populate_table(items)
        self.current_page = page_number
        self.total_pages = total_pages
        self.current_field = field
        self.current_value = value
        self.update_navigation()

    def populate_table(self, items):
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            edit_button = QPushButton("Edit")
            if 'ID' in item:
                edit_button.clicked.connect(lambda _, item_id=item['ID']: self.edit_item(item_id))
            else:
                logging.error(f"Item does not have 'ID' key: {item}")
                continue
            self.table.setCellWidget(row, 0, edit_button)
            for col, key in enumerate(['Item', 'Description', 'S/N', 'Location', 'Condition', 'Assigned To', 'Date', 'Cost', 'Funding'], start=1):
                self.table.setItem(row, col, QTableWidgetItem(str(item.get(key, ''))))

    def update_navigation(self):
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        self.page_label.setText(f"Page {self.current_page} of {self.total_pages}")

    def search_items(self):
        field = self.field_combo.currentText()
        value = self.value_input.text()
        self.load_items(page=1, field=field, value=value)

    def prev_page(self):
        if self.current_page > 1:
            self.load_items(page=self.current_page - 1, field=self.current_field, value=self.current_value)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.load_items(page=self.current_page + 1, field=self.current_field, value=self.current_value)

    def edit_item(self, item_id):
        self.item_selected.emit(str(item_id))

    def go_back(self):
        main_window = self.window()
        if hasattr(main_window, 'show_home'):
            main_window.show_home()
        else:
            print("Error: MainWindow does not have a show_home method")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InventoryWindow()
    window.show()
    sys.exit(app.exec())
