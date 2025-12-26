## Release Notes

### How to Create a Release

1. Update version number in:
   - `ScreenRuler_pro.py` (line ~906: version_label)
   - `ProRuler.spec` (name field)
   - `README.md`
   - `CHANGELOG.md`

2. Build the executable:
   ```bash
   pyinstaller --clean ProRuler.spec
   ```

3. Test the executable thoroughly

4. Create a release on GitHub:
   - Go to Releases → Draft a new release
   - Tag: `v1.0.0`
   - Title: `ScreenRuler Pro v1.0.0`
   - Attach: `ScreenRuler_Pro_v1.0.0.exe` from dist folder
   - Include: `README.txt` (user guide)
   - Copy changelog from `CHANGELOG.md`

5. Recommended release assets:
   - `ScreenRuler_Pro_v1.0.0.exe` (main executable)
   - `README.txt` (usage instructions for end users)
   - Source code (automatically included by GitHub)

### Release Checklist

- [ ] Version numbers updated
- [ ] Executable built and tested
- [ ] All features working
- [ ] Keyboard shortcuts tested
- [ ] Multi-monitor support verified
- [ ] System tray icon displays correctly
- [ ] About dialog scrolls properly
- [ ] Settings persist across sessions
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] LICENSE file included
- [ ] Icon.ico included in release assets
