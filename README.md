# 📏 ScreenRuler Pro V1.0.0

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

A professional on-screen measurement tool for Windows with advanced features including multiple measurement modes, customizable themes, and system tray integration.


## ✨ Features

### Measurement Modes
- **📏 Ruler Mode** - Measure distances with precision
- **📐 Angle Mode** - Measure angles between two lines
- **🔢 Fraction Mode** - Display measurements with customizable fractions
- **⬡ Polygon Mode** - Measure perimeter and area of polygons

### Units Support
- Pixels (px)
- Micrometers (μm)
- Millimeters (mm)
- Centimeters (cm)
- Meters (m)
- Inches (in)

### Advanced Features
- 🎨 **Multiple Themes** - Cyan, Green, Purple, Orange
- 🔒 **Angle Lock** - Lock to horizontal or vertical
- 👻 **Click-Through Mode** - Work/Edit mode toggle
- 🎯 **Calibration** - Calibrate measurements to real-world units
- 📊 **Interactive Toolbar** - Easy access to all features
- 🌙 **Opacity Control** - Adjust transparency
- 💾 **Save Settings** - Configuration persists between sessions
- 🖥️ **Multi-Monitor Support** - Works across multiple displays
- 📍 **Guide Lines** - Visual measurement aids

## 🚀 Quick Start

### Pre-built Executable (Recommended)
1. Download the latest release from the [Releases](https://github.com/dinuka0001/ScreenRuler-Pro/releases) page
2. Run `ScreenRuler_Pro_v1.0.0.exe`
3. No installation or Python required!

### Run from Source
```bash
# Clone the repository
git clone https://github.com/dinuka0001/ScreenRuler-Pro.git
cd ScreenRuler-Pro

# Create virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python ScreenRuler_pro.py
```

## 🔨 Building from Source

### Build Standalone Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build using the provided script
.\build_executable.ps1

# Or build manually
pyinstaller ProRuler.spec

# Executable will be in the 'dist' folder
```

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `W` / `S` | Toggle Work/Edit mode (Click-through) |
| `E` | Show/hide toolbar |
| `H` | Show help |
| `C` | Show control panel (Settings) |
| `A` | Show about dialog |
| `T` | Cycle themes |
| `U` | Cycle units |
| `L` | Cycle angle lock (None/Horizontal/Vertical) |
| `G` | Toggle guide lines |
| `F` | Toggle fraction display |
| `[` / `]` | Decrease/increase fraction count |
| `+` / `-` | Increase/decrease opacity |
| `.` / `,` | Increase/decrease ruler thickness |
| `V` | Toggle measurement labels |
| `M` | Cycle measurement modes |
| `Q` / `Esc` | Quit application |

## 🎯 Usage Guide

### Ruler Mode
1. Click and drag to measure distance
2. Right-click for context menu
3. Change units with `U` key
4. Toggle labels with `V` key

### Angle Mode
1. Click to set three points
2. Displays angle between the lines
3. Press `M` to cycle to this mode

### Fraction Mode
1. Measures in fractional units
2. Use `[` and `]` to adjust fraction count
3. Useful for architectural measurements

### Polygon Mode
1. Click to add vertices
2. Double-click to close polygon
3. Shows perimeter and area
4. Use number input to set sides

### Work vs Edit Mode
- **Edit Mode**: Can interact with ruler (default)
- **Work Mode**: Ruler becomes click-through (transparent to mouse)
- Toggle with `W` or `S` keys

## 🛠️ System Requirements

- Windows 10 or later (64-bit)
- Python 3.8+ (for running from source)
- ~25 MB disk space (for executable)

## 📦 Dependencies

- `tkinter` - GUI framework (included with Python)
- `Pillow` - Image processing for icons
- `pystray` - System tray integration
- `ttkthemes` - Additional themes

See [requirements.txt](requirements.txt) for full list.

## 🖼️ Screenshots

_Add your screenshots here_

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Configuration

Settings are automatically saved to `ruler_config.json` in the application directory. Configuration includes:
- Selected unit and theme
- Opacity settings
- Calibration factor
- UI preferences

## 🐛 Known Issues

- System tray icon may not display on some Windows themes
- Very small measurements may be less accurate due to screen pixel density

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Dinuka Adasooriya**  
Department of Oral Biology  
Yonsei University College of Dentistry  
📧 dinuka90@yuhs.ac

## 🙏 Acknowledgments

- Built with Python and Tkinter
- Icons from system emoji fonts
- Inspired by classic on-screen ruler tools

## 📊 Version History

### v1.0.0 (Current)
- Added polygon measurement mode
- Improved system tray integration
- Enhanced multi-monitor support
- Added customizable toolbar
- Fixed fraction display updates
- Improved icon visibility
- Added scrollable About dialog

### v0.1.0
- Initial release
- Basic ruler functionality
- Angle measurement
- Multiple units support

---

⭐ If you find this project useful, please consider giving it a star!

📢 For bug reports and feature requests, please use the [Issues](https://github.com/dinuka0001/ScreenRuler-Pro/issues) page.

