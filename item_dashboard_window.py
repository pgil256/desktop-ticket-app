from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QMessageBox, QLabel, QDateEdit)
from PyQt6.QtCore import pyqtSignal, QDate
from PyQt6.QtGui import QColor, QPalette, QFont
from sharepoint_utils import get_sharepoint_list_items, get_sharepoint_item, update_sharepoint_item

class ItemDashboardWindow(QWidget):
    report_issue_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = ""
        self.password = ""
        self.item_id = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Item Dashboard")
        self.setFixedSize(600, 400)

        # Set default font for the entire widget
        self.setFont(QFont("Arial", 14))
        
        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        # Search section
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Item Name or Serial Number")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_item)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        # Item details section
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)

        # Buttons
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        layout.addWidget(self.save_button)

        self.report_issue_button = QPushButton("Report Issue")
        self.report_issue_button.clicked.connect(self.report_issue)
        layout.addWidget(self.report_issue_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def set_credentials(self, username, password):
        self.username = username
        self.password = password

    def search_item(self):
        search_value = self.search_input.text()
        if not search_value:
            QMessageBox.warning(self, "Error", "Please enter an Item Name or Serial Number.")
            return

        try:
            items, _, _, _ = get_sharepoint_list_items(self.username, self.password, 'Inventory', field='S/N', value=search_value)
            if not items:
                items, _, _, _ = get_sharepoint_list_items(self.username, self.password, 'Inventory', field='Item', value=search_value)
            
            if items:
                self.load_item(items[0]['ID'])
            else:
                QMessageBox.information(self, "No results", "No items found matching your search.")
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def load_item(self, item_id):
        self.item_id = item_id
        item = get_sharepoint_item(self.username, self.password, "Inventory", item_id)
        self.populate_form(item)

    def populate_form(self, item):
        # Clear existing widgets
        for i in reversed(range(self.form_layout.count())): 
            self.form_layout.itemAt(i).widget().setParent(None)

        # Add new widgets
        self.fields = {}
        for key, value in item.items():
            if key != 'ID':  # Skip the ID field
                if key == 'Date':
                    date_edit = QDateEdit()
                    date_edit.setDisplayFormat("yyyy-MM-dd")
                    if value:
                        date = QDate.fromString(value.split('T')[0], "yyyy-MM-dd")
                        date_edit.setDate(date)
                    self.form_layout.addRow(key, date_edit)
                    self.fields[key] = date_edit
                else:
                    line_edit = QLineEdit(str(value))
                    self.form_layout.addRow(key, line_edit)
                    self.fields[key] = line_edit

    def save_changes(self):
        if not self.item_id:
            QMessageBox.warning(self, "Error", "No item loaded. Please search for an item first.")
            return

        updated_properties = {}
        for key, widget in self.fields.items():
            if isinstance(widget, QDateEdit):
                updated_properties[key] = widget.date().toString("yyyy-MM-dd")
            else:
                updated_properties[key] = widget.text()

        try:
            update_sharepoint_item(self.username, self.password, "Inventory", self.item_id, updated_properties)
            QMessageBox.information(self, "Success", "Item updated successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
            
    def report_issue(self):
        if not self.item_id:
            QMessageBox.warning(self, "Error", "No item loaded. Please search for an item first.")
            return
        self.report_issue_requested.emit(str(self.item_id))

    def go_back(self):
        main_window = self.window()
        if hasattr(main_window, 'show_home'):
            main_window.show_home()
        else:
            print("Error: MainWindow does not have a show_home method")

    def clear_form(self):
        self.item_id = ""
        for i in reversed(range(self.form_layout.count())): 
            self.form_layout.itemAt(i).widget().setParent(None)
        self.fields = {}
