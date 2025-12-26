# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ScreenRuler_pro.py'],
    pathex=[],
    binaries=[],
    datas=[('Icon.ico', '.'), ('LICENSE', '.')],  # Include Icon.ico and LICENSE in the bundle
    hiddenimports=['PIL', 'PIL._tkinter_finder', 'pystray', 'pystray._win32'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ScreenRuler_Pro_v1.0.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Icon.ico',  # Use Icon.ico as the .exe icon
)
