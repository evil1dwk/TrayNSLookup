# 📘 TrayNSLookup

A lightweight DNS lookup utility for Windows that lives in the system tray.  
Built with **Python 3.11+** and **PyQt6**, TrayNSLookup lets you perform DNS queries instantly — right from your desktop — with a persistent lookup history.

---

## 🧭 Features

- 🪟 **Single-window interface** with tabs:
  - **Lookup**: Query any domain or record type (A, AAAA, MX, CNAME, TXT, etc.)
  - **History**: Review past lookups and reload results
- ⚙️ **Custom DNS servers** — manage, edit, and switch easily
- 🧠 **Persistent history** saved locally in `.traynslookup_config.json`
- 📍 **Window position + size persistence**
- 🪄 **System tray integration**
  - Left-click to open the window
  - Right-click menu with options: *Open*, *Manage DNS Servers*, *Quit*
  
---

## 📂 Project Structure

```
TrayNSLookup/
├── build.ps1               # build script to create a stand alone EXE file
│
├── TrayNSLookup/
│   ├── __init__.py
│   ├── __main__.py         # enables "python -m TrayNSLookup"
│   ├── main.py             # main entry point (used for PyInstaller build)
│   ├── app.py              # QApplication + tray management
│   ├── ui_mainwindow.py    # main UI window with tabs
│   ├── dialogs.py          # DNS server management dialog
│   ├── dns_worker.py       # threaded DNS resolver
│   ├── config.py           # config & icon handling
│   └── icons/
│       ├── TrayNSLookup.ico
│       └── gear.ico
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Requirements

- Python **3.11+**
- [PyQt6](https://pypi.org/project/PyQt6/)
- [dnspython](https://pypi.org/project/dnspython/)

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## ▶️ Running in Development

You can run the app as a module or script:

**Option 1 (recommended):**
```bash
python -m TrayNSLookup
```

**Option 2:**
```bash
python TrayNSLookup/main.py
```

---

## 🧰 Packaging with `build.ps1`

The `build.ps1` script automates the entire packaging process.

Run this from **PowerShell** at the project root:
```powershell
.\build.ps1 -AppName TrayNSLookup
```

### What It Does
1. Automatically detects your project paths.
2. Cleans old `build/`, `dist/`, `.spec`, and `__pycache__` folders.
3. Runs PyInstaller to generate a single-file executable:
   ```powershell
   pyinstaller --noconfirm --onefile --windowed --add-data "TrayNSLookup/icons;icons" --name TrayWeatherApp --icon ..\TrayNSLookup.ico main.py
   ```
4. Moves the built EXE to the project root.
5. Runs Inno Setup from:
   ```
   build\windows\TrayNSLookup.iss
   ```
6. If Inno Setup completes successfully:
   - Displays the full installer EXE path.
   - Deletes the standalone EXE from the root folder.
7. If Inno Setup fails or is skipped, the standalone EXE remains in the project root.

✅ **Notes**
- The app’s icons are bundled **inside the EXE**.
- If `TrayNSLookup.ico` is missing, the app automatically falls back to a 🔍 emoji icon.
- If Inno Setup isn’t found, the script will still produce a standalone EXE.
- The configuration and lookup history are saved to:
  ```
  C:\Users\<YourName>\.traynslookup_config.json
  ```

---

## 🛠️ Configuration File

TrayNSLookup stores your settings and history in a JSON file:
```json
{
  "dns_servers": ["8.8.8.8", "1.1.1.1"],
  "history": [
    {
      "query": "example.com",
      "result": "A record: 93.184.216.34"
    }
  ],
  "window": {
    "size": [760, 540],
    "pos": [100, 100]
  }
}
```

You can delete this file to reset the app.

---

## 🧩 Building Tips

- Always run the PyInstaller command from the **project root**.
- Make sure the `icons/` folder contains `TrayNSLookup.ico` and `gear.ico` before building.
- The `.spec` file can simplify rebuilding.
