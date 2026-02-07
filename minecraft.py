import minecraft_launcher_lib
import subprocess
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QLineEdit, QLabel
from PyQt6.QtCore import Qt

class MinecraftModule(QWidget):
    def __init__(self):
        super().__init__()
        self.minecraft_dir = minecraft_launcher_lib.utils.get_minecraft_directory().replace("minecraft", ".hidenlogick_mc")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("HidenLogick - Minecraft")
        self.setFixedSize(350, 300)
        self.setStyleSheet("background-color: #121212; color: white;")

        layout = QVBoxLayout()
        self.label = QLabel("MINECRAFT MODULE")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("padding: 10px; background: #1E1E1E; border: 1px solid #333; border-radius: 5px;")

        self.version_select = QComboBox()
        self.version_select.setStyleSheet("padding: 10px; background: #1E1E1E; border: 1px solid #333;")
        
        self.status_label = QLabel("Loading versions...")
        
        self.btn_run = QPushButton("START GAME")
        self.btn_run.setStyleSheet("background-color: #388E3C; padding: 15px; font-weight: bold; border-radius: 5px;")
        self.btn_run.clicked.connect(self.run_game)

        layout.addWidget(self.label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.version_select)
        layout.addWidget(self.status_label)
        layout.addWidget(self.btn_run)

        self.setLayout(layout)
        self.load_versions()

    def load_versions(self):
        try:
            versions = [v["id"] for v in minecraft_launcher_lib.utils.get_version_list() if v["type"] == "release"]
            self.version_select.addItems(versions[:20])
            self.status_label.setText("Select version and play")
        except Exception:
            self.status_label.setText("Error loading versions.")

    def run_game(self):
        username = self.username_input.text() or "Player"
        version = self.version_select.currentText()
        self.btn_run.setText("LAUNCHING...")
        self.btn_run.setEnabled(False)
        QApplication.processEvents()

        minecraft_launcher_lib.install.install_minecraft_version(version, self.minecraft_dir)
        options = {"username": username, "uuid": "0", "token": "0"}
        command = minecraft_launcher_lib.command.get_minecraft_command(version, self.minecraft_dir, options)
        
        subprocess.Popen(command)
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinecraftModule()
    window.show()
    sys.exit(app.exec())
