"""Settings dialog for HidenLogick launcher."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QCheckBox, QSpinBox, QGroupBox, QTabWidget, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SettingsDialog(QDialog):
    """Premium settings dialog with tabs."""
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("HidenLogick Settings")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tabs.addTab(general_tab, "General")
        
        # Import tab
        import_tab = self.create_import_tab()
        tabs.addTab(import_tab, "Import")
        
        # Advanced tab
        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_and_close)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def create_general_tab(self):
        """Create general settings tab."""
        widget = QVBoxLayout()
        
        group = QGroupBox("Launcher Behavior")
        layout = QVBoxLayout()
        
        self.auto_launch_check = QCheckBox("Auto-import on startup")
        self.auto_launch_check.setChecked(self.config.get("auto_import_on_startup", False))
        layout.addWidget(self.auto_launch_check)
        
        self.backup_check = QCheckBox("Create backup copies when importing")
        self.backup_check.setChecked(self.config.get("backup_copies", True))
        layout.addWidget(self.backup_check)
        
        group.setLayout(layout)
        widget.addWidget(group)
        
        widget.addStretch()
        
        result = QWidget()
        result.setLayout(widget)
        return result

    def create_import_tab(self):
        """Create import settings tab."""
        widget = QVBoxLayout()
        
        group = QGroupBox("Background Import Scanner")
        layout = QVBoxLayout()
        
        self.scan_check = QCheckBox("Enable background scanner")
        self.scan_check.setChecked(self.config.get("enable_scanner", False))
        layout.addWidget(self.scan_check)
        
        scan_layout = QHBoxLayout()
        scan_layout.addWidget(QLabel("Scan interval (minutes):"))
        self.scan_spin = QSpinBox()
        self.scan_spin.setMinimum(5)
        self.scan_spin.setMaximum(1440)
        self.scan_spin.setValue(self.config.get("scan_interval_minutes", 15))
        scan_layout.addWidget(self.scan_spin)
        scan_layout.addStretch()
        layout.addLayout(scan_layout)
        
        group.setLayout(layout)
        widget.addWidget(group)
        
        # Info
        info = QLabel("Background scanner will periodically check for new versions in external installations.")
        info.setStyleSheet("color: #888; font-size: 11px;")
        info.setWordWrap(True)
        widget.addWidget(info)
        
        widget.addStretch()
        
        result = QWidget()
        result.setLayout(widget)
        return result

    def save_and_close(self):
        """Save settings and close."""
        self.config.set("auto_import_on_startup", self.auto_launch_check.isChecked())
        self.config.set("backup_copies", self.backup_check.isChecked())
        self.config.set("enable_scanner", self.scan_check.isChecked())
        self.config.set("scan_interval_minutes", self.scan_spin.value())
        self.config.set("discord_rpc_enabled", self.discord_check.isChecked())
        self.config.set("performance_overlay_enabled", self.perf_check.isChecked())
        self.accept()

    def create_advanced_tab(self):
        """Create advanced settings tab."""
        widget = QVBoxLayout()
        
        group = QGroupBox("Advanced Features")
        layout = QVBoxLayout()
        
        self.discord_check = QCheckBox("Enable Discord Rich Presence")
        self.discord_check.setChecked(self.config.get("discord_rpc_enabled", False))
        layout.addWidget(self.discord_check)
        
        self.perf_check = QCheckBox("Enable Performance Metrics Overlay")
        self.perf_check.setChecked(self.config.get("performance_overlay_enabled", False))
        layout.addWidget(self.perf_check)
        
        group.setLayout(layout)
        widget.addWidget(group)
        
        # Info
        info = QLabel("Discord RPC shows your game status on Discord. Performance overlay displays FPS and resource usage while playing.\n\nNote: Requires relaunch to take effect.")
        info.setStyleSheet("color: #888; font-size: 10px;")
        info.setWordWrap(True)
        widget.addWidget(info)
        
        widget.addStretch()
        
        result = QWidget()
        result.setLayout(widget)
        return result
