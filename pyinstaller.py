import PyInstaller.__main__
from pathlib import Path
import shutil
import os

HERE = Path(__name__).parent.absolute()
path_to_main = str(HERE / "timetable/run_app.py")

def install():

    cleanup = True
    if cleanup:
        build_dir = HERE/'build'
        dist_dir = HERE/'dist'
        spec_file = HERE/f'{path_to_main}.spec'

        for path in [build_dir,dist_dir,spec_file]:
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        print("Cleanup complete")

        
    PyInstaller.__main__.run([
        path_to_main,
        '--onedir',
        f'--add-data=timetable/TimeTable.py{os.pathsep}.',
        f'--add-data=timetable/solver_helper.py{os.pathsep}.',
        f'--add-data=timetable/static/*{os.pathsep}static',
        f'--add-data=timetable/templates/*{os.pathsep}templates',
        f'--add-data=timetable/models{os.pathsep}models',
        f'--add-data=timetable/outputs{os.pathsep}.',
        f'--add-data=timetable/app.py{os.pathsep}.',
        '--hidden-import=app',
        '--hidden-import=solver_helper',
        '--hidden-import=models',
        '--hidden-import=numpy',
        '--hidden-import=ortools.sat.python.cp_model',
    ])

if __name__ == "__main__":
    install()