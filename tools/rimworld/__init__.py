"""AI RimWorld runner version comes from the project VERSION file."""
from pathlib import Path

__version__ = (Path(__file__).resolve().parents[2] / "VERSION").read_text().strip()
