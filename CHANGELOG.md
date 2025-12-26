# Changelog

All notable changes to ScreenRuler Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-26

### Added
- Meter (m) unit now properly displays in meters instead of micrometers
- Code integrity improvements and cleanup of legacy code

### Changed
- Upgraded to stable Version 1.0.0
- Removed obsolete "Measurement Box Opacity" slider (measurements integrated in toolbar)
- Cleaned up legacy measurement display code
- Updated all documentation and version references

### Fixed
- Meter unit display bug fixed - now shows correct meter values
- Slider value conversion issues (tick spacing, ruler thickness) fixed
- Removed broken references to obsolete UI elements
- Updated comments to reflect current implementation

### Removed
- Obsolete `info_box_opacity` configuration option
- Legacy measurement display fallback code
- Unused backward compatibility code

## [0.2.0] - 2025-12-26

### Added
- Polygon measurement mode with perimeter and area calculation
- Scrollable About dialog for better content visibility
- Improved system tray icon with better visibility (128x128 resolution)
- Support for .ico file as application and system tray icon
- Multi-monitor support with virtual screen awareness
- Customizable fraction count (2-50)
- Real-time fraction spinbox update when using keyboard shortcuts
- Standalone executable builder with PyInstaller
- Comprehensive keyboard shortcuts
- Info box opacity control
- Toolbar visibility toggle

### Changed
- Enhanced About section with reduced spacing and scrollbar
- System tray icon now uses Icon.ico file
- Improved toolbar GUI with better organization
- Updated build script to support virtual environments
- Executable renamed to "ScreenRuler Pro V0.2.0.exe"

### Fixed
- About section bottom content now visible with scrolling
- Fraction count now updates in toolbar when using [ and ] keys
- PIL (Pillow) module import error resolved
- System tray icon visibility improved
- Memory leak in mousewheel binding fixed (changed from bind_all to widget-specific)
- Python environment detection for bundled executables

### Technical
- Added `sys` import for frozen executable detection
- Improved icon loading with fallback support
- Updated ProRuler.spec to include Icon.ico and LICENSE
- Enhanced build process with proper data file bundling

## [0.1.0] - 2024-12-XX

### Added
- Initial release
- Basic ruler measurement functionality
- Angle measurement mode
- Multiple unit support (px, μm, mm, cm, m, in)
- Multiple themes (Cyan, Green, Purple, Orange)
- Click-through mode (Work/Edit toggle)
- System tray integration
- Calibration support
- Guide lines
- Opacity control
- Configuration saving
- Context menu
- Keyboard shortcuts
- Help dialog
- Settings panel

[1.0.0]: https://github.com/yourusername/ScreenRuler-Pro/releases/tag/v1.0.0
[0.2.0]: https://github.com/yourusername/ScreenRuler-Pro/releases/tag/v0.2.0
[0.1.0]: https://github.com/yourusername/ScreenRuler-Pro/releases/tag/v0.1.0
