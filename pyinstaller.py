import PyInstaller.__main__
from pathlib import Path

HERE = Path(__name__).parent.absolute()
path_to_main = str(HERE / "timetable/app.py")

def install():
    PyInstaller.__main__.run([
        path_to_main,
        '--onefile',
        '--add-data=timetable/TimeTable.py:.',
        '--add-data=timetable/solver_helper.py:.',
        '--add-data=timetable/static:static',
        '--add-data=timetable/templates:templates',
        '--add-data=timetable/models:models',
        '--add-data=timetable/outputs:outputs',
    ])
