# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/zowya/CitoCounter_Proto/qt_app/main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/zowya/CitoCounter_Proto/models/cito95/best_model_weights.pt', 'models/cito95')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CitoCounter-Qt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CitoCounter-Qt',
)
