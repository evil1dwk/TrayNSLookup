# 🔍 TrayNSLookup

A lightweight DNS lookup utility for Windows and Linux that lives in the system tray.  
Built with **Python 3.11+** and **PyQt6**, TrayNSLookup lets you perform DNS queries instantly — right from your desktop — with a persistent lookup history.

---

## 🧭 Features

- 🖥️ **Cross-platform support** — works on both Windows and Linux
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
├── build.py                   # cross-platform build script
├── build/
│   ├── windows/
│   │   ├── build.json          # Windows build configuration
│   │   └── TrayNSLookup.iss    # optional Inno Setup script
│   └── linux/
│       └── build.json          # Linux build configuration
│
├── releases/
│   ├── windows/                # built executables (Windows)
│   └── linux/                  # built executables (Linux)
│
├── TrayNSLookup/
│   ├── __init__.py
│   ├── __main__.py             # enables "python -m TrayNSLookup"
│   ├── main.py                 # main entry point
│   ├── app.py                  # QApplication + tray management
│   ├── ui_mainwindow.py        # main UI window with tabs
│   ├── dialogs.py              # DNS server management dialog
│   ├── dns_worker.py           # threaded DNS resolver
│   ├── config.py               # config & icon handling
│   └── icons/
│       ├── TrayNSLookup.ico
│       └── gear.ico
├── TrayNSLookup.ico            # app icon
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

Run the app as a module or script:

```bash
python -m TrayNSLookup
```
or
```bash
python TrayNSLookup/main.py
```

---

## 🧰 Building the Executable (Cross-Platform)

You can package TrayNSLookup into a standalone executable using `build.py`.

### Prerequisites

- Python 3.10+  
- PyInstaller installed via requirements.txt  
- *(Windows only)* Inno Setup (optional) for generating an installer:

  [Download Inno Setup](https://jrsoftware.org/isinfo.php)

If Inno Setup is not installed, a standalone executable will still be created.

### Build Config Files
The build configuration is platform-specific:

- **Windows:** `build/windows/build.json`
- **Linux:** `build/linux/build.json`

Example `build.json`:

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

---

## 🏗️ Build Script: `build.py`

The `build.py` script automates the entire packaging process.

Run this from the project root:

```bash
python build.py
```

### What It Does

1. Detects your OS and loads the proper build configuration file:
   - `build/windows/build.json` on Windows
   - `build/linux/build.json` on Linux
2. Runs **PyInstaller**, outputting all files to:
   - `releases/windows/` or `releases/linux/`
3. (Windows only) Runs **Inno Setup** if available.
4. Removes the standalone executable once the installer is built (Windows only).
5. Performs safe cleanup of build artifacts:
   - Deletes `build/`, `dist/`, `.spec`, and `__pycache__` inside the app folder.

✅ **Notes**
- The app’s icons are bundled **inside the executable**.
- If `TrayNSLookup.ico` is missing, the app automatically falls back to a 🔍 emoji icon.
- On Linux, no Inno Setup is run; the standalone binary remains in `releases/linux/`.
- Configuration and lookup history are stored at:
  ```
  ~/.traynslookup_config.json
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

Delete this file to reset settings.

---

## 💡 Building Tips

- Always run `python build.py` from the **project root**
- Ensure the `.ico` file exists in the root (e.g., `TrayNSLookup.ico`)
- To debug build issues:
  ```bash
  python build.py --verbose
  ```
- Modify `build.json` to include additional PyInstaller options as needed

---

## ☀️ Summary

| Action | Command |
|--------|----------|
| 🧪 Run app from source | `python -m TrayNSLookup` |
| 🏗️ Build standalone executable | `python build.py` |
| 🧱 Build with full logs | `python build.py --verbose` |
| 💾 Output | `releases/<os>/` (windows or linux) |
| 🧹 Cleanup | Automatic, safe (no root deletions) |
