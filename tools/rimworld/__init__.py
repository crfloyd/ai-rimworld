"""AI RimWorld runner version comes from the project VERSION file."""
from pathlib import Path
import sys

if sys.version_info < (3, 10):
    raise RuntimeError("Python 3.10+ required for cross-process monotonic clocks; run from this repository with pyenv exec python (see .python-version).")

__version__ = (Path(__file__).resolve().parents[2] / "VERSION").read_text().strip()
