import sys
from PyQt6.QtWidgets import QApplication
from database import DatabaseManager
from monitor import SecurityEngine
from auth import AuthService
from interface import MainUI

def main():
    app = QApplication(sys.argv)
    db = DatabaseManager()
    engine = SecurityEngine()
    auth = AuthService(db)
    window = MainUI(auth, db, engine)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()