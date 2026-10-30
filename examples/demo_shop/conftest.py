"""Make the demo package importable no matter which cwd pytest runs from."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
