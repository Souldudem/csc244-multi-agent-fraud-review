"""Run the full standard-library suite and save a faithful evidence log."""
from pathlib import Path
import subprocess
import sys
import platform
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
output=ROOT/'.reports'/'tests.txt'
output.parent.mkdir(exist_ok=True)
command=[sys.executable, '-m', 'unittest', 'discover', '-p', 'test_*.py', '-v']
result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace')
header=(f'UTC: {datetime.now(timezone.utc).isoformat(timespec="seconds")}\n'
        f'Python: {sys.version.split()[0]}\nOS: {platform.platform()}\n'
        f'Command: python -m unittest discover -p test_*.py -v\n\n')
text=header+result.stdout+result.stderr+f'\nExit code: {result.returncode}\n'
output.write_text(text,encoding='utf-8')
print(text, end='')
raise SystemExit(result.returncode)
