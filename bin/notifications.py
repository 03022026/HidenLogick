"""Toast notifications system for HidenLogick."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont


class Toast(QWidget):
    """Simple toast notification that auto-hides."""
    closed = pyqtSignal()

    def __init__(self, title: str, message: str, duration: int = 3000, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: 1px solid #0078d4;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        title_label = QLabel(title)
        title_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0078d4;")
        layout.addWidget(title_label)
        
        msg_label = QLabel(message)
        msg_font = QFont("Segoe UI", 10)
        msg_label.setFont(msg_font)
        msg_label.setStyleSheet("color: #ccc;")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)
        
        self.setFixedWidth(300)
        self.adjustSize()
        
        # Auto-close timer
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.close_toast)
        timer.start(duration)
    
    def close_toast(self):
        """Close and emit signal."""
        self.closed.emit()
        self.close()

    def showTopRight(self, parent_widget=None):
        """Show in top-right corner."""
        if parent_widget:
            geom = parent_widget.geometry()
            x = geom.right() - self.width() - 20
            y = geom.top() + 20
        else:
            x = self.screen().geometry().right() - self.width() - 20
            y = self.screen().geometry().top() + 20
        
        self.move(x, y)
        self.show()


class NotificationManager:
    """Manager for showing toasts."""
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        self.toasts = []

    def show(self, title: str, message: str, duration: int = 3000):
        """Show a toast notification."""
        toast = Toast(title, message, duration, self.parent)
        toast.closed.connect(lambda: self.toasts.remove(toast))
        self.toasts.append(toast)
        toast.showTopRight(self.parent)
