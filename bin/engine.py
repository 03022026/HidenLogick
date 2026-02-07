import os
import shutil
import minecraft_launcher_lib
import subprocess
import uuid
import time
import socket
from datetime import datetime, timedelta

class GameEngine:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.game_dir = os.path.join(self.root_dir, "games", "Minecraft", "ac.game")
        self.version_cache = None
        self.cache_time = None
        self.cache_duration = timedelta(hours=1)
        
        os.makedirs(self.game_dir, exist_ok=True)

    def get_all_versions(self):
        """Get cached Minecraft versions with fallback."""
        # Check cache
        if self.version_cache and self.cache_time:
            if datetime.now() - self.cache_time < self.cache_duration:
                return self.version_cache
        
        try:
            socket.setdefaulttimeout(10)  # 10 second timeout
            versions = [v['id'] for v in minecraft_launcher_lib.utils.get_version_list() if v['type'] == 'release'][:15]
            self.version_cache = versions
            self.cache_time = datetime.now()
            return versions
        except (socket.timeout, ConnectionError, Exception):
            # Return cached or fallback versions
            if self.version_cache:
                return self.version_cache
            return ["1.21.1", "1.20.1", "1.16.5"]

    def install(self, version, progress_callback, log_callback):
        """Install Minecraft version with retry and timeout logic."""
        # Validate inputs
        if not version or not isinstance(version, str):
            log_callback("❌ Invalid version specified", "red")
            return False
        
        def set_status(text):
            """Format installation status messages."""
            if len(text) == 40 and all(c in "0123456789abcdef" for c in text.lower()):
                log_callback(f"[RES] Asset: {text[:8]}...", "#555555")
            else:
                log_callback(f"[STATUS] {text}", "#00aaff")

        callback = {
            "setStatus": set_status,
            "setProgress": lambda v: progress_callback(v),
            "setMax": lambda v: log_callback(f"[SYSTEM] Task size: {v} files", "#ffaa00")
        }
        
        max_retries = 5
        attempt = 0
        base_wait = 2  # Base wait time in seconds
        
        while attempt < max_retries:
            try:
                log_callback(f"🚀 ATTEMPT {attempt + 1}/{max_retries}: Installing Minecraft {version}", "white")
                socket.setdefaulttimeout(30)  # 30 second timeout
                
                minecraft_launcher_lib.install.install_minecraft_version(
                    version=version,
                    minecraft_directory=self.game_dir,
                    callback=callback
                )
                log_callback("✅ INSTALLATION COMPLETE!", "#00ff00")
                return True
                
            except Exception as e:
                attempt += 1
                error_msg = str(e)
                
                # Handle connection issues with exponential backoff
                if any(x in error_msg for x in ["10054", "Connection aborted", "ConnectionError", "timeout"]):
                    if attempt < max_retries:
                        wait_time = base_wait * (2 ** (attempt - 1))  # Exponential backoff
                        log_callback("🛑 Connection error detected", "#ff4444")
                        log_callback(f"⚠️ Waiting {wait_time}s before retry {attempt}/{max_retries}...", "#ffaa00")
                        time.sleep(wait_time)
                    else:
                        log_callback("💀 Max retries reached. Connection issues persist.", "red")
                        return False
                else:
                    log_callback(f"❌ FATAL ERROR: {error_msg}", "red")
                    return False
        
        return False

    def launch(self, version, username):
        """Launch Minecraft with validation."""
        if not version or not username:
            return False
        
        username = username.strip()
        if not username or len(username) < 3:
            return False
        
        options = {
            "username": username,
            "uuid": str(uuid.uuid4()),
            "token": ""
        }
        
        try:
            command = minecraft_launcher_lib.command.get_minecraft_command(version, self.game_dir, options)
            subprocess.Popen(command)
            return True
        except Exception as e:
            return False
    
    def is_version_installed(self, version: str) -> bool:
        """Check if version is already installed."""
        try:
            version_dir = os.path.join(self.game_dir, "versions", version)
            return os.path.exists(version_dir)
        except:
            return False

    def list_installed_versions(self) -> list:
        """Return a list of installed Minecraft versions found in the game directory.

        Looks under <game_dir>/versions and returns the folder names that look like
        installed versions. Returns an empty list if none found.
        """
        versions_root = os.path.join(self.game_dir, "versions")
        if not os.path.isdir(versions_root):
            return []

        try:
            entries = os.listdir(versions_root)
            found = [e for e in entries if os.path.isdir(os.path.join(versions_root, e))]
            return sorted(found)
        except Exception:
            return []

    def find_installed_version(self, query: str) -> list:
        """Find installed versions matching the given query.

        - If `query` matches a version exactly, that version is returned.
        - Otherwise, performs a case-insensitive substring search across
          installed version folder names and returns all matches.
        - Returns an empty list when no matches found.
        """
        if not query or not isinstance(query, str):
            return []

        query = query.strip()
        installed = self.list_installed_versions()
        # Exact match first
        if query in installed:
            return [query]

        qlow = query.lower()
        matches = [v for v in installed if qlow in v.lower()]
        return matches

    def find_installed_by_username(self, storage, username: str) -> list:
        """Optional helper: find installed versions for a given username using `storage`.

        `storage` should implement `get_installations()` returning a list of
        records with keys `version` and `username` (this matches `InstallationStorage`).
        Returns a list of versions associated with the username (may be empty).
        """
        if storage is None or not username:
            return []

        try:
            results = [r['version'] for r in storage.get_installations() if r.get('username', '').lower() == username.lower()]
            return results
        except Exception:
            return []

    def locate_system_installations(self) -> list:
        """Locate likely existing Minecraft/TLauncher installation folders on this system.

        Returns a list of absolute paths that look like launchers or Minecraft folders.
        This function is conservative and only checks common user folders (APPDATA and home).
        """
        candidates = []
        appdata = os.getenv('APPDATA')
        home = os.path.expanduser('~')

        paths_to_check = []
        if appdata:
            paths_to_check.append(os.path.join(appdata, '.minecraft'))
            paths_to_check.append(os.path.join(appdata, '.tlauncher'))
            paths_to_check.append(os.path.join(appdata, 'tlauncher'))
        if home:
            paths_to_check.append(os.path.join(home, '.minecraft'))

        # add any tlauncher-like folders under APPDATA
        if appdata and os.path.isdir(appdata):
            try:
                for name in os.listdir(appdata):
                    if 'tlauncher' in name.lower():
                        p = os.path.join(appdata, name)
                        if os.path.isdir(p):
                            paths_to_check.append(p)
            except Exception:
                pass

        for p in paths_to_check:
            if p and os.path.isdir(p):
                if p not in candidates:
                    candidates.append(p)

        return candidates

    def import_versions_from_path(self, src_path: str, storage=None, username: str = None, progress_callback=None) -> list:
        """Import version folders from a source Minecraft-like path into this launcher's versions.

        - Searches for a `versions` folder under `src_path`, `src_path/.minecraft`, and `src_path/minecraft`.
        - Copies any missing version directories into `<self.game_dir>/versions`.
        - Optionally registers each imported version in `storage` via `add_installation(version, username)`.

        Returns a list of imported version names.
        """
        if not src_path or not os.path.isdir(src_path):
            return []

        candidates = [src_path, os.path.join(src_path, '.minecraft'), os.path.join(src_path, 'minecraft')]
        src_versions = None
        for root in candidates:
            vroot = os.path.join(root, 'versions')
            if os.path.isdir(vroot):
                src_versions = vroot
                break

        if not src_versions:
            return []

        dest_versions_root = os.path.join(self.game_dir, 'versions')
        os.makedirs(dest_versions_root, exist_ok=True)

        imported = []
        try:
            all_names = [n for n in os.listdir(src_versions) if os.path.isdir(os.path.join(src_versions, n))]
            total = len(all_names)
            idx = 0
            for name in all_names:
                idx += 1
                src_dir = os.path.join(src_versions, name)
                dest_dir = os.path.join(dest_versions_root, name)
                if os.path.exists(dest_dir):
                    # already present -> skip
                    if progress_callback:
                        try:
                            progress_callback(idx, total, name, False)
                        except Exception:
                            pass
                    continue

                try:
                    shutil.copytree(src_dir, dest_dir)
                    imported.append(name)
                    # register in storage when provided
                    if storage is not None:
                        try:
                            storage.add_installation(name, username or 'imported')
                        except Exception:
                            pass
                    if progress_callback:
                        try:
                            progress_callback(idx, total, name, True)
                        except Exception:
                            pass
                except Exception:
                    # If copy fails for a version, continue with others
                    if progress_callback:
                        try:
                            progress_callback(idx, total, name, False)
                        except Exception:
                            pass
                    continue
        except Exception:
            return imported

        return imported

    def detect_and_import_third_party(self, storage=None) -> dict:
        """Detect common third-party launchers (e.g., TLauncher) and import versions.

        Returns a dict mapping detected source paths to lists of imported versions.
        """
        results = {}
        candidates = self.locate_system_installations()
        for p in candidates:
            imported = self.import_versions_from_path(p, storage=storage, username='imported')
            if imported:
                results[p] = imported
        return results

    def detect_versions_in_path(self, src_path: str) -> list:
        """Detect available version folders in a given source path without importing.

        Returns a sorted list of version folder names found under a `versions` folder.
        """
        if not src_path or not os.path.isdir(src_path):
            return []

        candidates = [src_path, os.path.join(src_path, '.minecraft'), os.path.join(src_path, 'minecraft')]
        src_versions = None
        for root in candidates:
            vroot = os.path.join(root, 'versions')
            if os.path.isdir(vroot):
                src_versions = vroot
                break

        if not src_versions:
            return []

        try:
            entries = [e for e in os.listdir(src_versions) if os.path.isdir(os.path.join(src_versions, e))]
            return sorted(entries)
        except Exception:
            return []

    def detect_all_versions_in_system(self) -> dict:
        """Detect versions available in common system installation locations.

        Returns a dict mapping detected source paths to lists of available versions
        (without performing any copy/import).
        """
        results = {}
        candidates = self.locate_system_installations()
        for p in candidates:
            found = self.detect_versions_in_path(p)
            if found:
                results[p] = found
        return results