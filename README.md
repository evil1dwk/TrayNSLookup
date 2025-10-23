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

## 🧰 Packaging with PyInstaller

Build a standalone Windows `.exe` with embedded icons:

```bash
pyinstaller --onefile --windowed TrayNSLookup/main.py ^
  --add-data "TrayNSLookup/icons;icons" ^
  --icon TrayNSLookup/icons/TrayNSLookup.ico ^
  --name TrayNSLookup
```

After building, your executable will be in:
```
dist/TrayNSLookup.exe
```

✅ **Notes**
- The app’s icons are bundled **inside the EXE**.
- If `TrayNSLookup.ico` is missing, the app automatically falls back to a 🔍 emoji icon.
- The configuration and lookup history are saved to:
  ```
  C:\Users\<YourName>\.traynslookup_config.json
  ```

---

## 🧩 Common Commands

| Action | Command |
|--------|----------|
| Run the app | `python -m TrayNSLookup` |
| Clean PyInstaller build files | `rmdir /s /q build dist` |
| Create executable | `pyinstaller --onefile --windowed TrayNSLookup/main.py --add-data "TrayNSLookup/icons;icons" --icon TrayNSLookup/icons/TrayNSLookup.ico --name TrayNSLookup` |
| Run directly from EXE | `dist\TrayNSLookup.exe` |

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
- The `.spec` file can simplify rebuilding — ask ChatGPT to generate one for you.

---

## 📜 License

MIT License © 2025  
You’re free to modify, use, and distribute TrayNSLookup with attribution.
