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

## 🧰 Building the Executable (Windows)

To package TrayNSLookup into a standalone Windows EXE, use the `build.py` build script.

### Prerequisites
- Python 3.10+
- PyInstaller installed via requirements.txt
- (Optional) Inno Setup if you want to build an installer:

  [Download Inno Setup](https://jrsoftware.org/isinfo.php)

  If Inno Setup is not installed a standalone exe file will be created.

## Build JSON: `build.json`
The `build.json` contains the information used to package the EXE file with `pyinstaller`

```json
{
  "AppName": "TrayNSLookup",
  "Version": "1.0.2",
  "Icon": "$AppName.ico",
  "pyinstaller": [
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--add-data", "icons;icons",
    "--name", "$AppName",
    "--icon", "$Icon",
    "main.py"
  ]
}
```

## Build Script: `build.py`
The `build.py` script automates the entire packaging process.

Run this from the command line at the project root:
```console
python build.py
```

### What It Does
1. It looks for the build.json file and executes `pyinstaller` with parameters in this file
4. Moves the built EXE to the project root.
5. Runs Inno Setup from:
   ```
   build\windows\TrayWeatherApp.iss
   ```
6. If Inno Setup completes successfully:
   - Deletes the standalone EXE file from the root folder.
   - Moves the installation EXE to the root folder.
7. If Inno Setup fails or is skipped, the standalone EXE remains in the project root.
8. Cleans `build/`, `dist/`, `.spec`, and `__pycache__` folders from the application folder.

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

## 💡 Building Tips

- Always run the build command from the **project root**
- Ensure your `.ico` file exists in the root (e.g., `TrayNSLookup.ico`)
- If debugging build issues, run:
  ```bash
  python build.py --verbose
  ```
- You can modify `build.json` to add extra PyInstaller options as needed

---

## ☀️ Summary

| Action | Command |
|--------|----------|
| 🧪 Run app from source | `python -m TrayNSLookup` |
| 🏗️ Build standalone EXE | `python build.py` |
| 🧱 Build with full logs | `python build.py --verbose` |
| 💾 Output | EXE or installer saved in project root |
| 🧹 Cleanup | Automatic (safe mode, no root deletion) |
