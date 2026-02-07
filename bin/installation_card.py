"""Dedicated installation card for clean, isolated UI."""
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QComboBox, QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from bin import styles


class InstallationCard(QFrame):
    """Dedicated installation panel - isolated from main UI."""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border: 1px solid #0078d4;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Title banner
        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #0078d4; border-radius: 6px;")
        title_frame.setFixedHeight(50)
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 0, 15, 0)
        
        title = QLabel("⚙ INSTALLATION")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title_layout.addWidget(title)
        
        layout.addWidget(title_frame)
        
        # Player nickname section
        nick_label = QLabel("👤 Player Nickname")
        nick_label.setStyleSheet("color: #0078d4; font-weight: bold; font-size: 12px; margin-top: 12px; margin-bottom: 5px;")
        layout.addWidget(nick_label)
        
        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Enter your nickname (3-32 characters)")
        self.nick_input.setStyleSheet("""
            QLineEdit {
                background: #111;
                color: #ddd;
                padding: 10px;
                border: 1px solid #333;
                border-radius: 6px;
                font-size: 11px;
                selection-background-color: #0078d4;
            }
            QLineEdit:focus { 
                border: 2px solid #0078d4; 
                background: #0a0a0a;
            }
        """)
        self.nick_input.setMaxLength(32)
        self.nick_input.setMinimumHeight(36)
        layout.addWidget(self.nick_input)
        
        # Version section
        ver_label = QLabel("📦 Minecraft Version")
        ver_label.setStyleSheet("color: #0078d4; font-weight: bold; font-size: 12px; margin-top: 12px; margin-bottom: 5px;")
        layout.addWidget(ver_label)
        
        self.ver_combo = QComboBox()
        self.ver_combo.setStyleSheet("""
            QComboBox {
                background: #111;
                color: #ddd;
                padding: 8px;
                border: 1px solid #333;
                border-radius: 6px;
                font-size: 11px;
                selection-background-color: #0078d4;
            }
            QComboBox:focus { 
                border: 2px solid #0078d4; 
                background: #0a0a0a;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background: #0a0a0a;
                color: #ddd;
                border: 1px solid #333;
                selection-background-color: #0078d4;
            }
        """)
        self.ver_combo.setMinimumHeight(36)
        layout.addWidget(self.ver_combo)
        
        # Log section label
        log_label = QLabel("📋 Installation Log")
        log_label.setStyleSheet("color: #0078d4; font-weight: bold; font-size: 12px; margin-top: 12px; margin-bottom: 5px;")
        layout.addWidget(log_label)
        
        # Progress bar
        self.p_bar = QProgressBar()
        self.p_bar.setStyleSheet("""
            QProgressBar {
                background-color: #111;
                border: 1px solid #333;
                border-radius: 6px;
                height: 8px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 5px;
            }
        """)
        self.p_bar.setVisible(False)
        layout.addWidget(self.p_bar)
        
        # Log/progress text
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setText("Installation log will appear here...")
        self.log_view.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #666;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 10px;
            }
        """)
        self.log_view.setMinimumHeight(80)
        self.log_view.setMaximumHeight(120)
        layout.addWidget(self.log_view)
        
        # Start button
        self.btn_start = QPushButton("START INSTALLATION")
        self.btn_start.setMinimumHeight(45)
        self.btn_start.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.btn_start.setStyleSheet(styles.PLAY_BUTTON_STYLE)
        layout.addWidget(self.btn_start)
        
        layout.addStretch()

    def clear_log(self):
        """Clear the log view."""
        self.log_view.clear()
        self.log_view.setTextColor(self.log_view.palette().color(self.log_view.foregroundRole()))
    
    def append_log(self, text, color="#888"):
        """Add timestamped log entry."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f'<span style="color: #444;">[{timestamp}]</span> <span style="color: {color}; font-family: Consolas;">{text}</span>'
        self.log_view.append(log_entry)
        self.log_view.ensureCursorVisible()
    
    def show_progress(self):
        """Show progress bar."""
        self.p_bar.setVisible(True)
        self.p_bar.setValue(0)
    
    def hide_progress(self):
        """Hide progress bar."""
        self.p_bar.setVisible(False)
    
    def set_progress(self, value):
        """Set progress bar value."""
        self.p_bar.setValue(value)
    
    def set_installing(self, is_installing):
        """Enable/disable controls during install."""
        self.nick_input.setEnabled(not is_installing)
        self.ver_combo.setEnabled(not is_installing)
        self.btn_start.setEnabled(not is_installing)
