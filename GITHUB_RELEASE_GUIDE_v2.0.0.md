# GitHub Release Guide for ScreenRuler Pro v2.0.0

## ✅ Pre-Release Checklist (All Completed)

- [x] Version numbers updated in all files:
  - [x] `ScreenRuler_pro.py` (line 4: VERSION = "2.0.0")
  - [x] `ProRuler.spec` (name: 'ScreenRuler_Pro_v2.0.0')
  - [x] `README.md` (header: Version 2.0.0)
  - [x] `CHANGELOG.md` (v2.0.0 entry added)
- [x] Executable built successfully: `ScreenRuler_Pro_v2.0.0.exe`
- [x] Source files copied to GitHub folder
- [x] Release notes created: `V2.0.0_RELEASE.md`

## 📦 Files Ready for Release

Located in: `f:\Portable_software\Ruler\251225 Active\ScreenRuler-Pro-GitHub\`

### Required Files
- ✅ `ScreenRuler_Pro_v2.0.0.exe` (Main executable ~25MB)
- ✅ `ScreenRuler_pro.py` (Updated source code with v2.0.0)
- ✅ `ProRuler.spec` (Updated build spec)
- ✅ `README.md` (Updated user guide)
- ✅ `CHANGELOG.md` (With v2.0.0 changes)
- ✅ `V2.0.0_RELEASE.md` (Release notes)
- ✅ `LICENSE` (GPL-3.0)
- ✅ `Icon.ico` (Application icon)
- ✅ `requirements.txt` (Dependencies)

## 🚀 GitHub Release Steps

### 1. Commit and Push Changes

Open PowerShell in the GitHub folder:

```powershell
cd "f:\Portable_software\Ruler\251225 Active\ScreenRuler-Pro-GitHub"

# Check status
git status

# Add all updated files
git add ScreenRuler_pro.py
git add ProRuler.spec
git add README.md
git add CHANGELOG.md
git add V2.0.0_RELEASE.md
git add ScreenRuler_Pro_v2.0.0.exe

# Commit with message
git commit -m "Release v2.0.0 - Text Annotation Mode

Major Features:
- Text annotation mode with formatting toolbar
- Font size, family, bold, italic, underline, outline
- Independent text movement
- Enhanced black/white themes for visibility
- Real-time text formatting updates
- UTF-8 multilanguage support
- Dynamic toolbar resizing
- View menu text options

Bug Fixes:
- Fixed ruler tick marks displaying beyond endpoint
- Improved exception handling

See V2.0.0_RELEASE.md for complete details."

# Push to GitHub
git push origin main
```

### 2. Create GitHub Release

1. **Go to your repository on GitHub**
   - Navigate to: `https://github.com/Dinuka0001/ScreenRuler-Pro`

2. **Click "Releases" → "Draft a new release"**

3. **Fill in Release Information:**

   **Tag version:**
   ```
   v2.0.0
   ```

   **Release title:**
   ```
   ScreenRuler Pro v2.0.0 - Text Annotation Release
   ```

   **Description:** Copy from below ⬇️

---

## 📝 Release Description (Copy this to GitHub)

