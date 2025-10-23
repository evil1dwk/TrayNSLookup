import sys
from TrayNSLookup.app import TrayNSLookupApp  # absolute import (case-sensitive)

def main():
    app = TrayNSLookupApp(sys.argv)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
