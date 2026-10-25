from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from .config import get_app_icon

class ManageDNSServersDialog(QDialog):
    def __init__(self, servers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage DNS Servers")
        self.setWindowIcon(get_app_icon())
        self.resize(420, 320)

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget(self)
        for server in servers:
            item = QListWidgetItem(server)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)

        btns = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")
        btns.addWidget(self.add_button)
        btns.addWidget(self.remove_button)
        btns.addStretch()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        btns.addWidget(self.save_button)
        btns.addWidget(self.cancel_button)
        layout.addLayout(btns)

        self.add_button.clicked.connect(self.add_server)
        self.remove_button.clicked.connect(self.remove_server)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def add_server(self):
        item = QListWidgetItem("")
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.list_widget.addItem(item)
        self.list_widget.editItem(item)

    def remove_server(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def get_servers(self):
        return [
            self.list_widget.item(i).text().strip()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).text().strip()
        ]


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Dialog)
        from .version import __version__
        self.setWindowTitle("About TrayNSLookup")
        self.setWindowIcon(get_app_icon())
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        body = QHBoxLayout()
        icon = QLabel(self)
        icon.setPixmap(get_app_icon().pixmap(64, 64))
        icon.setFixedSize(72, 72)
        icon.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        body.addWidget(icon)
        details = QVBoxLayout()
        self.title_label = QLabel(f"<b>TrayNSLookup {__version__}</b>", self)
        font = self.title_label.font()
        font.setPointSize(font.pointSize() + 3)
        self.title_label.setFont(font)
        details.addWidget(self.title_label)
        details.addWidget(QLabel("A desktop DNS lookup utility with system tray integration.", self))
        details.addWidget(QLabel("Created by evil1dwk", self))
        self.links_label = QLabel(
            '<a href="https://github.com/evil1dwk/TrayNSLookup">GitHub repository</a>  '
            '<a href="https://github.com/evil1dwk/TrayNSLookup/issues">Report an issue</a>', self)
        self.links_label.setOpenExternalLinks(True)
        self.links_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        details.addWidget(self.links_label)
        body.addLayout(details)
        layout.addLayout(body)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons, alignment=Qt.AlignmentFlag.AlignRight)
