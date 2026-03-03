# ScreenRuler Pro - User Guide

**Version 2.0.0**  
**Author:** Dinuka Adasooriya  
**Affiliation:** Department of Oral Biology, Yonsei University College of Dentistry  
**Contact:** <dinuka90@yuhs.ac>

## Overview

ScreenRuler Pro is a professional screen measurement tool with advanced features including system tray support, click-through capability, fraction mode, and draggable interface. Measure anything on your screen with precision while working with applications underneath.

## Features

### ✨ Core Features

- **Mode Visibility Toggle**: Click any mode icon to show/hide that measurement mode
- **Position Preservation**: Modes maintain position when switching
- **Text Selection & Deletion**: Click text to select (gold border), press Delete to remove
- **Text Annotation Mode**: Add custom text labels on screen with formatting options
- **Text Formatting Toolbar**: Font size, family, bold, italic, underline, outline
- **Independent Text Movement**: Drag text objects anywhere on screen
- **Click-Through Mode**: Work with windows beneath the ruler
- **Multiple Units**: Pixels, Centimeters, Inches, Millimeters, Micrometers
- **Angle Measurement**: Real-time angle display
- **Customizable Themes**: Cyan, Green, Purple, Orange, Black, White
- **Adjustable Opacity**: From 30% to 100%
- **Angle Lock**: Lock to horizontal or vertical
- **Guide Lines**: Optional crosshair guides
- **Measurement History**: Track your measurements
- **Copy to Clipboard**: Quick copy measurements
- **System Tray**: Minimize to tray with icon menu
- **Fraction Mode**: Divide ruler into equal fractions (2-50)
- **Draggable Info Box**: Move measurement display anywhere
- **Adjustable Thickness**: Ruler line thickness (1-20px)
- **Smart Cursors**: Context-aware mouse cursor changes
- **Calibration System**: Calibrate ruler against known references
- **Toggle Labels**: Show/hide ruler fraction labels
- **Real-time Preview**: See changes instantly in settings
- **Polygon Mode**: Measure perimeter and area of arbitrary polygons (3-20 sides)
- **UTF-8 Support**: Full multilanguage text support
- **Standard Windows Title Bars**: Native Windows chrome with 95% transparency

### 🎨 Themes

