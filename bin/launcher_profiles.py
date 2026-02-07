"""Launcher profiles - support for different mod loaders and launch configs."""
import json
import os
from typing import Dict, List


class LauncherProfile:
    """Represents a launcher profile (Vanilla, Fabric, Forge, etc)."""
    def __init__(self, name: str, jvm_args: str = "", mod_loader: str = "vanilla"):
        self.name = name
        self.jvm_args = jvm_args  # Additional JVM arguments
        self.mod_loader = mod_loader  # vanilla, fabric, forge, quilt
        self.enabled = True
    
    def to_dict(self):
        return {
            'name': self.name,
            'jvm_args': self.jvm_args,
            'mod_loader': self.mod_loader,
            'enabled': self.enabled
        }
    
    @staticmethod
    def from_dict(data):
        profile = LauncherProfile(data['name'], data.get('jvm_args', ''), data.get('mod_loader', 'vanilla'))
        profile.enabled = data.get('enabled', True)
        return profile


class ProfileManager:
    """Manage launcher profiles for each version."""
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.profiles_file = os.path.join(root_dir, 'bin', 'profiles.json')
        self.profiles: Dict[str, List[LauncherProfile]] = self._load_profiles()
    
    def _load_profiles(self) -> Dict:
        """Load profiles from disk."""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    return {
                        version: [LauncherProfile.from_dict(p) for p in profiles]
                        for version, profiles in data.items()
                    }
            except:
                pass
        return {}
    
    def _save_profiles(self):
        """Save profiles to disk."""
        data = {
            version: [p.to_dict() for p in profiles]
            for version, profiles in self.profiles.items()
        }
        with open(self.profiles_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_profile(self, version: str, profile: LauncherProfile):
        """Add a profile for a version."""
        if version not in self.profiles:
            self.profiles[version] = []
        self.profiles[version].append(profile)
        self._save_profiles()
    
    def get_profiles(self, version: str) -> List[LauncherProfile]:
        """Get all profiles for a version."""
        if version not in self.profiles:
            # Create default vanilla profile
            default = LauncherProfile("Vanilla", "", "vanilla")
            self.profiles[version] = [default]
            self._save_profiles()
        return self.profiles[version]
    
    def remove_profile(self, version: str, profile_name: str):
        """Remove a profile."""
        if version in self.profiles:
            self.profiles[version] = [p for p in self.profiles[version] if p.name != profile_name]
            self._save_profiles()
    
    def get_default_profile(self, version: str) -> LauncherProfile:
        """Get the default (first) enabled profile."""
        profiles = self.get_profiles(version)
        for p in profiles:
            if p.enabled:
                return p
        return profiles[0] if profiles else LauncherProfile("Vanilla", "", "vanilla")


# Preset profiles
FABRIC_PROFILE = LauncherProfile(
    "Fabric",
    "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200",
    "fabric"
)

FORGE_PROFILE = LauncherProfile(
    "Forge",
    "-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -XX:G1NewCollectionIntervalInMs=300 -XX:G1MixedGCIntervalInMs=4000",
    "forge"
)

QUILT_PROFILE = LauncherProfile(
    "Quilt",
    "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200",
    "quilt"
)

PERFORMANCE_PROFILE = LauncherProfile(
    "Performance (High RAM)",
    "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -Xmx8G -XX:MaxGCPauseMillis=200",
    "vanilla"
)

LOWEND_PROFILE = LauncherProfile(
    "Low-End PC",
    "-XX:+UseSerialGC -Xmx2G",
    "vanilla"
)
