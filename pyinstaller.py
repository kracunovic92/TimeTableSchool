import PyInstaller.__main__
from pathlib import Path

HERE = Path(__name__).parent.absolute()
path_to_main = str(HERE / "timetable/run_app.py")

def install():
    PyInstaller.__main__.run([
        path_to_main,
        '--onefile',
        f'--add-data={HERE}/timetable/TimeTable.py:.',
        f'--add-data={HERE}/timetable/solver_helper.py:.',
        f'--add-data={HERE}/timetable/static:static',
        f'--add-data={HERE}/timetable/templates:templates',
        f'--add-data={HERE}/timetable/models:models',
        f'--add-data={HERE}/timetable/outputs:outputs',
        '--hidden-import=solver_helper',
        '--hidden-import=models',
    ])

if __name__ == "__main__":
    install()