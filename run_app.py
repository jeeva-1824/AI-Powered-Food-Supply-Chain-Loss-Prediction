import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(ROOT, 'AI', 'AI', 'main.py')
VENV_PYTHON = os.path.join(ROOT, '.venv', 'Scripts', 'python.exe')

if not os.path.exists(VENV_PYTHON):
    raise SystemExit('Virtual environment not found at ' + VENV_PYTHON)

os.chdir(ROOT)
subprocess.call([VENV_PYTHON, MAIN])
