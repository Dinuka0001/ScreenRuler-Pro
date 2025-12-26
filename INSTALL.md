# Installation Guide

## Method 1: Standalone Executable (Recommended for End Users)

### Download and Run
1. Go to the [Releases](https://github.com/yourusername/ScreenRuler-Pro/releases) page
2. Download `ScreenRuler_Pro_v1.0.0.exe` from the latest release
3. Double-click to run - no installation needed!
4. The application is completely portable

### System Requirements
- Windows 10 or later (64-bit)
- ~25 MB free disk space
- No additional software required

---

## Method 2: Run from Source (For Developers)

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional, for cloning)

### Step-by-Step Installation

#### 1. Get the Source Code
**Option A: Clone with Git**
```bash
git clone https://github.com/yourusername/ScreenRuler-Pro.git
cd ScreenRuler-Pro
```

**Option B: Download ZIP**
1. Click the green "Code" button on GitHub
2. Select "Download ZIP"
3. Extract the ZIP file
4. Open command prompt in the extracted folder

#### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On Linux/Mac:
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Run the Application
```bash
python ScreenRuler_pro.py
```

---

## Method 3: Build Your Own Executable

If you want to build the executable yourself:

### Prerequisites
- Python 3.8+
- All dependencies from requirements.txt

### Build Steps

#### Windows (PowerShell)
```powershell
# Install dependencies including PyInstaller
pip install -r requirements.txt

# Run the build script
.\build_executable.ps1

# Or build manually
pyinstaller ProRuler.spec
```

The executable will be created in the `dist` folder.

---

## Configuration

### First Run
On first run, the application will:
- Create a configuration file (`ruler_config.json`) in the application directory
- Set default preferences
- Display a welcome message

### Settings Location
- **Standalone executable**: Same folder as the .exe
- **Source**: Same folder as ScreenRuler_pro.py

### Customization
All settings can be adjusted through:
- Settings panel (Press `C` or right-click → Settings)
- Keyboard shortcuts (Press `H` for help)
- Direct editing of `ruler_config.json` (not recommended)

---

## Troubleshooting

### Application Won't Start
1. Ensure you have Windows 10 or later
2. Check if antivirus is blocking the .exe
3. Try running as administrator
4. Check Windows Event Viewer for errors

### Missing Features
- Ensure you downloaded the complete release package
- Verify `Icon.ico` is in the same folder as the executable
- Check that no files were blocked by Windows

### Python Version Issues (Source Only)
```bash
# Check Python version
python --version

# Should be 3.8 or higher
# If not, download from: https://www.python.org/downloads/
```

### Dependency Issues (Source Only)
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# If specific package fails, install individually:
pip install pillow
pip install pystray
pip install ttkthemes
```

### Build Issues
```bash
# Clear previous builds
rmdir /s /q build dist

# Clean reinstall PyInstaller
pip uninstall pyinstaller
pip install pyinstaller

# Try building again
pyinstaller --clean ProRuler.spec
```

---

## Uninstallation

### Standalone Executable
Simply delete the .exe file and `ruler_config.json` (if present)

### Source Installation
1. Deactivate virtual environment (if used): `deactivate`
2. Delete the project folder

---

## Need Help?

- 📖 Check the [README](README.md) for usage guide
- 🐛 Report issues on [GitHub Issues](https://github.com/yourusername/ScreenRuler-Pro/issues)
- 📧 Contact: dinuka90@yuhs.ac
