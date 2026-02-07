"""Persistent storage for installed versions."""
import json
import os
from typing import List, Dict

class InstallationStorage:
    """Manage installed versions and player data."""
    
    def __init__(self, root_dir):
        self.storage_path = os.path.join(root_dir, "bin", "data.json")
        self.installations = self._load()
    
    def _load(self) -> List[Dict]:
        """Load installations from JSON."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save(self):
        """Save installations to JSON."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.installations, f, indent=2)
        except Exception as e:
            print(f"Failed to save installations: {e}")
    
    def add_installation(self, version: str, username: str) -> bool:
        """Add installation record."""
        if not version or not username:
            return False
        
        # Check if already exists
        for inst in self.installations:
            if inst['version'] == version and inst['username'] == username:
                return True
        
        self.installations.append({
            'version': version,
            'username': username,
            'installed_at': self._get_timestamp()
        })
        self._save()
        return True
    
    def get_installations(self) -> List[Dict]:
        """Get all installations."""
        return self.installations
    
    def remove_installation(self, version: str, username: str) -> bool:
        """Remove installation record."""
        original_len = len(self.installations)
        self.installations = [
            inst for inst in self.installations 
            if not (inst['version'] == version and inst['username'] == username)
        ]
        if len(self.installations) < original_len:
            self._save()
            return True
        return False
    
    @staticmethod
    def _get_timestamp():
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
