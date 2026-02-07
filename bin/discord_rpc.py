"""Discord Rich Presence integration."""
import os
import time
from datetime import datetime


class DiscordRPC:
    """Discord Rich Presence for showing game status."""
    
    CLIENT_ID = "YOUR_DISCORD_APP_ID"  # Replace with actual Discord app ID
    
    def __init__(self):
        self.connected = False
        self.client = None
        self._import_pypresence()
    
    def _import_pypresence(self):
        """Try to import pypresence library."""
        try:
            from pypresence import Presence
            self.Presence = Presence
        except ImportError:
            self.Presence = None
            print("pypresence not installed. Discord RPC disabled. Install with: pip install pypresence")
    
    def connect(self) -> bool:
        """Connect to Discord."""
        if not self.Presence:
            return False
        
        try:
            self.client = self.Presence(self.CLIENT_ID)
            self.client.connect()
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to Discord: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Discord."""
        if self.client and self.connected:
            try:
                self.client.clear()
                self.client.close()
            except:
                pass
            self.connected = False
    
    def update_playing(self, version: str, username: str, profile: str = "Vanilla"):
        """Update Discord presence with current game info.
        
        Args:
            version: Minecraft version (e.g., "1.20.1")
            username: Player username
            profile: Launch profile name
        """
        if not self.connected or not self.client:
            return
        
        try:
            self.client.update(
                state=f"Player: {username}",
                details=f"Version: {version} ({profile})",
                large_image="minecraft",
                large_text="HidenLogick Launcher",
                small_image="hiden_logick",
                small_text="Playing Minecraft",
                start=int(time.time())
            )
        except Exception as e:
            print(f"Failed to update Discord presence: {e}")
    
    def update_installing(self, version: str):
        """Update Discord presence while installing.
        
        Args:
            version: Minecraft version being installed
        """
        if not self.connected or not self.client:
            return
        
        try:
            self.client.update(
                state=f"Installing v{version}",
                details="Setting up Minecraft",
                large_image="minecraft",
                large_text="HidenLogick Launcher",
                small_image="hiden_logick",
                small_text="Installing",
                start=int(time.time())
            )
        except Exception as e:
            print(f"Failed to update Discord presence: {e}")
    
    def update_launcher(self, status: str = "Idle"):
        """Update Discord presence at launcher idle state.
        
        Args:
            status: Status message
        """
        if not self.connected or not self.client:
            return
        
        try:
            self.client.update(
                state="At Launcher",
                details=status,
                large_image="minecraft",
                large_text="HidenLogick Launcher",
                small_image="hiden_logick",
                small_text="Idle"
            )
        except Exception as e:
            print(f"Failed to update Discord presence: {e}")
    
    def clear(self):
        """Clear Discord presence."""
        if self.connected and self.client:
            try:
                self.client.clear()
            except:
                pass


# Singleton instance
_rpc_instance = None


def get_discord_rpc() -> DiscordRPC:
    """Get or create Discord RPC instance."""
    global _rpc_instance
    if _rpc_instance is None:
        _rpc_instance = DiscordRPC()
    return _rpc_instance


def init_discord_rpc(app_id: str) -> bool:
    """Initialize Discord RPC with custom app ID.
    
    Args:
        app_id: Your Discord application ID
    
    Returns:
        True if connected successfully
    """
    rpc = get_discord_rpc()
    rpc.CLIENT_ID = app_id
    return rpc.connect()
