import os
import sys
import minecraft_launcher_lib
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QPushButton, QLineEdit, QLabel, QFrame, QMessageBox, QWidget)
from PyQt6.QtCore import Qt

class MinecraftLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        # Získání cesty k dokumentům pro ukládání hry (bezpečnější než disk C:)
        self.minecraft_dir = os.path.join(os.getenv('APPDATA'), '.hidenlogick_mc')
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Minecraft Logic")
        self.setFixedSize(400, 500)
        self.setStyleSheet("background-color: #0d0d0d; font-family: 'Segoe UI', sans-serif;")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        # Nadpis
        self.label = QLabel("MINECRAFT SETUP")
        self.label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Input pro jméno
        self.nickname = QLineEdit()
        self.nickname.setPlaceholderText("Enter Nickname...")
        self.nickname.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a1a; color: white; border: 1px solid #333;
                border-radius: 8px; padding: 10px; font-size: 14px;
            }
        """)
        layout.addWidget(self.nickname)

        # Info o složce
        self.info = QLabel(f"Data will be stored in:\n{self.minecraft_dir}")
        self.info.setStyleSheet("color: #555; font-size: 10px; margin-top: 10px;")
        self.info.setWordWrap(True)
        layout.addWidget(self.info)

        layout.addStretch()

        # Launch Button
        self.launch_btn = QPushButton("LAUNCH GAME")
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4; color: white; border-radius: 10px;
                padding: 15px; font-weight: bold; font-size: 16px;
            }
            QPushButton:hover { background-color: #005a9e; }
        """)
        self.launch_btn.clicked.connect(self.launch_minecraft)
        layout.addWidget(self.launch_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def launch_minecraft(self):
        name = self.nickname.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a nickname!")
            return

        self.launch_btn.setText("PREPARING...")
        self.launch_btn.setEnabled(False)
        QApplication.processEvents() # Refresh UI

        try:
            # 1. Kontrola a vytvoření složky
            if not os.path.exists(self.minecraft_dir):
                os.makedirs(self.minecraft_dir)

            # 2. Nastavení verze (např. 1.20.1)
            version = "1.20.1"

            # 3. Stažení verze (pokud neexistuje)
            # callback={...} lze přidat pro progress bar
            minecraft_launcher_lib.install.install_minecraft_version(version, self.minecraft_dir)

            # 4. Generování příkazu pro spuštění
            options = {
                "username": name,
                "uuid": "",
                "token": ""
            }
            
            command = minecraft_launcher_lib.command.get_minecraft_command(version, self.minecraft_dir, options)

            # 5. Spuštění hry
            subprocess.Popen(command)
            
            # Zavřít okno logiky po úspěšném spuštění
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Crash Error", f"Failed to launch:\n{str(e)}")
            self.launch_btn.setText("LAUNCH GAME")
            self.launch_btn.setEnabled(True)

if __name__ == "__main__":
    # On Windows hide the console window when launching the GUI
    if os.name == 'nt':
        try:
            import ctypes
            whnd = ctypes.windll.kernel32.GetConsoleWindow()
            if whnd:
                ctypes.windll.user32.ShowWindow(whnd, 0)  # SW_HIDE = 0
        except Exception:
            pass

    app = QApplication(sys.argv)
    window = MinecraftLauncher()
    window.show()
    sys.exit(app.exec())