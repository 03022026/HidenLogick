"""Premium styling module for HidenLogick Launcher - Better than TLauncher."""

MAIN_STYLE = """
    QMainWindow {
        background-color: #0d0d0d;
        font-family: 'Segoe UI', sans-serif;
    }
"""
SIDEBAR_STYLE = """
    QFrame {
        background-color: #0f0f0f;
        border-right: 1px solid #1a1a1a;
    }
"""

PLAY_BUTTON_STYLE = """
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 13px;
        padding: 12px 24px;
        min-height: 45px;
    }
    QPushButton:hover {
        background-color: #1084d8;
        margin-top: 0px;
    }
    QPushButton:pressed {
        background-color: #005a9e;
        margin-top: 1px;
    }
    QPushButton:disabled {
        background-color: #444444;
        color: #888888;
    }
"""

INSTALL_BUTTON_STYLE = """
    QPushButton {
        background-color: #2e7d32;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 13px;
        padding: 12px 24px;
        min-height: 45px;
    }
    QPushButton:hover { background-color: #388e3c; }
    QPushButton:pressed { background-color: #1e5222; }
    QPushButton:disabled { background-color: #444444; color: #888888; }
"""

NEWS_TITLE = "color: #0078d4; font-size: 20px; font-weight: bold; margin-bottom: 5px;"
NEWS_TEXT = "color: #bbbbbb; font-size: 14px; line-height: 1.4;"

# Error states
ERROR_STYLE = "color: #ff4444; font-weight: bold;"
SUCCESS_STYLE = "color: #00ff00; font-weight: bold;"
WARNING_STYLE = "color: #ffaa00; font-weight: bold;"