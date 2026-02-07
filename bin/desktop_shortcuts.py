"""Create desktop shortcuts for quick version launching."""
import os
import sys
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import win32com.client  # type: ignore


class DesktopShortcut:
    """Create Windows .lnk shortcuts for launching versions."""
    
    @staticmethod
    def create_launcher_shortcut(version: str, username: str, launcher_path: str) -> bool:
        """Create a desktop shortcut for launching a Minecraft version.
        
        Args:
            version: Minecraft version (e.g., "1.20.1")
            username: Player username
            launcher_path: Path to aplication.py
        
        Returns:
            True if shortcut created successfully, False otherwise
        """
        try:
            import win32com.client
        except ImportError:
            # pywin32 not installed, skip shortcut creation
            return False
        
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / f"Minecraft {version} ({username}).lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            
            # Set shortcut properties
            python_exe = os.sys.executable
            shortcut.TargetPath = python_exe
            shortcut.Arguments = f'"{launcher_path}"'
            shortcut.WorkingDirectory = os.path.dirname(launcher_path)
            shortcut.IconLocation = os.path.join(os.path.dirname(launcher_path), "assets", "icon.ico")
            shortcut.Description = f"Launch Minecraft {version} as {username}"
            
            shortcut.save()
            return True
        except Exception as e:
            print(f"Failed to create shortcut: {e}")
            return False
    
    @staticmethod
    def create_settings_shortcut(launcher_path: str) -> bool:
        """Create a desktop shortcut for launcher settings."""
        try:
            import win32com.client
        except ImportError:
            return False
        
        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "HidenLogick Settings.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            
            python_exe = os.sys.executable
            shortcut.TargetPath = python_exe
            shortcut.Arguments = f'"{launcher_path}"'
            shortcut.WorkingDirectory = os.path.dirname(launcher_path)
            shortcut.Description = "Open HidenLogick Launcher Settings"
            
            shortcut.save()
            return True
        except Exception:
            return False
    
    @staticmethod
    def remove_shortcut(shortcut_name: str) -> bool:
        """Remove a shortcut from desktop."""
        try:
            desktop = Path.home() / "Desktop" / f"{shortcut_name}.lnk"
            if desktop.exists():
                desktop.unlink()
                return True
        except Exception:
            pass
        return False
    
    @staticmethod
    def get_desktop_shortcuts() -> list:
        """Get all HidenLogick shortcuts on desktop."""
        try:
            desktop = Path.home() / "Desktop"
            shortcuts = [
                f.stem for f in desktop.glob("Minecraft *.lnk")
                if f.stem.startswith("Minecraft")
            ]
            return shortcuts
        except Exception:
            return []


class StartMenuShortcut:
    """Create/manage shortcuts in Windows Start Menu."""
    
    @staticmethod
    def create_start_menu_shortcut(launcher_path: str) -> bool:
        """Create Start Menu shortcut for HidenLogick."""
        try:
            import win32com.client
        except ImportError:
            return False
        
        try:
            # Get StartMenu path
            start_menu = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            start_menu.mkdir(parents=True, exist_ok=True)
            
            shortcut_path = start_menu / "HidenLogick Launcher.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            
            python_exe = os.sys.executable
            shortcut.TargetPath = python_exe
            shortcut.Arguments = f'"{launcher_path}"'
            shortcut.WorkingDirectory = os.path.dirname(launcher_path)
            shortcut.Description = "HidenLogick - Premium Minecraft Launcher"
            
            shortcut.save()
            return True
        except Exception:
            return False
