"""Advanced mod profiler for managing mod-heavy profiles per version."""
import json
import os
from typing import Dict, List


class ModProfile:
    """Represents a mod profile with custom mods and settings."""
    def __init__(self, name: str, mods: List[str] = None, jvm_args: str = "", loader: str = "fabric"):
        self.name = name
        self.mods = mods or []  # List of mod folder names or JAR paths
        self.jvm_args = jvm_args
        self.loader = loader  # fabric, forge, quilt
        self.enabled = True
        self.memory_allocation = 4096  # MB
    
    def to_dict(self):
        return {
            'name': self.name,
            'mods': self.mods,
            'jvm_args': self.jvm_args,
            'loader': self.loader,
            'enabled': self.enabled,
            'memory_allocation': self.memory_allocation
        }
    
    @staticmethod
    def from_dict(data):
        profile = ModProfile(
            data['name'],
            data.get('mods', []),
            data.get('jvm_args', ''),
            data.get('loader', 'fabric')
        )
        profile.enabled = data.get('enabled', True)
        profile.memory_allocation = data.get('memory_allocation', 4096)
        return profile


class ModProfiler:
    """Manage mod profiles for each version."""
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.profiles_file = os.path.join(root_dir, 'bin', 'mod_profiles.json')
        self.profiles: Dict[str, List[ModProfile]] = self._load_profiles()
    
    def _load_profiles(self) -> Dict:
        """Load mod profiles from disk."""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    return {
                        version: [ModProfile.from_dict(p) for p in profiles]
                        for version, profiles in data.items()
                    }
            except:
                pass
        return {}
    
    def _save_profiles(self):
        """Save mod profiles to disk."""
        data = {
            version: [p.to_dict() for p in profiles]
            for version, profiles in self.profiles.items()
        }
        with open(self.profiles_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_profile(self, version: str, name: str, loader: str = "fabric") -> ModProfile:
        """Create a new mod profile for a version."""
        if version not in self.profiles:
            self.profiles[version] = []
        
        profile = ModProfile(name, [], "", loader)
        self.profiles[version].append(profile)
        self._save_profiles()
        return profile
    
    def get_profiles(self, version: str) -> List[ModProfile]:
        """Get all mod profiles for a version."""
        if version not in self.profiles:
            return []
        return self.profiles[version]
    
    def get_profile(self, version: str, profile_name: str) -> ModProfile:
        """Get a specific mod profile."""
        profiles = self.get_profiles(version)
        for p in profiles:
            if p.name == profile_name:
                return p
        return None
    
    def add_mod_to_profile(self, version: str, profile_name: str, mod_path: str):
        """Add a mod to a profile."""
        profile = self.get_profile(version, profile_name)
        if profile and mod_path not in profile.mods:
            profile.mods.append(mod_path)
            self._save_profiles()
    
    def remove_mod_from_profile(self, version: str, profile_name: str, mod_path: str):
        """Remove a mod from a profile."""
        profile = self.get_profile(version, profile_name)
        if profile and mod_path in profile.mods:
            profile.mods.remove(mod_path)
            self._save_profiles()
    
    def delete_profile(self, version: str, profile_name: str):
        """Delete a mod profile."""
        if version in self.profiles:
            self.profiles[version] = [p for p in self.profiles[version] if p.name != profile_name]
            self._save_profiles()
    
    def delete_all_profiles(self, version: str):
        """Delete all mod profiles for a version."""
        if version in self.profiles:
            del self.profiles[version]
            self._save_profiles()
    
    def duplicate_profile(self, version: str, profile_name: str, new_name: str) -> ModProfile:
        """Duplicate an existing profile."""
        original = self.get_profile(version, profile_name)
        if not original:
            return None
        
        # Create new profile with same settings
        if version not in self.profiles:
            self.profiles[version] = []
        
        new_profile = ModProfile(new_name, original.mods.copy(), original.jvm_args, original.loader)
        new_profile.memory_allocation = original.memory_allocation
        self.profiles[version].append(new_profile)
        self._save_profiles()
        return new_profile


# Preset mod profiles
SKYBLOCK_PROFILE = ModProfile(
    "Skyblock",
    ["skyblock-mod.jar"],
    "-XX:+UseG1GC -Xmx4G",
    "fabric"
)

VANILLA_TWEAKS_PROFILE = ModProfile(
    "Vanilla Tweaks",
    ["vanilla-tweaks.jar"],
    "-XX:+UseG1GC -Xmx6G",
    "fabric"
)

HEAVY_MODPACK_PROFILE = ModProfile(
    "Heavy Modpack",
    [],  # Will be populated by user
    "-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions -Xmx8G -XX:G1NewCollectionIntervalInMs=300",
    "forge"
)
