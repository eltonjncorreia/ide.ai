# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ide-ai
Generates a single executable (onefile mode) for Linux and Windows
"""

a = Analysis(
    ['src/ide_ai/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ide_ai/app.tcss', 'ide_ai'),
    ],
    hiddenimports=[
        'textual',
        'textual.widgets',
        'textual.containers',
        'rich',
        'rich.console',
        'rich.markdown',
        'rich.syntax',
        'asyncio',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ide-ai',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console (needed for TUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
