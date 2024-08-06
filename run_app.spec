# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['/home/kali/Desktop/TimeTableSchool/timetable/run_app.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/kali/Desktop/TimeTableSchool/timetable/TimeTable.py', '.'), ('/home/kali/Desktop/TimeTableSchool/timetable/solver_helper.py', '.'), ('/home/kali/Desktop/TimeTableSchool/timetable/static', 'static'), ('/home/kali/Desktop/TimeTableSchool/timetable/templates', 'templates'), ('/home/kali/Desktop/TimeTableSchool/timetable/models', 'models'), ('/home/kali/Desktop/TimeTableSchool/timetable/outputs', 'outputs')],
    hiddenimports=['solver_helper', 'models', 'ortools.sat.python.cp_model'],
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
    name='run_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
