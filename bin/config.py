"""Simple JSON-backed configuration for HidenLogick."""
import json
import os
from typing import Any


class Config:
    DEFAULTS = {
        "auto_import_on_startup": False,
        "scan_interval_minutes": 15,
        "backup_copies": True
    }

    def __init__(self, root_dir: str):
        self.path = os.path.join(root_dir, "bin", "config.json")
        self._data = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except Exception:
                self._data = dict(self.DEFAULTS)
        else:
            self._data = dict(self.DEFAULTS)
            self._save()

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get(self, key: str, default: Any = None):
        return self._data.get(key, self.DEFAULTS.get(key, default))

    def set(self, key: str, value: Any):
        self._data[key] = value
        self._save()
