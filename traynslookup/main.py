import sys
from traynslookup.app import TrayNSLookupApp

def main():
    app = TrayNSLookupApp(sys.argv)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