```markdown
# 🎉 ScreenRuler Pro v2.0.0 - Text Annotation Release

## Major New Feature: Text Annotation System

This release adds comprehensive text annotation capabilities with full formatting support!

### ✨ What's New

#### 📝 Text Annotation Mode
- **A/T Toggle Button**: Activate text mode from toolbar or press `Ctrl+T`
- **Add Custom Text**: Enter any text (UTF-8 multilanguage support)
- **Independent Movement**: Drag text anywhere on screen
- **Smart Cursor**: Changes to "move" when hovering over text

#### 🎨 Text Formatting Toolbar
- **Font Size**: 8pt - 72pt
- **Font Family**: Arial, Times New Roman, Courier New, Verdana, Tahoma
- **Text Styles**: Bold, Italic, Underline with styled B/I/U buttons
- **Text Outline**: Toggle for visibility on complex backgrounds
- **Visibility Control**: Show/Hide all text with eye button (👁)
- **Clear All**: Remove all annotations with trash button (🗑)

#### 🎭 Enhanced Themes
- **Black Theme**: Adjusted to #0A0A0A (dark gray) for better visibility
- **White Theme**: Adjusted to #F5F5F5 (light gray) for better visibility
- Both themes work perfectly against matching backgrounds

#### 🖥️ UI Improvements
- **Dynamic Toolbar**: Auto-expands (155px → 245px) in text mode
- **Wider Toolbar**: Default 490px width for better spacing
- **View Menu**: New "Screen Text" option with checkmark
- **Real-time Updates**: All formatting applies instantly to all text

### 🐛 Bug Fixes
- Fixed ruler tick marks appearing beyond endpoint
- Improved exception handling

### 📋 How to Use
1. Click A/T button or press `Ctrl+T`
2. Enter text and click "Add"
3. Drag text to position
4. Use formatting toolbar to customize
5. Toggle visibility with eye icon
6. Clear all with trash icon

### 🎯 Upgrade Recommendation
**Major version update** - All users encouraged to upgrade for new text annotation features!

---

## 📥 Installation

### Option 1: Standalone Executable (Recommended)
Download `ScreenRuler_Pro_v2.0.0.exe` and run - no installation needed!

### Option 2: Run from Source
```bash
pip install -r requirements.txt
python ScreenRuler_pro.py
```

---

## 📊 Technical Details
- **Version**: 2.0.0
- **Python**: 3.14.0 compatible
- **PyInstaller**: 6.17.0
- **File Size**: ~25 MB
- **Platform**: Windows 11/10
- **License**: GPL-3.0

---

## 🔗 Links
- **Full Release Notes**: [V2.0.0_RELEASE.md](https://github.com/Dinuka0001/ScreenRuler-Pro/blob/main/V2.0.0_RELEASE.md)
- **Changelog**: [CHANGELOG.md](https://github.com/Dinuka0001/ScreenRuler-Pro/blob/main/CHANGELOG.md)
- **User Guide**: [README.md](https://github.com/Dinuka0001/ScreenRuler-Pro/blob/main/README.md)
- **Report Issues**: [GitHub Issues](https://github.com/Dinuka0001/ScreenRuler-Pro/issues)

---

**Previous Release**: [v1.0.0](https://github.com/Dinuka0001/ScreenRuler-Pro/releases/tag/v1.0.0)

**Thank you** to all users who requested text annotation features! 🎉
```

---

### 4. **Attach Release Assets**

Upload these files to the release:

1. **Primary Asset:**
   - `ScreenRuler_Pro_v2.0.0.exe` (Main executable)

2. **Optional Documentation:**
   - GitHub automatically includes source code as ZIP/TAR.GZ

### 5. **Publish Release**

- ✅ Check "Set as the latest release"
- ✅ Click "Publish release"

---

## 📢 Post-Release

### Share the Release
- Update any project websites
- Announce on social media if applicable
- Notify users who requested text features

### Monitor Issues
- Watch for bug reports related to new features
- Respond to user feedback
- Plan hotfixes if needed

---

## 🔄 Quick Commands Reference

```powershell
# Navigate to GitHub folder
cd "f:\Portable_software\Ruler\251225 Active\ScreenRuler-Pro-GitHub"

# Check what's changed
git status
git diff

# Add and commit
git add .
git commit -m "Release v2.0.0"
git push origin main

# Create tag (optional - GitHub can create it)
git tag -a v2.0.0 -m "Version 2.0.0 - Text Annotation Release"
git push origin v2.0.0
```

---

## ✅ Release Complete!

Once published, your release will be available at:
`https://github.com/Dinuka0001/ScreenRuler-Pro/releases/tag/v2.0.0`

Users can download `ScreenRuler_Pro_v2.0.0.exe` directly from the release page.

---

**Questions or Issues?**
- Check the [CONTRIBUTING.md](CONTRIBUTING.md) guide
- Review [RELEASE_NOTES.md](RELEASE_NOTES.md) for process details
- Open an issue on GitHub for support
