# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MTR DUAT FastAPI Backend.

Usage:
    pyinstaller backend.spec

Output:
    backend_dist/backend/backend.exe
"""

import sys
from pathlib import Path

block_cipher = None

# Project root directory
ROOT = Path(SPECPATH)

# Collect data files: analysis/, parsers/, config.py, utils/, routers/
datas = [
    (str(ROOT / 'analysis'), 'analysis'),
    (str(ROOT / 'parsers'), 'parsers'),
    (str(ROOT / 'utils'), 'utils'),
    (str(ROOT / 'config.py'), '.'),
    (str(ROOT / 'backend' / 'services.py'), '.'),
    (str(ROOT / 'backend' / 'routers'), 'routers'),
]

# Hidden imports required by uvicorn and fastapi
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'multipart',
    'multipart.multipart',
    'email.mime.multipart',
    'analysis',
    'analysis.dashboard',
    'analysis.lag_analysis',
    'analysis.performance',
    'analysis.scurve',
    'analysis.manpower',
    'parsers',
    'parsers.docx_parser',
    'parsers.manpower_parser',
    'config',
    'utils',
    'utils.excel_export',
    'routers',
    'routers.config',
    'routers.parse',
    'routers.dashboard',
    'routers.lag',
    'routers.performance',
    'routers.scurve',
    'routers.export',
    'routers.keyword',
    'routers.manpower',
    'services',
    'backend.services',
    'backend.routers',
    'backend.routers.config',
    'backend.routers.parse',
    'backend.routers.dashboard',
    'backend.routers.lag',
    'backend.routers.performance',
    'backend.routers.scurve',
    'backend.routers.export',
    'backend.routers.keyword',
    'backend.routers.manpower',
]

# Modules to exclude (reduce bundle size)
excludes = [
    'tkinter',
    '_tkinter',
    'xmlrpc',
    'pydoc',
    'doctest',
    'lib2to3',
    'ensurepip',
    'idlelib',
    'turtle',
    'turtledemo',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.backends.backend_tk',
    'matplotlib.backends.backend_qt5agg',
    'matplotlib.backends.backend_qt5',
    'matplotlib.backends.backend_gtk3agg',
    'matplotlib.backends.backend_gtk3',
    'matplotlib.backends.backend_wx',
    'matplotlib.backends.backend_wxagg',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'wx',
    'gi',
]

a = Analysis(
    [str(ROOT / 'backend' / 'main.py')],
    pathex=[str(ROOT), str(ROOT / 'backend')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(ROOT / 'scripts' / 'pyi_rth_duat.py')],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='backend',
)
