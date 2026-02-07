import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QFrame, QComboBox, 
                             QProgressBar, QTextEdit, QLineEdit, QScrollArea,
                             QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QFont, QColor
from bin.engine import GameEngine
from bin.storage import InstallationStorage
from bin import styles
from bin.config import Config
from bin.notifications import NotificationManager
from bin.launcher_profiles import ProfileManager
from bin.installation_card import InstallationCard
from bin.mod_profiler import ModProfiler
from bin.update_checker import UpdateChecker, UpdateNotifier
from bin.discord_rpc import get_discord_rpc
from bin.performance_metrics import PerformanceMetrics, PerformanceOverlay
from PyQt6.QtCore import QTimer

class InstallWorker(QThread):
    """Worker thread for async installation."""
    progress = pyqtSignal(int)
    log = pyqtSignal(str, str)
    finished = pyqtSignal(bool)

    def __init__(self, engine, version):
        super().__init__()
        self.engine = engine
        self.version = version
        self.is_running = True

    def run(self):
        """Run installation in background."""
        if self.is_running:
            success = self.engine.install(self.version, self.progress.emit, self.log.emit)
            self.finished.emit(success)
    
    def stop(self):
        """Stop the worker thread."""
        self.is_running = False


class LaunchWorker(QThread):
    """Worker thread for launching game."""
    log = pyqtSignal(str, str)
    finished = pyqtSignal(bool)

    def __init__(self, engine, version, username):
        super().__init__()
        self.engine = engine
        self.version = version
        self.username = username

    def run(self):
        """Launch game in background."""
        self.log.emit("🚀 Launching game...", "white")
        success = self.engine.launch(self.version, self.username)
        self.finished.emit(success)


class ImportWorker(QThread):
    """Worker thread to import versions from multiple source paths."""
    progress = pyqtSignal(int, int, str, bool)  # idx, total, name, success
    finished = pyqtSignal(dict)
    log = pyqtSignal(str)

    def __init__(self, engine, src_paths, storage, username='imported'):
        super().__init__()
        self.engine = engine
        self.src_paths = list(src_paths)
        self.storage = storage
        self.username = username

    def run(self):
        results = {}
        try:
            for p in self.src_paths:
                def cb(idx, total, name, ok):
                    try:
                        self.progress.emit(idx, total, name, ok)
                    except Exception:
                        pass

                imported = self.engine.import_versions_from_path(p, storage=self.storage, username=self.username, progress_callback=cb)
                if imported:
                    results[p] = imported
                    try:
                        self.log.emit(f"Imported {len(imported)} versions from {p}")
                    except Exception:
                        pass
        except Exception:
            pass

        self.finished.emit(results)


