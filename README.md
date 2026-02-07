# HidenLogick Launcher

A **premium-grade Minecraft launcher** built with PyQt6 and minecraft-launcher-lib. Rivals TLauncher with advanced version management, profile support, and modern UI.

## 🚀 Features

### Core
- ✅ Install Minecraft versions with intelligent retry/backoff logic
- ✅ Detect and import versions from existing Minecraft installs or third-party launchers (TLauncher)
- ✅ Persistent storage for versions, players, and launch profiles
- ✅ Professional dark theme with smooth animations and notifications

### Version Management
- 📦 **Sidebar cards** showing installed versions with PLAY/DELETE buttons
- 🔍 **Search/filter** versions by name or player
- 📊 **Stats dashboard** showing storage used, version count, and active players
- 🎯 **Launch profiles** - support for Vanilla, Fabric, Forge, Quilt with custom JVM args
- 🔄 **Safe import flow** - non-destructive copy with progress window
- ✋ **Manual folder import** - choose any folder to import from

### Advanced Features
- ⚙️ **Settings dialog** - configure auto-import, background scanner, backup options
- 🔔 **Toast notifications** - get notified on imports and version updates
- 🔎 **Background scanner** - periodically auto-detect new installations (configurable)
- 🎮 **Desktop shortcuts** - launch versions directly from Windows desktop
- ⌨️ **Launch profiles** - Vanilla, Fabric, Forge, Quilt, Performance, Low-End configs
- 💾 **Auto-backup** - optional backup copies when importing

## 📋 Requirements

- Python 3.10+
- Windows (shortcuts feature Windows-only; core launcher cross-platform)

## 🔧 Installation

1. Install optional desktop shortcut support:

```powershell
pip install pywin32
```

2. Run the app:

```powershell
python aplication.py
```

## 📖 Usage

### First Launch
- The app will detect and offer to import versions from:
  - Existing Minecraft installations (`%APPDATA%\.minecraft`, `~\.minecraft`)
  - TLauncher folders
  - Any custom folder you select

### Installing New Versions
1. Enter player nickname (3-32 characters)
2. Select version from dropdown
3. Click "START INSTALLATION"
4. Monitor progress in the log

### Playing Installed Versions
- Click **PLAY** on any installed version card
- Select a launch profile if multiple exist
- Game launches with the configured JVM args

### Managing Versions
- **PLAY** - Launch with selected profile
- **DELETE** - Remove installation and card
- **Search** - Filter by version/player name (sidebar search box)

### Settings & Configuration
- Click **⚙ Settings** to open the settings dialog
- Configure:
  - Auto-import on startup
  - Create backups when importing
  - Background scanner (periodic auto-detection)
  - Scan interval (minutes)

### Launch Profiles
Each version supports multiple profiles:
- **Vanilla** - Standard launch (default)
- **Fabric** - Lightweight mod loader
- **Forge** - Heavy-duty modding
- **Quilt** - Modern alternative to Fabric
- **Performance** - High RAM, optimized GC
- **Low-End** - 2GB RAM, minimal overhead

## 📁 Project Structure

```
HidenLogick/
├── aplication.py                 # Entry point
├── requirements.txt              # Dependencies
├── LICENSE                       # Copyright + Protection
├── README.md                     # This file
├── bin/
│   ├── __init__.py
│   ├── engine.py                 # Core game engine (install, launch, detect)
│   ├── storage.py                # Persistent JSON storage
│   ├── config.py                 # Settings management
│   ├── ui_main.py                # Main UI (PyQt6)
│   ├── styles.py                 # Dark theme styling
│   ├── settings_dialog.py         # Settings UI
│   ├── notifications.py          # Toast notifications
│   ├── progress_window.py         # Progress dialog
│   ├── launcher_profiles.py       # Launch profile management
│   ├── desktop_shortcuts.py       # Windows shortcut creation
│   ├── data.json                 # Persistent storage (auto-created)
│   ├── config.json               # Settings (auto-created)
│   ├── profiles.json             # Launch profiles (auto-created)
│   └── assets/
│       └── miniatures/           # Version thumbnails
├── games/
│   └── Minecraft/
│       └── ac.game/
│           └── versions/         # Installed game versions
└── mods/
    └── dlcs/                     # Extension/mod directory
```

## 🔒 Copyright & License

This software is protected under the MIT License with additional Copyright Protection Clauses.

**Key Points:**
- ✅ Free to use, modify, and redistribute
- ✅ Must retain attribution and copyright notices
- ✅ Derivative works must be clearly marked and use different name
- ❌ Cannot remove copyright notices
- ❌ Cannot claim original authorship
- ❌ Cannot misrepresent origin
- 📖 See [LICENSE](LICENSE) file for full legal terms

**For Developers:**
If you create extensions, forks, or modifications:
1. Keep all copyright notices intact
2. Add a note like: "Based on HidenLogick by [original author]"
3. Use a different name for your version
4. Link to the original repository

## 🛠️ Configuration

### `bin/config.json`
```json
{
    "auto_import_on_startup": false,
    "scan_interval_minutes": 30,
    "backup_copies": true,
    "enable_scanner": false
}
```

### `bin/profiles.json`
Lists launch profiles for each version (auto-generated per version).

### `bin/data.json`
Persistent storage of installed versions:
```json
[
    {
        "version": "1.20.1",
        "username": "PlayerName",
        "installed_at": "2026-02-07 10:30:45"
    }
]
```

## 🔐 Security & Privacy

- **Local only** - App only reads/writes local game folders, no external data transmission
- **Safe imports** - Non-destructive copy; existing files never deleted
- **Configurable** - Settings for auto-import, scanner, backups all optional
- **Transparent** - Progress windows show exactly what's happening

## 🚀 Advanced Features

### Background Scanner
Enable in Settings to periodically auto-detect new Minecraft installations:
- Runs on configurable interval (default: 30 min)
- Auto-imports found versions
- Notifies on discovery

### Desktop Shortcuts
After installing a version, create Windows desktop shortcut for quick launch.

### Custom Profiles
Add custom launch profiles in `bin/profiles.json` with custom JVM arguments for specific versions.

## 📊 Stats Dashboard
View at the top of the install page:
- 📦 Installed versions count
- 💾 Total storage used (GB)
- 👤 Active player count

## 🐛 Troubleshooting

**"No versions found"**
- Ensure Minecraft is installed in standard locations
- Try manual import from custom folder using the "Import from Folder..." button

**"Installation stuck"**
- Check internet connection
- Restart the app
- Check logs for errors

**"Settings not saving"**
- Ensure `bin/` folder is writable
- Check `bin/config.json` exists

## 📝 Version History

**v1.0** - Release
- Core launcher + install/launch
- Version detection & import
- Sidebar version management  
- Professional UI

**v2.0** - Premium Features (Current)
- Settings dialog + config system
- Toast notifications
- Stats dashboard
- Sidebar search/filter
- Launch profiles support
- Background scanner
- Desktop shortcuts
- Bulletproof copyright license

## 🔗 Links & Resources

- **Minecraft Launcher Lib**: https://github.com/JuniorJPDJ/minecraft-launcher-lib
- **PyQt6**: https://www.riverbankcomputing.com/software/pyqt/

## 💡 Contributing

To extend HidenLogick:
1. Create a new branch
2. Make your changes
3. Add attribution to HidenLogick in comments/README
4. Submit a PR or fork with clear naming (e.g., "HidenLogick-Plus")

---

**Made with ❤️ for the Minecraft community**

© 2026 HidenLogick Contributors. All rights reserved.
