"""Auto-import all importer modules to trigger registration."""

import importlib
from pathlib import Path

_package_dir = Path(__file__).parent
for _file in _package_dir.glob("*.py"):
    if _file.name.startswith("_"):
        continue
    importlib.import_module(f".{_file.stem}", __package__)
