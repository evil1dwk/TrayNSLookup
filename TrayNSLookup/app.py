import sys
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox, QDialog
from .config import load_config, get_app_icon
from .dialogs import ManageDNSServersDialog
from .ui_mainwindow import MainWindow

class TrayNSLookupApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        self.cfg = load_config()
        self.icon = get_app_icon()

        self.main_win = MainWindow(self.cfg, self._open_manage_servers_dialog)

        self.tray = QSystemTrayIcon(self.icon, self)
        self.tray.setToolTip("Tray NSLookup")
        self._build_tray_menu()
        self.tray.show()
        self.tray.activated.connect(self._on_tray_activated)

        self.tray.showMessage(
            "Tray NSLookup", "Running in the system tray.\nLeft-click to open.",
            QSystemTrayIcon.MessageIcon.Information, 3000
        )

    def _build_tray_menu(self):
        menu = QMenu()
        open_action = QAction("Open", self)
        open_action.triggered.connect(self._show_main_window)
        menu.addAction(open_action)

        manage_action = QAction("Manage DNS Servers", self)
        manage_action.triggered.connect(lambda: self._open_manage_servers_dialog(self.cfg["dns_servers"], True))
        menu.addAction(manage_action)

        menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_main_window()

    def _show_main_window(self):
        self.main_win.show()
        self.main_win.raise_()
        self.main_win.activateWindow()

    def _open_manage_servers_dialog(self, servers, show_message=False):
        dlg = ManageDNSServersDialog(servers, parent=self.main_win)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            new_servers = dlg.get_servers()
            if show_message:
                QMessageBox.information(None, "DNS Servers Updated", "Changes saved successfully.")
            return new_servers
        return None

    def _quit_app(self):
        self.tray.hide()
        self.quit()
