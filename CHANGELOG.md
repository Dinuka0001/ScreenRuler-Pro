# Changelog

All notable changes to ScreenRuler Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-31

### Added
- **GitHub Link in About Section**: Added "View on GitHub" link with GitHub icon in the About tab
  - Clickable link opens the project repository
  - GitHub_Black.ico icon included (with emoji fallback)
  - Hover effects for better UX
- **Mode Visibility Toggle**: Click any mode icon to show/hide that measurement mode
  - Click ruler icon (📏) to toggle ruler visibility
  - Click fractions icon (¼) to toggle fractions visibility
  - Click angle icon (∠) to toggle angle visibility
  - Click polygon icon (⬟) to toggle polygon visibility
  - Visual feedback: Blue=active/visible, Gray=inactive/visible, Dimmed=hidden
- **Position Preservation**: Position is now maintained when switching between modes
  - Ruler, Angle, Polygon, and Fractions modes remember their positions
  - No more resetting to default when changing modes
  - Smooth transitions between measurement types
- **Polygon Sides Preservation**: Changing polygon sides now preserves center position
  - Adjust from 3 to 20 sides without repositioning
  - New polygons appear at the same location
- **Minimize to Tray**: Added to File menu and right-click context menu
  - Minimizes entire app (ruler + toolbar) to system tray
  - Easy access from multiple locations
- **Text Selection & Deletion**: Enhanced text object management
  - Click text to select (gold border highlight)
  - Press Delete or Backspace to remove selected text
  - Click elsewhere to deselect
  - Selection toggle by clicking same text again
- **Text Annotation Mode**: Add custom text annotations on screen with independent movement
  - Text mode toggle button (A/T icon) in toolbar
  - Text input field with "Add" button
  - Drag text objects independently of the ruler
  - Cursor changes to "fleur" (move) when hovering over text
- **Text Formatting Toolbar**: Comprehensive text formatting controls
  - Font size selector (8-72 pt)
  - Font family selector (Arial, Times New Roman, Courier New, Verdana, Tahoma)
  - Bold, Italic, Underline formatting buttons with styled icons
  - Text outline toggle for better visibility
  - Clear all text button (🗑)
  - Show/Hide text visibility button (👁)
- **Enhanced Theme Colors**: Black and white themes adjusted for better visibility
  - Black theme: #0A0A0A (dark gray) for visibility against pure black backgrounds
  - White theme: #F5F5F5 (light gray) for visibility against pure white backgrounds
- **View Menu Enhancement**: "Screen Text" option added to View menu with checkmark indicator
- **Dynamic Toolbar**: Toolbar height automatically adjusts (155px → 245px) when text mode is active
- **Real-time Updates**: All text formatting changes apply instantly to all existing text objects
- **UTF-8 Support**: Full multilanguage text support with proper encoding
- **Centered Default Positions**: All modes default to screen center for consistency

### Changed
- **View Menu**: Removed duplicate "Show Fractions" option (now accessible via dedicated toolbar button)
- **Toolbar Close Button**: Now exits entire application instead of just minimizing toolbar
- **Standard Windows Title Bars**: Both toolbar and control panel use native Windows chrome
  - Toolbar: Standard title bar with transparency (95%)
  - Control Panel: Standard title bar matching toolbar style
  - Better OS integration and taskbar behavior
- **Menu System Updates**: Mode switching from menus now respects visibility system
- **Keyboard Shortcuts**: M key cycles modes and ensures new mode is visible
- Default toolbar width increased from 450px to 490px for better control spacing
- Text objects now use simpler dragging interface without resize handles
- Improved toolbar organization with secondary text formatting section

### Fixed
- Toolbar close button now properly exits entire app (not just toolbar)
- Polygon sides change preserves position (stays at current center)
- Mode switching preserves position across all modes
- Ruler tick marks no longer display beyond ruler endpoint when ruler length is between fractions
- Improved exception handling (replaced bare except clause with proper Exception handling)

### Removed
- Custom resize grip code (not needed with standard title bars)
- Custom window dragging code for control panel (uses native dragging)
- Unused resize toolbar functions

## [1.0.0] - 2025-12-26

### Added
- Basic ruler measurement functionality with multiple units (pixels, μm, mm, cm, m, in)
- Angle measurement mode with real-time angle display
- Polygon measurement mode with perimeter and area calculation (3-20 sides)
- Fraction mode to divide ruler into equal parts (2-50 fractions)
- Multiple themes: Cyan, Green, Purple, Orange, Black, White
- Click-through mode (Work/Edit toggle) to interact with windows beneath
- System tray integration with minimize to tray functionality
- Calibration system to calibrate against known references
- Guide lines and crosshair support
- Adjustable opacity (30% to 100%)
- Adjustable ruler line thickness (1-20px)
- Measurement history tracking
- Copy to clipboard functionality
- Draggable measurement display
- Scrollable About dialog
- Multi-monitor support with virtual screen awareness
- Comprehensive keyboard shortcuts
- Configuration persistence across sessions
- Context menu for quick access
- Real-time preview of settings changes
- Standalone executable with PyInstaller
- Support for .ico file as application and system tray icon

### Changed
- Cleaned up legacy measurement display code
- Enhanced About section with reduced spacing and scrollbar
- System tray icon now uses Icon.ico file (128x128 resolution)
- Improved toolbar GUI with better organization
- Updated all documentation and version references

### Fixed
- Meter unit display bug fixed - now shows correct meter values
- Slider value conversion issues (tick spacing, ruler thickness) fixed
- About section bottom content now visible with scrolling
- Fraction count now updates in toolbar when using keyboard shortcuts
- PIL (Pillow) module import error resolved
- System tray icon visibility improved
- Memory leak in mousewheel binding fixed (widget-specific binding)
- Python environment detection for bundled executables
- Removed broken references to obsolete UI elements

### Removed
- Obsolete `info_box_opacity` configuration option
- Legacy measurement display fallback code
- Unused backward compatibility code

[2.0.0]: https://github.com/Dinuka0001/ScreenRuler-Pro/releases/tag/v2.0.0
[1.0.0]: https://github.com/Dinuka0001/ScreenRuler-Pro/releases/tag/v1.0.0
