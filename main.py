import os
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / 'AI' / 'AI' / 'main.py'

if not TARGET.exists():
    raise SystemExit(f'Entry point not found: {TARGET}')

os.chdir(ROOT)
runpy.run_path(str(TARGET), run_name='__main__')
