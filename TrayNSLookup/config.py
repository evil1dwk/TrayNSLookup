import json
import sys
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt6.QtWidgets import QStyle

CONFIG_PATH = Path.home() / ".traynslookup_config.json"
DEFAULT_DNS_SERVERS = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

ICON_DIRS = [
    BASE_DIR / "icons",
    BASE_DIR / "TrayNSLookup" / "icons",
    Path(__file__).resolve().parent / "icons",
]

def _find_icon(filename: str) -> Path | None:
    for d in ICON_DIRS:
        p = d / filename
        if p.exists():
            return p
    return None

def create_text_icon(text="🔍", size=64) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    font = QFont()
    font.setPointSize(size // 2)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
    painter.end()
    return QIcon(pixmap)

def get_app_icon() -> QIcon:
    ico = _find_icon("TrayNSLookup.ico")
    return QIcon(str(ico)) if ico else create_text_icon("🔍")

def get_gear_icon(style) -> QIcon:
    ico = _find_icon("gear.ico")
    return QIcon(str(ico)) if ico else style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)

def load_config():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    return {"dns_servers": DEFAULT_DNS_SERVERS.copy(), "history": []}

def save_config(cfg):
    try:
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2))
    except Exception as e:
        print("Failed to save config:", e)