- **Cyan** (Default): Bright cyan/red colors
- **Green**: Nature-inspired green/orange
- **Purple**: Modern purple/yellow
- **Orange**: Warm orange/cyan
- **Black**: Dark gray (#0A0A0A) for visibility
- **White**: Light gray (#F5F5F5) for visibility

### 📏 Measurement Units

- **Pixels (px)**: Screen pixels
- **Millimeters (mm)**: Based on 96 DPI and calibration factor
- **Centimeters (cm)**: Based on 96 DPI and calibration factor
- **Inches (in)**: Based on 96 DPI and calibration factor
- **Micrometers (µm)**: Based on 96 DPI and calibration factor
- **Area/Perimeter**: Uses the selected unit with calibration applied

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **P** | Toggle Work/Edit Mode (Click-through) |
| **M** | Cycle through measurement modes |
| **Ctrl+T** | Toggle Text Annotation Mode |
| **Del/Backspace** | Delete selected text (click text first) |
| **H** | Show/Hide Help |
| **S** | Open Settings Panel |
| **A** | About / Credits |
| **C** | Copy Measurement to Clipboard |
| **R** | Reset Ruler Position |
| **G** | Toggle Guide Lines |
| **V** | Toggle Ruler Labels |
| **L** | Cycle Lock (None → Horizontal → Vertical) |
| **T** | Cycle Theme |
| **U** | Cycle Unit (px → cm → inch) |
| **F** | Toggle Fraction Mode |
| **[** | Decrease Fractions |
| **]** | Increase Fractions |
| **,** | Decrease Ruler Thickness |
| **.** | Increase Ruler Thickness |
| **+** | Increase Opacity |
| **-** | Decrease Opacity |
| **Space** | Minimize to Tray |
| **Esc** | Exit Application |

## Mouse Controls

### Edit Mode (Press P to activate)

- **Left Click + Drag** on endpoints: Move ruler endpoints (Crosshair cursor)
- **Left Click + Drag** on line: Move entire ruler (4-way arrow cursor)
- **Left Click + Drag** on info box: Reposition measurement display (Hand cursor)
- **Right Click**: Show context menu

### Work Mode (Default - Click-through enabled)

- Mouse clicks pass through to applications below
- Ruler is visible but non-interactive

### Smart Cursor Feedback

- **Crosshair**: Hovering over endpoints (resize mode)
- **4-way Arrow**: Hovering over ruler line (move mode)
- **Hand**: Hovering over info box (drag mode)
- **Fleur (Move)**: Hovering over text objects in text mode

## Text Annotation Mode

### Overview

Text annotation mode allows you to add custom text labels on your screen with extensive formatting options. Text objects move independently of the ruler and remain on screen until cleared.

### Activating Text Mode

1. Click the **A/T button** in the toolbar, or
2. Press **Ctrl+T** keyboard shortcut
3. Toolbar expands to show text formatting controls

### Adding Text

1. Enter text in the input field (supports UTF-8 multilanguage characters)
2. Click the **Add** button
3. Text appears at center of screen
4. Drag to desired position

### Text Formatting Options

**Font Settings:**
- **Font Size**: 8pt - 72pt (default: 12pt)
- **Font Family**: Arial, Times New Roman, Courier New, Verdana, Tahoma

**Text Styles:**
- **Bold** (B button): Make text bold
- **Italic** (I button): Italicize text
- **Underline** (U button): Underline text
- **Outline**: Toggle text outline for better visibility

**Text Management:**
- **Show/Hide** (👁 button): Toggle visibility of all text objects
- **Clear All** (🗑 button): Remove all text annotations
- **View Menu**: "Screen Text" option for toggling text visibility

### Real-time Updates

All formatting changes apply instantly to all existing text objects:
- Change font size → All text resizes
- Change font family → All text updates font
- Toggle bold/italic/underline → All text updates style
- Changes are synchronized across all text annotations

### Text Movement

- **Click and drag** any text object to reposition it
- Cursor changes to **fleur (move)** when hovering over text
- Each text object moves independently
- Text positions are maintained during ruler resizing

### Best Practices

- Use **text outline** for visibility on complex backgrounds
- Adjust **font size** for readability at different screen resolutions
- Use **Show/Hide** to temporarily toggle text visibility
- Text annotations are **session-based** (not saved between runs)

## Settings Panel

Access via **S** key or right-click menu.

### Appearance Tab

- **Theme Selection**: Choose from 4 color themes
- **Opacity Control**: Adjust transparency (30%-100%)
- **Show Guides**: Toggle crosshair guide lines

### Measurement Tab

- **Unit Selection**: Choose px, mm, cm, inches, or µm
- **Tick Spacing**: Adjust ruler tick marks (10-50px)
- **Ruler Thickness**: Set line width (1-20px)
- **Lock Angle**: Lock ruler to horizontal/vertical

### Calibration Tab

- **Calibration Factor**: Adjust measurement accuracy
- **Step-by-step Guide**: Instructions for calibrating
- **Real-time Display**: See current measurement while calibrating
- **Reset Option**: Return to default calibration (1.0)
- **Example Calculations**: Learn how to calculate calibration factor

## Advanced Features

### Fraction Mode

Divide the ruler into equal parts for precise proportional measurements:

- Press **F** to toggle fraction mode
- Use **[** and **]** to adjust number of divisions (2-50)
- Each division shows its fraction label (e.g., 1/10, 2/10)
- Perfect for design layouts and grid systems

### Polygon Mode

Measure arbitrary polygons for both perimeter and area:

- Switch with **M** (cycle) or Right-click → Measurement Mode → Polygon
- Drag any vertex to reshape; drag near an edge to move the entire polygon
- Tap the small **+** handle near the last vertex to enter add-vertex mode; click anywhere to add points; press **Enter** to finish or **Esc** to cancel
- Info box shows perimeter and area using the selected unit and calibration factor
- Each edge shows its length label (unit-aware)
- Press **C** to copy perimeter and area to clipboard
- Drag the info box to reposition it

### System Tray Integration

- Press **Space** to minimize to system tray
- Right-click tray icon for quick access:
  - Show Ruler
  - Exit Application
- Application continues running in background

### Calibration System

Calibrate the ruler for accurate measurements:

1. Open Settings (press **S**)
2. Go to **Calibration** tab
3. Measure a known reference object (e.g., physical 10cm ruler)
4. Note the displayed measurement
5. Calculate calibration factor: `Known Value ÷ Displayed Value`
6. Enter the factor and click **Apply**
7. All measurements will now use this calibration

**Example:**

- You measure a 10cm object
- Ruler shows 9.5cm
- Calibration factor = 10 ÷ 9.5 = 1.053
- Enter 1.053 and apply

### Real-time Settings Preview

Changes in the settings window are applied immediately:

- **Theme changes**: See new colors instantly
- **Opacity**: Adjust transparency in real-time
- **Guides**: Toggle on/off to see effect
- **Tick spacing**: Preview spacing changes
- **Thickness**: See line width adjustments
- **Labels**: Show/hide fraction labels instantly

## Configuration

Settings are automatically saved to `ruler_config.json` in the application directory.

### Saved Settings Include

- Theme preference
- Opacity levels
- Unit selection
- Tick spacing
- Ruler thickness
- Guide line visibility
- Angle lock preference
- Fraction mode state
- Fraction count
- Info box position

## Usage Examples

### Measuring UI Elements

1. Launch ProRuler.exe
2. Press **P** to enter Edit Mode
3. Drag endpoints to measure desired element
4. Press **C** to copy measurement
5. Press **P** to return to Work Mode

### Measuring at Specific Angle

1. Press **L** to lock to horizontal or vertical
2. Position ruler at desired location
3. Measurement maintains locked angle

### Checking Pixel Spacing

1. Press **U** to cycle to pixel unit
2. Position ruler between elements
3. Read exact pixel distance in info box

## Building Executable

To create a standalone .exe file:

1. Open PowerShell in the Ruler folder
2. Run: `.\build_executable.ps1`
3. Wait for build to complete
4. Find `ProRuler.exe` in the `dist` folder

The executable can run on any Windows PC without Python installed.

## System Requirements

- **OS**: Windows 7 or later
- **Python**: 3.7+ (only for building, not for running .exe)
- **Screen**: Any resolution

## Tips & Tricks

1. **Quick Measurements**: Keep in Work Mode, press P briefly to adjust, press P again to lock
2. **Precise Positioning**: Use guide lines (G key) for alignment
3. **Color Contrast**: Switch themes (T key) for better visibility on different backgrounds
4. **Persistent Settings**: Your preferences are saved automatically
5. **Copy-Paste**: Use C key to quickly copy measurements to any application

## Troubleshooting

### Ruler not visible

- Press **Space** to restore if minimized
- Check opacity setting (press + to increase)
- Try different theme for better contrast

### Can't interact with ruler

- Press **P** to exit Work Mode
- Ruler must be in Edit Mode to move

### Clicks not passing through

- Press **P** to enable Work Mode
- Check for "🌐 WORK" in info box

## Technical Details

- **DPI Assumption**: 96 DPI (standard Windows)
- **Config File**: ruler_config.json (JSON format)
- **Windows API**: Uses WS_EX_TRANSPARENT for click-through
- **Framework**: Tkinter (built into Python)

## Version

**ScreenRuler Pro v2.0.0**

**Author:** Dinuka Adasooriya  
**Affiliation:** Department of Oral Biology, Yonsei University College of Dentistry  
**Email:** <dinuka90@yuhs.ac>

### Version 2.0.0 Features

- System tray minimize support
- Fraction mode with adjustable divisions
- Draggable info box
- Adjustable ruler thickness
- Smart cursor feedback
- **Calibration system for accurate measurements**
- **Toggle show/hide ruler labels**
- **Real-time preview in settings**
- About/Credits dialog
- Professional GUI
- Multiple themes
- Unit conversion
- Settings panel
- Standalone executable support

### System Requirements

- **OS**: Windows 7 or later
- **RAM**: Minimal (< 50 MB)
- **Display**: Any resolution
- **Dependencies**: None (standalone .exe)

---

© 2025 Dinuka Adasooriya  
Department of Oral Biology  
Yonsei University College of Dentistry  
Contact: <dinuka90@yuhs.ac>

## License

- **Type:** GNU General Public License v3.0 (GPL-3.0)
- **Summary:** You may run, study, share, and modify this software. Derivative works must also be licensed under GPL-3.0.
- **Full Text:** See the LICENSE file in this repository or open the About tab and click "View Full License".
