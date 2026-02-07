import sys
import os
import subprocess
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

# Hide console window on Windows
try:
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCP(65001)  # UTF-8
    # Hide console window
    import subprocess
    CREATE_NO_WINDOW = 0x08000000
    subprocess.CREATE_NO_WINDOW = CREATE_NO_WINDOW
except:
    pass

class Worker(QThread):
    finished = pyqtSignal()
    progress_update = pyqtSignal(str)
    progress_bar = pyqtSignal(int)
    
    def run(self):
        """Check and install required dependencies."""
        all_dependencies = [
            "PyQt6",
            "minecraft-launcher-lib",
            "requests",
            "pywin32",
            "psutil",
            "pypresence"
        ]
        
        total = len(all_dependencies)
        installed = 0
        
        for idx, lib in enumerate(all_dependencies):
            progress = int((idx / total) * 100)
            self.progress_bar.emit(progress)
            self.progress_update.emit(f"Checking {lib}...")
            time.sleep(0.3)  # Brief pause for effect
            
            try:
                __import__(lib.replace("-", "_"))
                self.progress_update.emit(f"✓ {lib} ready")
                installed += 1
                time.sleep(0.4)
            except ImportError:
                self.progress_update.emit(f"Installing {lib}...")
                time.sleep(0.2)
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", lib, "--quiet"],
                        timeout=120,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    self.progress_update.emit(f"✓ {lib} installed")
                    installed += 1
                    time.sleep(0.5)
                except subprocess.TimeoutExpired:
                    self.progress_update.emit(f"⚠ {lib} timed out, skipping...")
                    time.sleep(0.3)
                except Exception as e:
                    self.progress_update.emit(f"⚠ {lib} install failed, continuing...")
                    time.sleep(0.3)
        
        # Setup phase
        self.progress_bar.emit(85)
        self.progress_update.emit("Setting up directories...")
        time.sleep(0.3)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(base_dir, "bin", "assets", "miniatures")
        
        try:
            os.makedirs(assets_dir, exist_ok=True)
            self.progress_update.emit("✓ Assets ready")
            time.sleep(0.2)
        except Exception as e:
            self.progress_update.emit("⚠ Assets setup skipped")
            time.sleep(0.2)
        
        # Final checks
        self.progress_bar.emit(95)
        self.progress_update.emit("Initializing launcher...")
        time.sleep(0.4)
        
        self.progress_bar.emit(100)
        self.progress_update.emit("Ready! Loading launcher...")
        time.sleep(0.8)
        
        self.finished.emit()

class LoadingScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(500, 350)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0A0A0A;
                border: 2px solid #0078d4;
                border-radius: 15px;
            }
        """)
        
        # Center window
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 500) // 2
        y = (screen.height() - 350) // 2
        self.move(x, y)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("HIDENLOGICK")
        title_font = QFont("Segoe UI", 32, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #0078d4; letter-spacing: 3px;")
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Premium Minecraft Launcher")
        subtitle_font = QFont("Segoe UI", 11)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #555; margin-bottom: 15px;")
        layout.addWidget(subtitle)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #111;
                border: 1px solid #333;
                border-radius: 8px;
                height: 8px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 7px;
            }
        """)
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        
        # Status message
        self.status = QLabel("Starting custom engine...")
        status_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        self.status.setFont(status_font)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("color: white; margin-top: 10px;")
        layout.addWidget(self.status)
        
        # Detail message
        self.detail = QLabel("Initializing...")
        detail_font = QFont("Segoe UI", 10)
        self.detail.setFont(detail_font)
        self.detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail.setStyleSheet("color: #0078d4;")
        layout.addWidget(self.detail)
        
        layout.addStretch()
        
        # Footer
        footer = QLabel("v2.0 | Powered by HidenLogick Team")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #333; font-size: 9px;")
        layout.addWidget(footer)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Workers
        self.worker = Worker()
        self.worker.finished.connect(self.launch_app)
        self.worker.progress_update.connect(self.update_detail)
        self.worker.progress_bar.connect(self.update_progress)
        self.worker.start()
    
    def update_detail(self, message):
        """Update status details."""
        self.detail.setText(message)
    
    def update_progress(self, value):
        """Update progress bar."""
        self.progress.setValue(value)

    def launch_app(self):
        """Launch main application."""
        try:
            from bin.ui_main import HidenLogickUI
            self.main_window = HidenLogickUI()
            self.main_window.show()
        except Exception as e:
            self.detail.setText(f"Error: {e}")
            return
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoadingScreen()
    window.show()
    sys.exit(app.exec())