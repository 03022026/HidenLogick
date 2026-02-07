"""Auto-update checker for HidenLogick launcher."""
import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Tuple


class UpdateChecker:
    """Check for updates from GitHub releases."""
    
    REPO = "03022026/HidenLogick"  # GitHub owner/repo
    GITHUB_URL = "https://github.com/03022026/HidenLogick"  # Full GitHub URL
    API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
    
    def __init__(self, root_dir: str, current_version: str = "2.0.0"):
        self.root_dir = root_dir
        self.current_version = current_version
        self.cache_file = os.path.join(root_dir, 'bin', 'update_cache.json')
        self.check_interval_hours = 24  # Check once per day
    
    def _get_cache(self) -> dict:
        """Load cached update check result."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'last_check': None, 'latest_version': None}
    
    def _save_cache(self, data: dict):
        """Save cache file."""
        with open(self.cache_file, 'w') as f:
            json.dump(data, f)
    
    def _should_check(self) -> bool:
        """Check if enough time has passed to re-check."""
        cache = self._get_cache()
        last_check = cache.get('last_check')
        
        if not last_check:
            return True
        
        last_check_dt = datetime.fromisoformat(last_check)
        if datetime.now() - last_check_dt > timedelta(hours=self.check_interval_hours):
            return True
        
        return False
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings.
        Returns: 1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        try:
            v1_parts = [int(x) for x in v1.lstrip('v').split('.')]
            v2_parts = [int(x) for x in v2.lstrip('v').split('.')]
            
            # Pad with zeros
            while len(v1_parts) < len(v2_parts):
                v1_parts.append(0)
            while len(v2_parts) < len(v1_parts):
                v2_parts.append(0)
            
            if v1_parts > v2_parts:
                return 1
            elif v1_parts < v2_parts:
                return -1
            return 0
        except:
            return 0
    
    def check_for_updates(self, force: bool = False) -> Tuple[bool, dict]:
        """Check for updates.
        
        Returns:
            Tuple of (update_available, update_info)
            update_info contains: {'version', 'url', 'changelog', 'size_mb'}
        """
        if not force and not self._should_check():
            cache = self._get_cache()
            latest = cache.get('latest_version')
            if latest and self._compare_versions(latest, self.current_version) > 0:
                return True, {
                    'version': latest,
                    'from_cache': True
                }
            return False, {}
        
        try:
            # Fetch latest release from GitHub
            with urllib.request.urlopen(self.API_URL, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            latest_version = data.get('tag_name', '').lstrip('v')
            update_available = self._compare_versions(latest_version, self.current_version) > 0
            
            # Update cache
            cache_data = {
                'last_check': datetime.now().isoformat(),
                'latest_version': latest_version
            }
            self._save_cache(cache_data)
            
            if update_available:
                # Get download URL and info
                download_url = None
                for asset in data.get('assets', []):
                    if asset['name'].endswith('.zip'):
                        download_url = asset['browser_download_url']
                        size_mb = asset.get('size', 0) / (1024 * 1024)
                        break
                
                update_info = {
                    'version': latest_version,
                    'url': download_url or data.get('html_url'),
                    'changelog': data.get('body', 'No changelog available'),
                    'size_mb': size_mb if download_url else None,
                    'released_at': data.get('published_at')
                }
                return True, update_info
            
            return False, {}
        
        except urllib.error.URLError as e:
            print(f"Update check failed (network): {e}")
            return False, {}
        except Exception as e:
            print(f"Update check failed: {e}")
            return False, {}
    
    def get_cached_version(self) -> str:
        """Get last known latest version."""
        cache = self._get_cache()
        return cache.get('latest_version')


class UpdateNotifier:
    """Handle update notifications and prompts."""
    
    @staticmethod
    def format_changelog(changelog: str, max_lines: int = 10) -> str:
        """Format changelog for display."""
        lines = changelog.split('\n')[:max_lines]
        return '\n'.join(lines)
    
    @staticmethod
    def get_download_link_text(url: str) -> str:
        """Get user-friendly download link text."""
        if url:
            return f"Download from: {url}"
        return "Visit GitHub releases page"
