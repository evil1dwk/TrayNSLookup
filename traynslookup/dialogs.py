from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QDialogButtonBox, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from .config import get_app_icon

class ManageDNSServersDialog(QDialog):
    def __init__(self, servers, parent=None, names=None):
        super().__init__(parent)
        self.setWindowTitle("Manage DNS Servers")
        self.setWindowIcon(get_app_icon())
        self.resize(520, 340)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(['Name (optional)', 'IP address'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        for server in servers:
            self._add_row((names or {}).get(server, ''), server)
        layout.addWidget(self.table)
        buttons = QHBoxLayout()
        for text, callback in [('Add', self.add_server), ('Remove', self.remove_server),
                               ('Save', self.accept), ('Cancel', self.reject)]:
            button = QPushButton(text)
            button.clicked.connect(callback)
            buttons.addWidget(button)
        layout.addLayout(buttons)

    def _add_row(self, name='', address=''):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(name))
        self.table.setItem(row, 1, QTableWidgetItem(address))

    def add_server(self):
        self._add_row()
        self.table.editItem(self.table.item(self.table.rowCount() - 1, 0))

    def remove_server(self):
        for row in sorted({i.row() for i in self.table.selectionModel().selectedRows()}, reverse=True):
            self.table.removeRow(row)

    def _rows(self):
        return [(self.table.item(row, 0).text().strip(), self.table.item(row, 1).text().strip())
                for row in range(self.table.rowCount())]

    def accept(self):
        import ipaddress
        addresses = []
        try:
            for name, address in self._rows():
                if not name and not address:
                    continue
                ipaddress.ip_address(address)
                if address in addresses:
                    raise ValueError('Each DNS server address must be unique.')
                addresses.append(address)
        except ValueError as exc:
            QMessageBox.warning(self, 'Invalid DNS server', str(exc))
            return
        super().accept()

    def get_servers(self):
        return [address for name, address in self._rows() if address]

    def get_names(self):
        return {address: name for name, address in self._rows() if address and name}


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
