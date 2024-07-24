import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from login_window import LoginWindow
from home_window import HomeWindow
from inventory_window import InventoryWindow
from item_dashboard_window import ItemDashboardWindow
from report_issue_window import ReportIssueWindow

class CenteredWidget(QWidget):
    def __init__(self, child_widget):
        super().__init__()
        self.child_widget = child_widget

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        h_layout = QHBoxLayout()
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(self.child_widget)

        layout.addLayout(h_layout)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setGeometry(100, 100, 800, 600)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#e0f7fa"))
        self.setPalette(palette)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.login_window = CenteredWidget(LoginWindow(self))
        self.home_window = CenteredWidget(HomeWindow(self))
        self.inventory_window = CenteredWidget(InventoryWindow(self))
        self.item_dashboard_window = CenteredWidget(ItemDashboardWindow(self))
        self.report_issue_window = CenteredWidget(ReportIssueWindow(self))

        self.central_widget.addWidget(self.login_window)
        self.central_widget.addWidget(self.home_window)
        self.central_widget.addWidget(self.inventory_window)
        self.central_widget.addWidget(self.item_dashboard_window)
        self.central_widget.addWidget(self.report_issue_window)

        self.central_widget.setCurrentWidget(self.login_window)

        # Connect signals
        self.login_window.child_widget.login_successful.connect(self.on_login_successful)
        self.home_window.child_widget.show_inventory_requested.connect(self.show_inventory)
        self.home_window.child_widget.show_submit_ticket_requested.connect(self.show_submit_ticket)
        self.home_window.child_widget.show_item_dashboard_requested.connect(self.show_item_dashboard)
        self.inventory_window.child_widget.item_selected.connect(self.show_item_dashboard_with_item)
        self.item_dashboard_window.child_widget.report_issue_requested.connect(self.show_report_issue)

    def on_login_successful(self, username, password):
        self.username = username
        self.password = password
        self.item_dashboard_window.child_widget.set_credentials(username, password)
        self.report_issue_window.child_widget.set_credentials(username, password)
        self.show_home()

    def show_home(self):
        self.central_widget.setCurrentWidget(self.home_window)

    def show_inventory(self):
        self.inventory_window.child_widget.set_credentials(self.username, self.password)
        self.central_widget.setCurrentWidget(self.inventory_window)

    def show_submit_ticket(self):
        self.report_issue_window.child_widget.reset_fields()
        self.central_widget.setCurrentWidget(self.report_issue_window)

    def show_item_dashboard(self):
        self.item_dashboard_window.child_widget.clear_form()
        self.central_widget.setCurrentWidget(self.item_dashboard_window)

    def show_item_dashboard_with_item(self, item_id):
        self.item_dashboard_window.child_widget.load_item(item_id)
        self.central_widget.setCurrentWidget(self.item_dashboard_window)

    def show_report_issue(self, item_id):
        self.report_issue_window.child_widget.set_credentials(self.username, self.password)
        self.report_issue_window.child_widget.set_item_id(item_id)
        self.central_widget.setCurrentWidget(self.report_issue_window)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

    
