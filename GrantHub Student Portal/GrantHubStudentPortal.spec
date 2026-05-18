# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['portal.management.commands.seed_demo']
hiddenimports += collect_submodules('portal.migrations')
hiddenimports += collect_submodules('django.contrib.admin.migrations')
hiddenimports += collect_submodules('django.contrib.auth.migrations')
hiddenimports += collect_submodules('django.contrib.contenttypes.migrations')
hiddenimports += collect_submodules('django.contrib.sessions.migrations')


a = Analysis(
    ['run_granthub.py'],
    pathex=[],
    binaries=[],
    datas=[('portal/templates', 'portal/templates'), ('portal/static', 'portal/static'), ('db.sqlite3', '.')],
    hiddenimports=hiddenimports,
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
    name='GrantHubStudentPortal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='GrantHubStudentPortal',
)