class InstalledVersionCard(QFrame):
    """Card for installed version."""
    play_clicked = pyqtSignal(str, str)  # version, username
    delete_clicked = pyqtSignal(str, str)  # version, username

    def __init__(self, version: str, username: str):
        super().__init__()
        self.version = version
        self.username = username
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
            }
            QFrame:hover {
                border: 1px solid #0078d4;
                background-color: #222;
            }
        """)
        self.setMinimumHeight(70)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # Version label
        version_label = QLabel(f"v{version}")
        version_font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        version_label.setFont(version_font)
        version_label.setStyleSheet("color: #0078d4;")
        layout.addWidget(version_label)
        
        # Username label
        user_label = QLabel(f"Player: {username}")
        user_font = QFont("Segoe UI", 10)
        user_label.setFont(user_font)
        user_label.setStyleSheet("color: #888;")
        layout.addWidget(user_label)
        
        # Buttons layout
        btn_layout = QHBoxLayout()
        
        play_btn = QPushButton("▶ PLAY")
        play_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover { background-color: #005a9e; }
            QPushButton:pressed { background-color: #003d75; }
        """)
        play_btn.clicked.connect(lambda: self.play_clicked.emit(self.version, self.username))
        btn_layout.addWidget(play_btn)
        
        delete_btn = QPushButton("✕ DELETE")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px 10px;
                font-size: 9px;
            }
            QPushButton:hover { background-color: #c41e3a; }
        """)
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.version, self.username))
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)


class HidenLogickUI(QMainWindow):
    """Main launcher UI - TLauncher killer."""
    def __init__(self):
        super().__init__()
        self.bin_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = os.path.dirname(self.bin_dir)
        self.engine = GameEngine(self.root_dir)
        self.storage = InstallationStorage(self.root_dir)
        self.config = Config(self.root_dir)
        self.notify = NotificationManager(self)
        self.profile_manager = ProfileManager(self.root_dir)
        self.mod_profiler = ModProfiler(self.root_dir)
        self.update_checker = UpdateChecker(self.root_dir)
        self.discord_rpc = get_discord_rpc()
        self.performance_metrics = PerformanceMetrics()
        
        self.last_progress = 0
        self.worker = None
        self.is_installing = False
        self.is_launching = False
        self.search_filter = ""
        self.installation_card = None
        
        # Background scanner setup
        self.scanner_timer = QTimer()
        self.scanner_timer.timeout.connect(self.background_scanner_tick)
        
        # Update checker timer (check once per launch + periodically)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_for_updates)
        
        self.init_ui()
        self.start_background_scanner()
        self.check_for_updates()  # Check on startup

    def closeEvent(self, event):
        """Handle window close event."""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()
    
    def init_ui(self):
        """Initialize main UI layout."""
        self.setWindowTitle("HidenLogick Launcher")
        self.setFixedSize(1100, 700)
        self.setStyleSheet(styles.MAIN_STYLE)

        container = QWidget()
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # LEFT SIDEBAR - INSTALLED VERSIONS
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet(styles.SIDEBAR_STYLE)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(15, 15, 15, 15)
        self.sidebar_collor = QColor("#0f0f0f")
        self.sidebar.setStyleSheet(f"background-color: {self.sidebar_collor.name()}; border-right: 1px solid #1a1a1a;")

        # Logo section
        logo_path = os.path.join(self.bin_dir, "assets", "miniatures", "minecraft.png")
        if os.path.exists(logo_path):
            try:
                logo_l = QLabel()
                pix = QPixmap(logo_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                if not pix.isNull():
                    logo_l.setPixmap(pix)
                    logo_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.sidebar_layout.addWidget(logo_l)
            except:
                pass
        
        # Installed title
        installed_title = QLabel("INSTALLED VERSIONS")
        installed_title.setStyleSheet("color: #0078d4; font-size: 12px; font-weight: bold; margin-top: 15px;")
        self.sidebar_layout.addWidget(installed_title)

        # Manual import button
        self.import_btn = QPushButton("Import from other launchers")
        self.import_btn.setStyleSheet("""
            QPushButton { background-color: #333; color: white; border-radius: 6px; padding: 6px; font-size: 11px; }
            QPushButton:hover { background-color: #444; }
        """)
        self.import_btn.clicked.connect(self.manual_import_trigger)
        self.sidebar_layout.addWidget(self.import_btn)

        # Manual folder import button
        self.import_folder_btn = QPushButton("Import from folder...")
        self.import_folder_btn.setStyleSheet("""
            QPushButton { background-color: #333; color: white; border-radius: 6px; padding: 6px; font-size: 11px; }
            QPushButton:hover { background-color: #444; }
        """)
        self.import_folder_btn.clicked.connect(self.manual_import_from_folder)
        self.sidebar_layout.addWidget(self.import_folder_btn)

        # Settings button
        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.setStyleSheet("""
            QPushButton { background-color: #333; color: white; border-radius: 6px; padding: 6px; font-size: 11px; }
            QPushButton:hover { background-color: #444; }
        """)
        self.settings_btn.clicked.connect(self.show_settings_dialog)
        self.sidebar_layout.addWidget(self.settings_btn)
        
        # Search filter
        search_label = QLabel("SEARCH VERSIONS")
        search_label.setStyleSheet("color: #0078d4; font-size: 11px; font-weight: bold; margin-top: 10px;")
        self.sidebar_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter by version/player...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #111;
                color: white;
                padding: 8px;
                border: 1px solid #333;
                border-radius: 4px;
                font-size: 10px;
            }
            QLineEdit:focus { border: 1px solid #0078d4; }
        """)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.sidebar_layout.addWidget(self.search_input)
        
        # Scroll area for installed versions
        scroll = QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #111;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #333;
                border-radius: 4px;
            }
        """)
        scroll.setWidgetResizable(True)
        
        # Container for cards
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(5)
        
        scroll.setWidget(self.cards_container)
        self.sidebar_layout.addWidget(scroll)
        
        self.sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        # CENTER AREA - CONTENT
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(15)
        main_layout.addWidget(self.content_widget)
        
        # Add stats dashboard
        self.add_stats_dashboard()
        
        # Divider
        divider = QFrame()
        divider.setStyleSheet("background-color: #333; height: 1px;")
        divider.setFixedHeight(1)
        self.content_layout.addWidget(divider)
        
        # Create and add installation card
        self.installation_card = InstallationCard()
        self.installation_card.btn_start.clicked.connect(self.on_installation_start)
        self.content_layout.addWidget(self.installation_card)
        
        self.content_layout.addStretch()
        
        self.setCentralWidget(container)
        self.setup_installation_card()
        self.refresh_installed_cards()
        # Offer to detect/import at startup (only if configured)
        if self.config.get("auto_import_on_startup", False):
            self.auto_import_at_startup_silent()
        else:
            self.offer_import_at_startup()

    def refresh_installed_cards(self):
        """Refresh installed versions cards with search filter applied."""
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add installed cards
        installations = self.storage.get_installations()
        filtered_installations = []
        
        if installations:
            # Apply search filter
            for inst in installations:
                search_text = self.search_filter
                version_match = search_text in inst['version'].lower()
                username_match = search_text in inst['username'].lower()
                
                if search_text == "" or version_match or username_match:
                    filtered_installations.append(inst)
            
            if filtered_installations:
                for inst in filtered_installations:
                    card = InstalledVersionCard(inst['version'], inst['username'])
                    card.play_clicked.connect(self.on_play_installed)
                    card.delete_clicked.connect(self.on_delete_installation)
                    self.cards_layout.addWidget(card)
            else:
                no_match = QLabel("No versions match search")
                no_match.setStyleSheet("color: #666; font-size: 11px;")
                no_match.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.cards_layout.addWidget(no_match)
        else:
            no_inst = QLabel("No installed versions yet")
            no_inst.setStyleSheet("color: #666; font-size: 11px;")
            no_inst.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.addWidget(no_inst)
        
        self.cards_layout.addStretch()

    def on_play_installed(self, version: str, username: str):
        """Play installed version."""
        if self.is_launching or self.is_installing:
            return
        
        self.is_launching = True
        self.append_log(f"🚀 Launching {username} on v{version}...", "#00aaff")
        
        # Update Discord RPC
        try:
            profile = "Vanilla"  # Could get actual profile from selection
            self.discord_rpc.update_playing(version, username, profile)
        except:
            pass
        
        # Start performance metrics monitoring
        self.performance_metrics.start_monitoring()
        
        worker = LaunchWorker(self.engine, version, username)
        worker.log.connect(self.append_log)
        worker.finished.connect(lambda s: self.on_launch_finished(s))
        worker.start()
        self.worker = worker

    def on_launch_finished(self, success: bool):
        """Handle launch completion."""
        self.is_launching = False
        
        # Stop performance metrics
        self.performance_metrics.stop_monitoring()
        
        # Update Discord RPC back to launcher
        try:
            self.discord_rpc.update_launcher("Ready")
        except:
            pass
        
        if success:
            self.append_log("✅ Game launched successfully!", "#00ff00")
        else:
            self.append_log("❌ Failed to launch game", "red")

    def on_delete_installation(self, version: str, username: str):
        """Delete installation record and all game files + mod profiles."""
        reply = QMessageBox.question(
            self, "Delete Installation",
            f"Remove v{version} ({username}) from library?\nAll game files and mod profiles will be DELETED.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            import shutil
            try:
                # Delete version directory with all files
                version_path = os.path.join(self.engine.game_dir, "versions", version)
                if os.path.exists(version_path):
                    shutil.rmtree(version_path)
                    self.append_log(f"🗑️ Deleted files for v{version}", "#888")
                
                # Delete all mod profiles for this version
                self.mod_profiler.delete_all_profiles(version)
                self.append_log(f"🗑️ Deleted mod profiles for v{version}", "#888")
            except Exception as e:
                self.append_log(f"❌ Error deleting files: {str(e)}", "red")
            
            # Remove from installation storage
            self.storage.remove_installation(version, username)
            self.refresh_installed_cards()
            self.append_log(f"✓ Removed v{version} ({username})", "#888")

    def on_import_finished(self):
        """Called when import finishes."""
        self.refresh_installed_cards()
        # Show toast notification if configured
        if hasattr(self, 'notify') and self.notify:
            self.notify.show_toast("✓ Import completed", duration=3000)
        """Detect third-party versions and offer import at startup."""
        try:
            detected = self.engine.detect_all_versions_in_system()
            if not detected:
                return

            # Build summary
            lines = []
            total = 0
            for p, versions in detected.items():
                lines.append(f"Source: {p}")
                for v in versions:
                    lines.append(f"  - {v}")
                total += len(versions)

            msg = "Detected the following versions in other launchers:\n\n" + "\n".join(lines) + f"\n\nImport {total} versions into HidenLogick?"
            reply = QMessageBox.question(self, "Import detected versions", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                # perform safe import in background with progress
                from bin.progress_window import ProgressWindow
                pw = ProgressWindow("Importing versions", self)
                pw.set_label("Preparing import...")

                worker = ImportWorker(self.engine, list(detected.keys()), self.storage, username='imported')

                def on_progress(idx, total, name, ok):
                    pw.set_label(f"Importing {name} ({idx}/{total})")
                    percent = int((idx / total) * 100) if total else 0
                    pw.set_progress(percent)
                    pw.append_log(f"{name}: {'imported' if ok else 'skipped/failed'} ({idx}/{total})")

                def on_finished_map(result_map):
                    pw.append_log("Import finished")
                    pw.enable_close()
                    if result_map:
                        for src, items in result_map.items():
                            for it in items:
                                self.append_log(f"Imported {it} from {src}", "#00aa00")
                        self.refresh_installed_cards()

                worker.progress.connect(on_progress)
                worker.log.connect(lambda t: pw.append_log(t))
                worker.finished.connect(on_finished_map)
                worker.start()
                pw.exec()
        except Exception:
            pass

    def manual_import_trigger(self):
        """User-triggered import flow: detect -> confirm -> import."""
        try:
            detected = self.engine.detect_all_versions_in_system()
            if not detected:
                QMessageBox.information(self, "No external installations", "No other launchers or Minecraft folders detected.")
                return

            # Build short summary
            lines = []
            total = 0
            for p, versions in detected.items():
                lines.append(f"{os.path.basename(p)}: {len(versions)} versions")
                total += len(versions)

            msg = "Found external versions:\n\n" + "\n".join(lines) + f"\n\nImport all {total} versions now?"
            reply = QMessageBox.question(self, "Import external versions", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                from bin.progress_window import ProgressWindow
                pw = ProgressWindow("Importing versions", self)
                pw.set_label("Preparing import...")

                worker = ImportWorker(self.engine, list(detected.keys()), self.storage, username='imported')

                def on_progress(idx, total, name, ok):
                    pw.set_label(f"Importing {name} ({idx}/{total})")
                    percent = int((idx / total) * 100) if total else 0
                    pw.set_progress(percent)
                    pw.append_log(f"{name}: {'imported' if ok else 'skipped/failed'} ({idx}/{total})")

                def on_finished_map(result_map):
                    pw.append_log("Import finished")
                    pw.enable_close()
                    if result_map:
                        self.refresh_installed_cards()
                        for src, items in result_map.items():
                            for it in items:
                                self.append_log(f"Imported {it} from {src}", "#00aa00")
                    else:
                        QMessageBox.information(self, "Import complete", "No new versions were imported (already present or none found).")

                worker.progress.connect(on_progress)
                worker.log.connect(lambda t: pw.append_log(t))
                worker.finished.connect(on_finished_map)
                worker.start()
                pw.exec()
        except Exception as e:
            QMessageBox.warning(self, "Import error", f"Import failed: {e}")

    def show_settings_dialog(self):
        """Open settings dialog."""
        from bin.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.config, self)
        dialog.exec()
        # Refresh UI in case settings changed
        self.refresh_installed_cards()

    def auto_import_at_startup_silent(self):
        """Auto-import without prompting user (runs in background)."""
        versions_found = self.engine.detect_all_versions_in_system()
        if versions_found:
            # Run import in background without user interaction
            self.import_worker = ImportWorker(
                destinations=list(versions_found.keys()),
                storage=self.storage,
                engine=self.engine
            )
            self.import_worker.progress.connect(self.on_import_progress)
            self.import_worker.finished.connect(self.on_import_finished)
            self.import_worker.start()

    def manual_import_from_folder(self):
        """Allow the user to pick a folder and import versions from it."""
        folder = QFileDialog.getExistingDirectory(self, "Select folder to import from")
        if not folder:
            return

        # Detect versions in chosen folder
        found = self.engine.detect_versions_in_path(folder)
        if not found:
            QMessageBox.information(self, "No versions found", "No Minecraft versions were detected in the selected folder.")
            return

        # Ask user to confirm which versions to import
        lines = [f"{v}" for v in found]
        msg = "Found the following versions:\n\n" + "\n".join(lines) + f"\n\nImport all {len(found)} versions from this folder?"
        reply = QMessageBox.question(self, "Import from folder", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Run import with progress window
        from bin.progress_window import ProgressWindow
        pw = ProgressWindow("Importing from folder", self)
        pw.set_label("Preparing import...")

        worker = ImportWorker(self.engine, [folder], self.storage, username='imported')

        def on_progress(idx, total, name, ok):
            pw.set_label(f"Importing {name} ({idx}/{total})")
            percent = int((idx / total) * 100) if total else 0
            pw.set_progress(percent)
            pw.append_log(f"{name}: {'imported' if ok else 'skipped/failed'} ({idx}/{total})")

        def on_finished_map(result_map):
            pw.append_log("Import finished")
            pw.enable_close()
            if result_map:
                self.refresh_installed_cards()
                # Show notification
                if hasattr(self, 'notify') and self.notify:
                    self.notify.show_toast("✓ Import completed", duration=3000)
                for src, items in result_map.items():
                    for it in items:
                        self.append_log(f"Imported {it} from {src}", "#00aa00")

        worker.progress.connect(on_progress)
        worker.log.connect(lambda t: pw.append_log(t))
        worker.finished.connect(on_finished_map)
        worker.start()
        pw.exec()

    def setup_installation_card(self):
        """Initialize the installation card with available versions."""
        versions = self.engine.get_all_versions()
        self.installation_card.ver_combo.addItems(versions)
    
    def on_installation_start(self):
        """Handle installation start button press."""
        self.start_install_process()

    def append_log(self, text, color):
        """Add timestamped log entry to installation card."""
        self.installation_card.append_log(text, color)
        self.log_view.ensureCursorVisible()

    def handle_progress(self, value):
        """Update progress bar (reset on phase change)."""
        if value < self.last_progress:
            self.installation_card.p_bar.reset()
        self.installation_card.set_progress(value)
        self.last_progress = value

    def start_install_process(self):
        """Start installation process with validation."""
        if self.is_installing or self.is_launching:
            self.append_log("❌ Operation already in progress", "#ffaa00")
            return
        
        nick = self.installation_card.nick_input.text().strip()
        if not nick or len(nick) < 3:
            self.append_log("❌ Nickname must be 3+ characters", "red")
            return
        
        if len(nick) > 32:
            self.append_log("❌ Nickname must be 32 characters or less", "red")
            return

        version = self.installation_card.ver_combo.currentText()
        if not version:
            self.append_log("❌ No version selected", "red")
            return
        
        self.is_installing = True
        self.installation_card.set_installing(True)
        self.last_progress = 0
        self.installation_card.clear_log()
        self.installation_card.show_progress()
        
        self.append_log(f"📥 Installing Minecraft v{version} for {nick}", "#00aaff")
        
        self.worker = InstallWorker(self.engine, version)
        self.worker.progress.connect(self.handle_progress)
        self.worker.log.connect(self.append_log)
        self.worker.finished.connect(lambda s: self.on_finished(s, version, nick))
        self.worker.start()

    def on_finished(self, success, version, nick):
        """Handle installation completion."""
        self.is_installing = False
        self.installation_card.set_installing(False)
        self.installation_card.hide_progress()
        
        if success:
            self.append_log("✅ Installation complete!", "#00ff00")
            self.storage.add_installation(version, nick)
            self.refresh_installed_cards()
            self.append_log(f"🎮 Ready to play! Click PLAY in the sidebar.", "#00aa00")
        else:
            self.append_log("❌ Installation failed", "red")

    def on_import_progress(self, idx, total, name, ok):
        """Handle import progress (called from auto-import)."""
        pass  # Silent background import, no UI feedback needed

    def on_import_finished(self, result_map):
        """Called when silent import finishes."""
        if result_map:
            self.refresh_installed_cards()
            # Show notification
            if hasattr(self, 'notify') and self.notify:
                total = sum(len(items) for items in result_map.values())
                self.notify.show_toast(f"✓ Auto-imported {total} version(s)", duration=3000)

    def offer_import_at_startup(self):
        """Ask user if they want to import external versions on app startup."""
        try:
            versions_found = self.engine.detect_all_versions_in_system()
            if not versions_found:
                return
            
            total = sum(len(v) for v in versions_found.values())
            msg = f"Found {total} Minecraft version(s) from other sources.\n\nWould you like to import them?"
            reply = QMessageBox.question(
                self,
                "Import external versions?",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.manual_import_trigger()
        except Exception:
            pass  # Silent fail on startup

    def add_stats_dashboard(self):
        """Add stats dashboard showing storage, versions, etc."""
        installations = self.storage.get_installations()
        num_versions = len(installations)
        
        # Calculate total storage used
        import_path = os.path.join(self.root_dir, 'games', 'Minecraft', 'ac.game', 'versions')
        total_size_bytes = 0
        if os.path.exists(import_path):
            for dirpath, _, filenames in os.walk(import_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size_bytes += os.path.getsize(fp)
        
        # Convert to GB
        total_size_gb = total_size_bytes / (1024**3)
        
        # Create stats frame
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 10, 15, 10)
        stats_layout.setSpacing(30)
        
        # Version count
        ver_stat = QLabel(f"📦 Versions: {num_versions}")
        ver_stat.setStyleSheet("color: #0078d4; font-size: 12px; font-weight: bold;")
        stats_layout.addWidget(ver_stat)
        
        # Storage used
        storage_stat = QLabel(f"💾 Storage: {total_size_gb:.2f} GB")
        storage_stat.setStyleSheet("color: #00aaff; font-size: 12px; font-weight: bold;")
        stats_layout.addWidget(storage_stat)
        
        # Player count
        player_count = len(set(inst['username'] for inst in installations))
        player_stat = QLabel(f"👤 Players: {player_count}")
        player_stat.setStyleSheet("color: #00dd00; font-size: 12px; font-weight: bold;")
        stats_layout.addWidget(player_stat)
        
        stats_layout.addStretch()
        
        self.content_layout.addWidget(stats_frame)

    def on_search_text_changed(self, text):
        """Filter installed versions by search text."""
        self.search_filter = text.lower()
        self.refresh_installed_cards()

    def start_background_scanner(self):
        """Start background scanner if enabled in config."""
        if self.config.get("enable_scanner", False):
            scan_interval = self.config.get("scan_interval_minutes", 30)
            # Convert minutes to milliseconds
            interval_ms = scan_interval * 60 * 1000
            self.scanner_timer.start(interval_ms)

    def background_scanner_tick(self):
        """Periodic background scan for new installations."""
        try:
            versions_found = self.engine.detect_all_versions_in_system()
            if versions_found:
                # Check if any new versions exist
                current = self.storage.get_installations()
                current_versions = {inst['version']: inst for inst in current}
                
                new_count = 0
                for path, versions in versions_found.items():
                    for v in versions:
                        if v not in current_versions:
                            new_count += 1
                            # Auto-import new version
                            try:
                                self.engine.import_versions_from_path(
                                    path,
                                    self.storage,
                                    username='scanned'
                                )
                            except:
                                pass
                
                if new_count > 0:
                    self.refresh_installed_cards()
                    if hasattr(self, 'notify') and self.notify:
                        self.notify.show_toast(f"✓ Scanner found {new_count} new version(s)", duration=3000)
        except Exception:
            pass

    def check_for_updates(self):
        """Check for app updates from GitHub."""
        try:
            update_available, update_info = self.update_checker.check_for_updates()
            
            if update_available:
                # Show update notification
                msg = f"HidenLogick v{update_info['version']} is available!"
                reply = QMessageBox.information(
                    self,
                    "Update Available",
                    f"{msg}\n\n{update_info['changelog'][:200]}...",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Ok and update_info.get('url'):
                    import webbrowser
                    webbrowser.open(update_info['url'])
                
                if hasattr(self, 'notify') and self.notify:
                    self.notify.show_toast(f"📦 Update available: v{update_info['version']}", duration=5000)
        except Exception as e:
            print(f"Update check error: {e}")
    
    def setup_discord(self, app_id: str = "1234567890"):
        """Setup Discord RPC with custom app ID."""
        try:
            from bin.discord_rpc import init_discord_rpc
            if init_discord_rpc(app_id):
                self.discord_rpc.update_launcher("Idle")
                self.append_log("✅ Discord RPC connected", "#00ff00")
                return True
        except ImportError:
            print("pypresence not installed for Discord RPC")
        except Exception as e:
            print(f"Discord RPC setup failed: {e}")
        return False
    
    def show_performance_overlay(self):
        """Show/hide performance metrics overlay."""
        overlay = PerformanceOverlay(self.performance_metrics)
        overlay.toggle()
        self.append_log(f"Performance overlay {'enabled' if overlay.visible else 'disabled'}", "#0078d4")