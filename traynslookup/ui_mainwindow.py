from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QPlainTextEdit,
    QListWidget, QListWidgetItem, QMessageBox, QStyle, QToolButton,
    QMenu, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSplitter, QScrollArea, QApplication, QFileDialog,
    QCheckBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QBrush
from copy import deepcopy
from .comparisons import server_statuses, compare_history
from datetime import datetime
from pathlib import Path
from .result_tools import RECORD_TYPES, export_result, format_text, history_matches
from .dialogs import AboutDialog
from .dns_worker import DNSLookupThread
from .config import save_config, get_app_icon, get_gear_icon


class MainWindow(QMainWindow):
    def __init__(self, cfg, open_manage_servers_callback):
        super().__init__()
        self._comparison_baseline = None
        self.current_lookup = None
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

    def _build_query_controls(self, layout):
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Domain / IP:"))
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("example.com or IPv4 / IPv6 address")
        self.domain_input.returnPressed.connect(self._run_lookup)
        row1.addWidget(self.domain_input)

        row1.addWidget(QLabel("Record Type:"))
        self.record_combo = QComboBox()
        self.record_combo.addItems(RECORD_TYPES)
        row1.addWidget(self.record_combo)

        self.run_button = QPushButton("Run Lookup")
        self.run_button.clicked.connect(self._run_lookup)
        row1.addWidget(self.run_button)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("DNS Server:"))
        self.compare_menu = QMenu(self)
        self.choose_servers_button = QToolButton()
        self.choose_servers_button.setText("Select servers")
        self.choose_servers_button.setFixedWidth(220)
        self.choose_servers_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.choose_servers_button.setMenu(self.compare_menu)
        self._reload_compare_servers()
        row2.addWidget(self.choose_servers_button)
        self.edit_servers_button = QPushButton()
        self.edit_servers_button.setToolTip("Edit DNS servers")
        self.edit_servers_button.setIcon(get_gear_icon(self.style()))
        self.edit_servers_button.clicked.connect(self._open_manage_servers)
        row2.addWidget(self.edit_servers_button)
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
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self._show_about)
        buttons.addWidget(self.about_button)
        buttons.addStretch()
        self.copy_selected_button = QPushButton("Copy Selected")
        self.copy_selected_button.clicked.connect(self._copy_selected)
        buttons.addWidget(self.copy_selected_button)
        self.copy_all_button = QPushButton("Copy All")
        self.copy_all_button.clicked.connect(self._copy_all)
        buttons.addWidget(self.copy_all_button)
        self.export_button = QToolButton()
        self.export_button.setText("Export")
        self.export_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        export_menu = QMenu(self.export_button)
        for label, kind in [('Text (.txt)', 'txt'), ('CSV (.csv)', 'csv'), ('JSON (.json)', 'json')]:
            export_menu.addAction(label).triggered.connect(lambda checked=False, kind=kind: self._export_results(kind))
        self.export_button.setMenu(export_menu)
        buttons.addWidget(self.export_button)
        self.clear_results_button = QPushButton("Clear Results")
        self.clear_results_button.clicked.connect(self._clear_results)
        buttons.addWidget(self.clear_results_button)
        layout.addLayout(buttons)
        self._set_output_actions(False)

    def _build_history_tab(self):
        layout = QVBoxLayout(self.history_tab)
        filters = QHBoxLayout()
        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Search domain / IP")
        self.history_server_filter = QLineEdit()
        self.history_server_filter.setPlaceholderText("Filter DNS server")
        self.history_type_filter = QComboBox()
        self.history_type_filter.addItems(['All types', *RECORD_TYPES])
        for widget in (self.history_search, self.history_server_filter, self.history_type_filter):
            filters.addWidget(widget)
        layout.addLayout(filters)
        dates = QHBoxLayout()
        self.history_date_filter = QCheckBox("Date range")
        dates.addWidget(self.history_date_filter)
        self.history_from = QDateEdit(QDate.currentDate().addDays(-30))
        self.history_to = QDateEdit(QDate.currentDate())
        for label, widget in [('From', self.history_from), ('To', self.history_to)]:
            widget.setCalendarPopup(True)
            widget.setDisplayFormat('yyyy-MM-dd')
            widget.setEnabled(False)
            dates.addWidget(QLabel(label))
            dates.addWidget(widget)
            widget.dateChanged.connect(self._refresh_history_view)
        self.history_date_filter.toggled.connect(self.history_from.setEnabled)
        self.history_date_filter.toggled.connect(self.history_to.setEnabled)
        self.history_date_filter.toggled.connect(self._refresh_history_view)
        self.history_reset_button = QPushButton("Reset Filters")
        self.history_reset_button.clicked.connect(self._reset_history_filters)
        dates.addWidget(self.history_reset_button)
        dates.addStretch()
        layout.addLayout(dates)
        self.history_search.textChanged.connect(self._refresh_history_view)
        self.history_server_filter.textChanged.connect(self._refresh_history_view)
        self.history_type_filter.currentTextChanged.connect(self._refresh_history_view)
        self.history_count = QLabel()
        layout.addWidget(self.history_count)
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
        self.history_about_button = QPushButton("About")
        self.history_about_button.clicked.connect(self._show_about)
        btns.addWidget(self.history_about_button)
        btns.addStretch()
        self.rerun_button = QPushButton("Run Again")
        self.rerun_button.clicked.connect(self._rerun_selected_history)
        self.compare_history_button = QPushButton("Compare with Current")
        self.compare_history_button.clicked.connect(self._compare_selected_history)
        btns.addWidget(self.compare_history_button)
        btns.addWidget(self.rerun_button)
        btns.addWidget(self.view_button)
        btns.addWidget(self.refresh_button)
        btns.addWidget(self.clear_button)
        layout.addLayout(btns)

    def _server_label(self, server):
        if server is None:
            return 'System default'
        name = self.cfg.get('dns_server_names', {}).get(server, '')
        return f'{name} — {server}' if name else server

    def _reload_compare_servers(self):
        available = [None, *dict.fromkeys(self.cfg.get('dns_servers', []))]
        # None identifies the system resolver in the JSON settings as null.
        saved = self.cfg.get('selected_dns_servers', available)
        previous = set(saved) if isinstance(saved, list) else set(available)
        self.compare_menu.clear()
        self.server_actions = []
        for server in available:
            action = self.compare_menu.addAction(self._server_label(server))
            action.setCheckable(True)
            action.setData(server)
            action.setChecked(server in previous)
            action.toggled.connect(self._save_server_selection)
            self.server_actions.append(action)
        self._save_server_selection()

    def _save_server_selection(self):
        selected = [a.data() for a in self.server_actions if a.isChecked()]
        self.cfg['selected_dns_servers'] = selected
        if not selected:
            label = 'Select servers'
        elif len(selected) == 1:
            label = self._server_label(selected[0])
        else:
            label = f'{len(selected)} servers selected'
        self.choose_servers_button.setText(label)
        self.choose_servers_button.setToolTip(
            "\n".join(self._server_label(server) for server in selected) or "Select one or more DNS servers")
        save_config(self.cfg)

    def _clear_results(self):
        self.current_lookup = None
        self._set_output_actions(False)
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
        servers = [a.data() for a in self.server_actions if a.isChecked()]
        if not servers:
            QMessageBox.warning(self, "DNS servers", "Select at least one DNS server.")
            return
        self._start_lookup(domain, record_type, servers)

    def _start_lookup(self, domain, record_type, servers, baseline=None):
        if self._lookup_running:
            return
        self._comparison_baseline = deepcopy(baseline) if baseline else None
        self._query_server_names = dict(self.cfg.get("dns_server_names", {}))
        from .dns_worker import prepare_query
        name, kind = prepare_query(domain, record_type)
        self.record_combo.setCurrentText(kind)
        self.tabs.setCurrentWidget(self.lookup_tab)
        self._clear_results()
        self.results.setPlainText(f"Querying {domain} ({kind}) as {name}...")
        self._lookup_running = True
        self.run_button.setEnabled(False)
        self.rerun_button.setEnabled(False)
        self.compare_history_button.setEnabled(False)
        self.worker = DNSLookupThread(domain, kind, servers)
        self.worker.completed.connect(self._display_result)
        self.worker.finished.connect(self._lookup_finished)
        self.worker.start()

    def _lookup_finished(self):
        self._lookup_running = False
        self.run_button.setEnabled(True)
        self.rerun_button.setEnabled(True)
        self.compare_history_button.setEnabled(True)

    def _wait_for_lookup(self):
        if self._lookup_running:
            self.worker.wait()

    def _display_result(self, lookup):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lookup['timestamp'] = timestamp
        for result in lookup['results']:
            name = getattr(self, '_query_server_names', self.cfg.get('dns_server_names', {})).get(result['requested_server'])
            if name:
                result['requested_server_name'] = name
        if self._comparison_baseline is not None:
            lookup['history_comparison'] = compare_history(self._comparison_baseline, lookup)
        self._comparison_baseline = None
        full_result = format_text(lookup)
        self._render_lookup(lookup)
        self.cfg.setdefault("history", []).append(dict(query=lookup['query'], timestamp=timestamp, result=full_result, lookup=lookup))
        save_config(self.cfg)
        self._refresh_history_view()

    def _render_lookup(self, lookup):
        self._clear_results()
        summary = QLabel(f"Query: {lookup['query']}" + (' — ' + lookup['comparison'] if lookup.get('comparison') else ''))
        summary.setTextFormat(Qt.TextFormat.PlainText)
        summary.setWordWrap(True)
        self.structured_layout.addWidget(summary)
        comparison = lookup.get('history_comparison')
        if comparison:
            dates = QLabel(f"Saved: {comparison['saved_timestamp']}    Current: {comparison['current_timestamp']}"
                           "\nAdded = green; Removed = red. TTL and record order are ignored.")
            dates.setTextFormat(Qt.TextFormat.PlainText)
            dates.setWordWrap(True)
            self.structured_layout.addWidget(dates)
        elif len(lookup['results']) > 1:
            self.structured_layout.addWidget(QLabel('Different = highlighted; Shared = present on every server.'))
        statuses = server_statuses(lookup['results'])
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.result_tables = []
        for result_index, result in enumerate(lookup['results']):
            panel = QWidget()
            panel.setMinimumWidth(480 if comparison else 420)
            layout = QVBoxLayout(panel)
            server_title = result.get('requested_server_name', '')
            server_title = f"{server_title} — {result['requested_server']}" if server_title else result['requested_server']
            label = QLabel(f"{server_title}\nResponding server: {result['server'] or 'Unavailable'}"
                           f"\n{result['record_type']} — {result['elapsed_ms']} ms")
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setWordWrap(True)
            layout.addWidget(label)
            if result['error']:
                error = QLabel(result['error'])
                error.setTextFormat(Qt.TextFormat.PlainText)
                error.setWordWrap(True)
                layout.addWidget(error)
            history_result = comparison['results'][result_index] if comparison else None
            if history_result and history_result['error']:
                warning = QLabel('Unable to compare: ' + history_result['error'])
                warning.setTextFormat(Qt.TextFormat.PlainText)
                warning.setWordWrap(True)
                layout.addWidget(warning)
            records = history_result['rows'] if history_result else result['records']
            columns = [('status', 'Change' if comparison else 'Comparison'), ('name', 'Name'),
                       ('type', 'Type'), ('value', 'Value')]
            columns += [('saved_ttl', 'Saved TTL'), ('current_ttl', 'Current TTL')] if comparison else [('ttl', 'TTL (s)')]
            if not comparison and len(lookup['results']) == 1:
                columns = columns[1:]
            table = QTableWidget(len(records), len(columns))
            table.display_records = records if comparison else [dict(record, status=statuses[result_index][i])
                                                       for i, record in enumerate(records)]
            table.setHorizontalHeaderLabels([label for key, label in columns])
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            table.verticalHeader().hide()
            for col, (key, title) in enumerate(columns):
                table.setColumnWidth(col, 110 if key in ('name', 'status') else 90 if key in ('saved_ttl', 'current_ttl') else 65)
                if key == 'value':
                    table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            for row, record in enumerate(records):
                status = record.get('status', statuses[result_index][row] if not comparison else '')
                for col, (key, title) in enumerate(columns):
                    value = status if key == 'status' else record.get(key, '')
                    item = QTableWidgetItem(str(value))
                    item.setToolTip(str(value))
                    color = {'Different': '#fff0b3', 'Added': '#c8eed0', 'Removed': '#ffd0d0'}.get(status)
                    if color:
                        item.setBackground(QBrush(QColor(color)))
                        item.setForeground(QBrush(QColor('#111111')))
                    table.setItem(row, col, item)
            layout.addWidget(table)
            self.result_tables.append(table)
            splitter.addWidget(panel)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(splitter)
        self.structured_layout.addWidget(scroll)
        self.result_stack.setCurrentWidget(self.structured_results)
        self.current_lookup = lookup
        self._set_output_actions(True)

    def _refresh_history_view(self):
        self.history_list.clear()
        history = self.cfg.get("history", [])
        for index in reversed(range(len(history))):
            entry = history[index]
            if not history_matches(entry, self.history_search.text().strip(),
                    self.history_server_filter.text().strip(),
                    '' if self.history_type_filter.currentIndex() == 0 else self.history_type_filter.currentText(),
                    self.history_from.date().toString('yyyy-MM-dd') if self.history_date_filter.isChecked() else '',
                    self.history_to.date().toString('yyyy-MM-dd') if self.history_date_filter.isChecked() else ''):
                continue
            first_line = entry["result"].split("\n", 1)[0]
            server_names = ', '.join(r.get('requested_server_name') or r['requested_server']
                                     for r in entry.get('lookup', {}).get('results', []))
            item = QListWidgetItem(f"{first_line} — {entry['query']}" + (f" — {server_names}" if server_names else ''))
            item.setToolTip(item.text())
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.history_list.addItem(item)
        self.history_count.setText(f"{self.history_list.count()} of {len(history)} saved lookups")

    def _reset_history_filters(self):
        self.history_search.clear()
        self.history_server_filter.clear()
        self.history_type_filter.setCurrentIndex(0)
        self.history_date_filter.setChecked(False)

    def _selected_history(self):
        item = self.history_list.currentItem()
        if item is None:
            return None
        index = item.data(Qt.ItemDataRole.UserRole)
        history = self.cfg.get('history', [])
        return history[index] if isinstance(index, int) and 0 <= index < len(history) else None

    def _open_selected_history(self):
        selected = self._selected_history()
        if selected is None:
            return
        if 'lookup' in selected:
            self._render_lookup(selected['lookup'])
        else:
            self._clear_results()
            self.results.setPlainText(selected["result"])
            self._set_output_actions(bool(selected['result']))
        self.tabs.setCurrentWidget(self.lookup_tab)

    def _compare_selected_history(self):
        selected = self._selected_history()
        if selected is None or self._lookup_running:
            return
        if not selected.get('lookup', {}).get('results'):
            QMessageBox.information(self, 'Compare with Current',
                                    'This older text-only entry has no structured records to compare.')
            return
        self._rerun_selected_history(compare=True)

    def _rerun_selected_history(self, checked=False, compare=False):
        selected = self._selected_history()
        if selected is None or self._lookup_running:
            return
        self.domain_input.setText(selected['query'])
        lookup = selected.get('lookup')
        if lookup and lookup.get('results'):
            results = lookup['results']
            kind = results[0]['record_type']
            servers = list(dict.fromkeys(None if r['requested_server'] == 'System default'
                                        else r['requested_server'] for r in results))
            for server in servers:
                if server is not None and server not in self.cfg.get('dns_servers', []):
                    self.cfg.setdefault('dns_servers', []).append(server)
            self.cfg['selected_dns_servers'] = servers
            self._reload_compare_servers()
            if compare:
                baseline = deepcopy(lookup)
                baseline.setdefault('timestamp', selected.get('timestamp') or selected['result'].split('\n')[0])
                self._start_lookup(selected['query'], kind, servers, baseline=baseline)
            else:
                self._start_lookup(selected['query'], kind, servers)
        else:
            # Text-only history has no resolver/type metadata: use visible controls.
            self._run_lookup()

    def _set_output_actions(self, enabled):
        for widget in (self.copy_selected_button, self.copy_all_button, self.export_button):
            widget.setEnabled(enabled)

    def _copy_all(self):
        QApplication.clipboard().setText(export_result(self.current_lookup, self.results.toPlainText(), 'txt'))

    def _copy_selected(self):
        if self.current_lookup is None:
            text = self.results.textCursor().selectedText().replace('\u2029', '\n')
        else:
            lines = []
            for result, table in zip(self.current_lookup['results'], self.result_tables):
                for row in sorted(index.row() for index in table.selectionModel().selectedRows()):
                    record = table.display_records[row]
                    lines.append('\t'.join(str(v) for v in (result['server'], record['name'],
                                 record['type'], record['value'], record.get('ttl', ''), record.get('status', ''))))
            text = '\n'.join(lines)
            if text:
                text = 'Server\tName\tType\tValue\tTTL (s)\tChange\n' + text
        if text:
            QApplication.clipboard().setText(text)
        else:
            QMessageBox.information(self, "Copy Selected", "Select result rows or text to copy.")

    def _export_results(self, kind):
        path, _ = QFileDialog.getSaveFileName(self, "Export results", f"TrayNSLookup-results.{kind}",
                                             f"{kind.upper()} files (*.{kind})")
        if not path:
            return
        if not Path(path).suffix:
            path += '.' + kind
        try:
            with open(path, 'w', encoding='utf-8', newline='') as output:
                output.write(export_result(self.current_lookup, self.results.toPlainText(), kind))
        except OSError as exc:
            QMessageBox.warning(self, "Export failed", str(exc))

    def _clear_history(self):
        if QMessageBox.question(self, "Clear History", "Delete all saved results?") == QMessageBox.StandardButton.Yes:
            self.cfg["history"] = []
            save_config(self.cfg)
            self._refresh_history_view()

    def _open_manage_servers(self):
        new_servers = self.open_manage_servers_callback(self.cfg.get("dns_servers", []))
        if new_servers is not None:
            self.cfg["dns_servers"] = new_servers
            save_config(self.cfg)
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
