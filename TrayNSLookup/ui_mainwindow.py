from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QPlainTextEdit,
    QListWidget, QListWidgetItem, QMessageBox, QStyle
)
from datetime import datetime
from .dns_worker import DNSLookupThread
from .config import save_config, get_app_icon, get_gear_icon


class MainWindow(QMainWindow):
    def __init__(self, cfg, open_manage_servers_callback):
        super().__init__()
        self.cfg = cfg
        self.open_manage_servers_callback = open_manage_servers_callback

        # Basic window setup
        self.setWindowTitle("Tray NSLookup")
        self.setWindowIcon(get_app_icon())
        self.resize(760, 540)
        self._restore_window_geometry()

        # Tabs container
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.lookup_tab = QWidget()
        self.tabs.addTab(self.lookup_tab, "Lookup")
        self._build_lookup_tab()

        self.history_tab = QWidget()
        self.tabs.addTab(self.history_tab, "History")
        self._build_history_tab()

        self._refresh_history_view()

    def _build_lookup_tab(self):
        layout = QVBoxLayout(self.lookup_tab)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Domain:"))
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("example.com")
        self.domain_input.returnPressed.connect(self._run_lookup)
        row1.addWidget(self.domain_input)

        row1.addWidget(QLabel("Record Type:"))
        self.record_combo = QComboBox()
        self.record_combo.addItems(["A", "AAAA", "CNAME", "MX", "TXT", "NS", "PTR"])
        row1.addWidget(self.record_combo)

        self.run_button = QPushButton("Run Lookup")
        self.run_button.clicked.connect(self._run_lookup)
        row1.addWidget(self.run_button)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("DNS Server:"))
        self.server_combo = QComboBox()
        self._reload_server_combo()
        row2.addWidget(self.server_combo)

        self.edit_servers_button = QPushButton()
        self.edit_servers_button.setToolTip("Edit DNS servers")
        self.edit_servers_button.setIcon(get_gear_icon(self.style()))
        self.edit_servers_button.clicked.connect(self._open_manage_servers)
        row2.addWidget(self.edit_servers_button)

        row2.addStretch()
        layout.addLayout(row2)

        # Results panel
        self.results = QPlainTextEdit()
        self.results.setReadOnly(True)
        self.results.setPlaceholderText("Results will appear here...")
        layout.addWidget(self.results)

    def _build_history_tab(self):
        layout = QVBoxLayout(self.history_tab)
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self._open_selected_history)
        layout.addWidget(self.history_list)

        btns = QHBoxLayout()
        self.view_button = QPushButton("View Result")
        self.view_button.clicked.connect(self._open_selected_history)
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_history_view)
        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self._clear_history)
        btns.addWidget(self.view_button)
        btns.addStretch()
        btns.addWidget(self.refresh_button)
        btns.addWidget(self.clear_button)
        layout.addLayout(btns)

    def _run_lookup(self):
        domain = self.domain_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "Error", "Please enter a domain name.")
            return

        record_type = self.record_combo.currentText()
        server_text = self.server_combo.currentText()
        server = None if server_text == "(system default)" else server_text

        self.results.clear()
        self.results.appendPlainText(f"Querying {domain} ({record_type}) via {server or 'system default'}...\n")

        self.worker = DNSLookupThread(domain, record_type, server)
        self.worker.finished.connect(self._display_result)
        self.worker.start()

    def _display_result(self, query, result):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_result = f"{timestamp}\nQuery: {query}\n\n{result}"
        self.results.setPlainText(full_result)
        self.cfg.setdefault("history", []).append({"query": query, "result": full_result})
        save_config(self.cfg)
        self._refresh_history_view()

    def _refresh_history_view(self):
        self.history_list.clear()
        for entry in reversed(self.cfg.get("history", [])):
            first_line = entry["result"].split("\n", 1)[0]
            item = QListWidgetItem(f"{first_line} — {entry['query']}")
            self.history_list.addItem(item)

    def _open_selected_history(self):
        item = self.history_list.currentItem()
        if not item:
            return
        idx = self.history_list.row(item)
        history = self.cfg.get("history", [])
        if not history:
            return
        original_index = len(history) - 1 - idx
        selected = history[original_index]
        self.results.setPlainText(selected["result"])
        self.tabs.setCurrentWidget(self.lookup_tab)

    def _clear_history(self):
        if QMessageBox.question(self, "Clear History", "Delete all saved results?") == QMessageBox.StandardButton.Yes:
            self.cfg["history"] = []
            save_config(self.cfg)
            self._refresh_history_view()

    def _reload_server_combo(self):
        self.server_combo.clear()
        self.server_combo.addItem("(system default)")
        self.server_combo.addItems(self.cfg.get("dns_servers", []))

    def _open_manage_servers(self):
        new_servers = self.open_manage_servers_callback(self.cfg.get("dns_servers", []))
        if new_servers:
            self.cfg["dns_servers"] = new_servers
            save_config(self.cfg)
            self._reload_server_combo()
            QMessageBox.information(self, "DNS Servers Updated", "Changes saved successfully.")

    def _restore_window_geometry(self):
        win = self.cfg.get("window", {})
        size = win.get("size")
        pos = win.get("pos")
        if size:
            self.resize(*size)
        if pos:
            self.move(*pos)

    def _save_window_geometry(self):
        self.cfg["window"] = {
            "size": [self.width(), self.height()],
            "pos": [self.x(), self.y()]
        }
        save_config(self.cfg)

    def closeEvent(self, event):
        self._save_window_geometry()
        super().closeEvent(event)
