import minecraft_launcher_lib
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QLineEdit

class MinecraftModule(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HidenLogick - Minecraft")
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(300, 250)
        layout = QVBoxLayout()

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")

        # Version Selection
        self.version_select = QComboBox()
        # In a real scenario, you'd fetch this list via minecraft_launcher_lib
        self.version_select.addItems(["1.20.1", "1.19.4", "1.18.2"])

        self.btn_run = QPushButton("START GAME")
        self.btn_run.clicked.connect(self.run_game)

        layout.addWidget(self.user_input)
        layout.addWidget(self.version_select)
        layout.addWidget(self.btn_run)
        self.setLayout(layout)

    def run_game(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinecraftModule()
    window.show()
    sys.exit(app.exec())
