from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QPushButton
from PyQt6.QtCore import Qt


class ProgressWindow(QDialog):
    """Modal progress window showing progress and logs for long operations."""
    def __init__(self, title: str = "Progress", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout(self)
        self.label = QLabel("")
        layout.addWidget(self.label)

        self.pbar = QProgressBar()
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(100)
        layout.addWidget(self.pbar)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setEnabled(False)
        layout.addWidget(self.close_btn)

    def set_label(self, text: str):
        self.label.setText(text)

    def set_progress(self, value: int):
        try:
            self.pbar.setValue(int(value))
        except Exception:
            pass

    def append_log(self, text: str):
        self.log.append(text)

    def enable_close(self):
        self.close_btn.setEnabled(True)
