from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QPlainTextEdit,
    QListWidget, QListWidgetItem, QMessageBox, QStyle, QCheckBox, QToolButton,
    QMenu, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSplitter, QScrollArea, QApplication
)
from PyQt6.QtCore import Qt
from datetime import datetime
from .dialogs import AboutDialog
from .dns_worker import DNSLookupThread
from .config import save_config, get_app_icon, get_gear_icon


class MainWindow(QMainWindow):
    def __init__(self, cfg, open_manage_servers_callback):
        super().__init__()
        self._lookup_running = False
        self.cfg = cfg
        self.open_manage_servers_callback = open_manage_servers_callback

        # Basic window setup
        self.setWindowTitle("Tray NSLookup")
        self.setWindowIcon(get_app_icon())
        self.resize(760, 540)
        self._restore_window_geometry()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self._build_query_controls(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.lookup_tab = QWidget()
        self.tabs.addTab(self.lookup_tab, "Results")
        self._build_results_tab()
        self.history_tab = QWidget()
        self.tabs.addTab(self.history_tab, "History")
        self._build_history_tab()
        self._refresh_history_view()

        QApplication.instance().aboutToQuit.connect(self._wait_for_lookup)

        footer = QHBoxLayout()
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self._show_about)
        footer.addWidget(self.about_button)
        footer.addStretch()
        layout.addLayout(footer)

    def _build_query_controls(self, layout):
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Domain / IP:"))
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("example.com or IPv4 / IPv6 address")
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

        self.compare_check = QCheckBox("Compare servers")
        self.compare_check.toggled.connect(lambda checked: self.server_combo.setEnabled(not checked))
        row2.addWidget(self.compare_check)
        self.compare_menu = QMenu(self)
        self.choose_servers_button = QToolButton()
        self.choose_servers_button.setText("Select servers")
        self.choose_servers_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.choose_servers_button.setMenu(self.compare_menu)
        self._reload_compare_servers()
        row2.addWidget(self.choose_servers_button)
        row2.addStretch()
        layout.addLayout(row2)

    def _show_about(self):
        if not hasattr(self, "_about_dialog"):
            self._about_dialog = AboutDialog(self)
        self._about_dialog.show()
        self._about_dialog.raise_()
        self._about_dialog.activateWindow()

    def _build_results_tab(self):
        layout = QVBoxLayout(self.lookup_tab)
        self.results = QPlainTextEdit()
        self.results.setReadOnly(True)
        self.results.setPlaceholderText("Results will appear here...")
        self.result_stack = QStackedWidget()
        self.result_stack.addWidget(self.results)
        self.structured_results = QWidget()
        self.structured_layout = QVBoxLayout(self.structured_results)
        self.result_stack.addWidget(self.structured_results)
        layout.addWidget(self.result_stack)
        buttons = QHBoxLayout()
        buttons.addStretch()
        self.clear_results_button = QPushButton("Clear Results")
        self.clear_results_button.clicked.connect(self._clear_results)
        buttons.addWidget(self.clear_results_button)
        layout.addLayout(buttons)

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

    def _reload_compare_servers(self):
        previous = {action.data() for action in getattr(self, 'server_actions', []) if action.isChecked()}
        first = not hasattr(self, 'server_actions')
        self.compare_menu.clear()
        self.server_actions = []
        for server in [None, *dict.fromkeys(self.cfg.get('dns_servers', []))]:
            action = self.compare_menu.addAction(server or "System default")
            action.setCheckable(True)
            action.setData(server)
            action.setChecked(first or server in previous)
            self.server_actions.append(action)

    def _clear_results(self):
        self.result_tables = []
        self.results.clear()
        self.result_stack.setCurrentWidget(self.results)
        while self.structured_layout.count():
            item = self.structured_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _run_lookup(self):
        if self._lookup_running:
            return
        domain = self.domain_input.text().strip()
        if not domain:
            QMessageBox.warning(self, "Error", "Please enter a domain name or IP address.")
            return
        record_type = self.record_combo.currentText()
        if self.compare_check.isChecked():
            servers = [a.data() for a in self.server_actions if a.isChecked()]
            if len(servers) < 2:
                QMessageBox.warning(self, "Compare servers", "Select at least two DNS servers.")
                return
        else:
            servers = [None if self.server_combo.currentIndex() == 0 else self.server_combo.currentText()]
        from .dns_worker import prepare_query
        name, kind = prepare_query(domain, record_type)
        self.record_combo.setCurrentText(kind)
        self.tabs.setCurrentWidget(self.lookup_tab)
        self._clear_results()
        self.results.setPlainText(f"Querying {domain} ({kind}) as {name}...")
        self._lookup_running = True
        self.run_button.setEnabled(False)
        self.worker = DNSLookupThread(domain, kind, servers)
        self.worker.completed.connect(self._display_result)
        self.worker.finished.connect(self._lookup_finished)
        self.worker.start()

    def _lookup_finished(self):
        self._lookup_running = False
        self.run_button.setEnabled(True)

    def _wait_for_lookup(self):
        if self._lookup_running:
            self.worker.wait()

    def _display_result(self, lookup):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [timestamp, f"Query: {lookup['query']}", lookup['comparison']]
        for result in lookup['results']:
            lines.append(f"{result['requested_server']} — {result['server']} ({result['elapsed_ms']} ms)")
            lines.append(result['error'] or '\n'.join(
                f"{r['name']} {r['ttl']} {r['type']} {r['value']}" for r in result['records']))
        full_result = '\n'.join(lines)
        self._render_lookup(lookup)
        self.cfg.setdefault("history", []).append(dict(query=lookup['query'], result=full_result, lookup=lookup))
        save_config(self.cfg)
        self._refresh_history_view()

    def _render_lookup(self, lookup):
        self._clear_results()
        summary = QLabel(f"Query: {lookup['query']}" + (' — ' + lookup['comparison'] if lookup.get('comparison') else ''))
        summary.setTextFormat(Qt.TextFormat.PlainText)
        summary.setWordWrap(True)
        self.structured_layout.addWidget(summary)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.result_tables = []
        for result in lookup['results']:
            panel = QWidget()
            panel.setMinimumWidth(360)
            layout = QVBoxLayout(panel)
            label = QLabel(f"{result['requested_server']}\nResponding server: {result['server'] or 'Unavailable'}"
                           f"\n{result['record_type']} — {result['elapsed_ms']} ms")
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            layout.addWidget(label)
            if result['error']:
                error = QLabel(result['error'])
                error.setTextFormat(Qt.TextFormat.PlainText)
                error.setWordWrap(True)
                layout.addWidget(error)
            table = QTableWidget(len(result['records']), 4)
            table.setHorizontalHeaderLabels(['Name', 'Type', 'Value', 'TTL (s)'])
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            table.setColumnWidth(0, 110)
            table.setColumnWidth(1, 50)
            table.setColumnWidth(3, 65)
            table.verticalHeader().hide()
            for row, record in enumerate(result['records']):
                for col, key in enumerate(('name', 'type', 'value', 'ttl')):
                    item = QTableWidgetItem(str(record[key]))
                    item.setToolTip(str(record[key]))
                    table.setItem(row, col, item)
            layout.addWidget(table)
            self.result_tables.append(table)
            splitter.addWidget(panel)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(splitter)
        self.structured_layout.addWidget(scroll)
        self.result_stack.setCurrentWidget(self.structured_results)

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
        if 'lookup' in selected:
            self._render_lookup(selected['lookup'])
        else:
            self._clear_results()
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
        if new_servers is not None:
            self.cfg["dns_servers"] = new_servers
            save_config(self.cfg)
            self._reload_server_combo()
            self._reload_compare_servers()
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
