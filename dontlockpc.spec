# PyInstaller build spec for "Don't Lock My PC".
#
# Build a standalone, windowed (no-console) executable:
#
#     pip install pyinstaller
#     pyinstaller dontlockpc.spec
#
# The result is placed in ./dist:
#   * Windows -> dist/DontLockMyPC.exe
#   * macOS   -> dist/DontLockMyPC.app
#
# Run PyInstaller on the target OS you want to build for (it does not
# cross-compile).

import sys

block_cipher = None

hidden_imports = ["PIL._tkinter_finder"]
if sys.platform.startswith("win"):
    hidden_imports.append("pystray._win32")
elif sys.platform == "darwin":
    hidden_imports.append("pystray._darwin")

a = Analysis(
    ["src/dontlockpc/__main__.py"],
    pathex=["src"],
    binaries=[],
    datas=[],
    hiddenimports=hidden_imports,
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
    name="DontLockMyPC",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Build a proper .app bundle on macOS.
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="DontLockMyPC.app",
        icon=None,
        bundle_identifier="com.dontlockpc.app",
        info_plist={
            "NSHighResolutionCapable": True,
            "LSUIElement": False,
        },
    )
